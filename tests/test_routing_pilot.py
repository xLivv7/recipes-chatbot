from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from evals.run_routing_pilot import prepare, execute, BudgetedClient, cost_reservation, request
from evals.run_routing_experiment import ROOT, DATASETS, write_json
from evals.run_llm_eval import load_cases
from test_separated_routing_eval import response


class RoutingPilotTests(unittest.TestCase):
    def test_frozen_subset_matches_original_labels_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp, patch('evals.run_routing_pilot.OpenAI') as api:
            m = prepare(Path(tmp) / 'pilot')
            self.assertEqual(len(m['cases']), 20)
            originals = {c['id']:c for name in DATASETS for c in load_cases(ROOT / name)}
            self.assertTrue(all(c == originals[c['id']] for c in m['cases']))
            self.assertEqual(m['planned_calls'], 120)
            self.assertLess(m['estimated_max_output_cost_usd'], .50)
            api.assert_not_called()

    def test_budget_reserves_before_request_caps_output_and_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            m = dict(actual_calls=0, reserved_usd=0)
            client = Mock()
            bounded = BudgetedClient(client, m, directory)
            kwargs = request('prompt', dict(user_message='query'))
            kwargs.pop('max_completion_tokens')
            bounded.create(**kwargs)
            self.assertEqual(client.chat.completions.create.call_args.kwargs['max_completion_tokens'], 512)
            self.assertEqual(json.loads((directory/'manifest.json').read_text())['actual_calls'], 1)
            m['reserved_usd'] = .50
            with self.assertRaises(RuntimeError): bounded.create(**kwargs)
            self.assertEqual(client.chat.completions.create.call_count, 1)

    def test_complete_mock_campaign_alternates_and_does_not_change_application(self):
        import main
        active = main.build_system_prompt('Winiary')
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'pilot'
            m = prepare(directory)
            # Construct correct mocked observations from each declared expected case.
            expected_calls = [c for _,_ in m['schedule'] for c in m['cases']]
            seen = []
            def reply(**kwargs):
                c = expected_calls[len(seen)]
                seen.append(kwargs)
                if c.get('expected_action', 'tool') == 'no_tool':
                    value = response(count=0)
                else:
                    args = dict(c['expected'])
                    if args.get('time_max') is None: del args['time_max']
                    value = response(json.dumps(args))
                value.model = 'test-model'
                value.choices[0].finish_reason = 'stop'
                return value
            client = Mock()
            client.chat.completions.create.side_effect = reply
            with patch('evals.run_routing_pilot.OpenAI', return_value=client) as constructor:
                result = execute(directory)
            self.assertEqual(len(seen), 120)
            self.assertEqual(result['candidate'], 'V0')
            self.assertEqual(result['variants']['V2']['no_tool'], dict(passed=18,total=18))
            self.assertEqual([seen[i]['messages'][0]['content'] for i in (0,20,40,60,80,100)],
                             [m['prompts'][v] for _,v in m['schedule']])
            self.assertEqual(constructor.call_args.kwargs['max_retries'], 0)
            self.assertEqual(constructor.call_args.kwargs['base_url'], 'https://api.openai.com/v1')
            self.assertEqual(main.build_system_prompt('Winiary'), active)
            with self.assertRaises(ValueError): execute(directory)

    def test_truncation_is_failure_and_changed_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'pilot'
            m = prepare(directory)
            m['cases'][0]['user_message'] = 'tampered'
            write_json(directory/'manifest.json', m)
            with patch('evals.run_routing_pilot.OpenAI') as api:
                with self.assertRaises(ValueError): execute(directory)
                api.assert_not_called()
            m['cases'] = load_cases(ROOT/'evals/routing_pilot_cases.json')
            write_json(directory/'manifest.json', m)
            row = dict(id=m['cases'][0]['id'], failure_stage=None, passed=True, finish_reason='length')
            def stop_after_first(*args, **kwargs):
                if (directory/'results.json').exists(): raise RuntimeError('test stop')
                return deepcopy(row)
            with patch('evals.run_routing_pilot.OpenAI'), patch('evals.run_routing_pilot.evaluate_case', side_effect=stop_after_first):
                with self.assertRaises(RuntimeError): execute(directory)
            saved = json.loads((directory/'results.json').read_text())['results'][0]
            self.assertFalse(saved['passed'])
            self.assertEqual(saved['failure_stage'], 'completion_limit')
