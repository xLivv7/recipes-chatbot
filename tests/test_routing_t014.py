"""Offline checks of the T014 protocol; mocked results do not evaluate V3 quality."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import main
from evals.run_llm_eval import load_cases
from evals.run_routing_eval import evaluate_case
from evals.run_routing_experiment import ROOT, write_json
from evals.run_routing_pilot import (CASES, BudgetedClient, campaign_schedule,
                                    execute, prepare, request, summarize_t014)
from test_separated_routing_eval import response


def correct_response(case):
    if case.get('expected_action', 'tool') == 'no_tool':
        value = response(count=0)
    else:
        args = dict(case['expected'])
        if args.get('time_max') is None:
            del args['time_max']
        value = response(json.dumps(args))
    value.model = 'test-model'
    value.choices[0].finish_reason = 'stop'
    return value


class RoutingT014Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(ROOT / CASES)
        cls.supported = [c['id'] for c in cls.cases if c.get('expected_action', 'tool') == 'tool']
        cls.rows = []
        for attempt, variant, mode in campaign_schedule('t014'):
            for case in cls.cases:
                client = Mock()
                client.chat.completions.create.return_value = correct_response(case)
                cls.rows.append(dict(evaluate_case(case, mode, client),
                                     variant=variant, mode=mode, attempt=attempt))

    def failed_rows(self, variant, mode, ids, attempts=(1, 2, 3), rows=None):
        rows = deepcopy(self.rows if rows is None else rows)
        for row in rows:
            if row['variant'] == variant and row['mode'] == mode and row['id'] in ids and row['attempt'] in attempts:
                row.update(passed=False, failure_stage='decision')
        return rows

    def candidate_rows(self):
        return self.failed_rows('V0', 'raw', self.supported[:1])

    def test_v3_adds_only_one_priority_paragraph_and_preserves_examples(self):
        v2 = (ROOT / 'evals/routing_prompts/V2.txt').read_text(encoding='utf-8')
        v3 = (ROOT / 'evals/routing_prompts/V3.txt').read_text(encoding='utf-8')
        additions = [line for line in v3.splitlines(keepends=True) if line.startswith('PRIORYTET ZAKRESU:')]
        self.assertEqual(len(additions), 1)
        self.assertEqual(v3.replace(additions[0], '', 1), v2)
        self.assertEqual(v3.count('Zapytanie:'), 5)
        self.assertIn('Ta decyzja ma pierwszeństwo', additions[0])
        self.assertEqual(main.build_system_prompt('Winiary'),
                         (ROOT / 'evals/routing_prompts/V0.txt').read_text(encoding='utf-8'))

    def test_prepare_freezes_240_scores_216_calls_without_api(self):
        with tempfile.TemporaryDirectory() as tmp, patch('evals.run_routing_pilot.OpenAI') as api:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory, 't014')
            self.assertEqual(manifest['planned_evaluations'], 240)
            self.assertEqual(manifest['planned_calls'], 216)
            self.assertEqual(manifest['actual_calls'], 0)
            self.assertLess(manifest['estimated_max_output_cost_usd'], .50)
            self.assertEqual(set(manifest['prompt_hashes']), {'V0', 'V3'})
            self.assertIn('evals/routing_prompts/V2.txt', manifest['files'])
            self.assertEqual(manifest['schedule'][0], (1, 'V0', 'raw'))
            self.assertEqual(manifest['schedule'][4], (2, 'V3', 'raw'))
            self.assertEqual(len(manifest['schedule']), 12)
            with self.assertRaises(FileExistsError):
                prepare(directory, 't014')
            api.assert_not_called()

    def test_mock_campaign_sends_frozen_prompts_in_both_modes_and_restores_application(self):
        active = main.build_system_prompt('Winiary')
        lookup = {case['user_message']: case for case in self.cases}
        seen = []
        def reply(**kwargs):
            seen.append(kwargs)
            return correct_response(lookup[kwargs['messages'][1]['content']])
        client = Mock()
        client.chat.completions.create.side_effect = reply
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory, 't014')
            with patch('evals.run_routing_pilot.OpenAI', return_value=client) as constructor:
                result = execute(directory)
            self.assertEqual(len(seen), 216)
            self.assertEqual(result['candidate'], 'V0')  # A tie cannot qualify V3.
            saved = json.loads((directory / 'results.json').read_text(encoding='utf-8'))
            self.assertEqual(len(saved['results']), 240)
            self.assertTrue(saved['complete'])
            offset = 0
            for _, variant, mode in manifest['schedule']:
                count = 20 if mode == 'raw' else 16
                batch = seen[offset:offset + count]
                self.assertTrue(all(k['messages'][0]['content'] == manifest['prompts'][variant] for k in batch))
                self.assertTrue(all(k['max_completion_tokens'] == 512 for k in batch))
                offset += count
            for variant in ('V0', 'V3'):
                self.assertEqual(result['variants'][variant]['application']['correct_guards'], 12)
                self.assertEqual(result['variants'][variant]['raw']['api_calls'], 60)
                self.assertEqual(result['variants'][variant]['application']['api_calls'], 48)
            self.assertEqual(constructor.call_args.kwargs['max_retries'], 0)
            self.assertEqual(constructor.call_args.kwargs['base_url'], 'https://api.openai.com/v1')
            self.assertEqual(main.build_system_prompt('Winiary'), active)
            with self.assertRaises(ValueError):
                execute(directory)

    def test_configuration_or_frozen_prompt_changes_stop_before_client_creation(self):
        for change in ('configuration', 'prompt'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp) / 'campaign'
                manifest = prepare(directory, 't014')
                if change == 'configuration':
                    manifest['configuration']['max_retries'] = 1
                    write_json(directory / 'manifest.json', manifest)
                else:
                    (directory / 'V3.txt').write_text('modified', encoding='utf-8')
                with patch('evals.run_routing_pilot.OpenAI') as api:
                    with self.assertRaises(ValueError):
                        execute(directory)
                    api.assert_not_called()

    def test_t014_call_cap_stops_before_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = Mock()
            manifest = dict(profile='t014', actual_calls=215, reserved_usd=0)
            bounded = BudgetedClient(client, manifest, Path(tmp))
            bounded.create(**request('prompt', dict(user_message='query')))
            with self.assertRaises(RuntimeError):
                bounded.create(**request('prompt', dict(user_message='query')))
            self.assertEqual(client.chat.completions.create.call_count, 1)

    def test_candidate_requires_improvement_and_no_tool_boundary_in_both_modes(self):
        self.assertEqual(summarize_t014(self.rows)['candidate'], 'V0')
        self.assertEqual(summarize_t014(self.candidate_rows())['candidate'], 'V3')
        for mode in ('raw', 'application'):
            rows = self.failed_rows('V3', mode, ['routing_004'], (1,), self.candidate_rows())
            self.assertEqual(summarize_t014(rows)['candidate'], 'V0')

    def test_application_loss_stability_loss_and_persistent_regression_disqualify(self):
        app_loss = self.failed_rows('V3', 'application', self.supported[:1], (1,), self.candidate_rows())
        self.assertEqual(summarize_t014(app_loss)['candidate'], 'V0')
        # V3 has more correct scores (56 > 51), but fewer stable cases (16 < 17).
        stable_loss = self.failed_rows('V0', 'raw', self.supported[:3])
        stable_loss = self.failed_rows('V3', 'raw', self.supported[:4], (1,), stable_loss)
        self.assertEqual(summarize_t014(stable_loss)['candidate'], 'V0')
        regression = self.failed_rows('V0', 'raw', self.supported[:2])
        regression = self.failed_rows('V3', 'raw', self.supported[2:3], rows=regression)
        result = summarize_t014(regression)
        self.assertEqual(result['candidate'], 'V0')
        self.assertEqual(result['new_persistent_regressions']['raw'], self.supported[2:3])

    def test_raw_failure_blocked_by_application_stays_a_model_failure(self):
        rows = self.failed_rows('V3', 'raw', ['routing_004'], (1,), self.candidate_rows())
        result = summarize_t014(rows)
        self.assertIn(dict(variant='V3', attempt=1, id='routing_004'),
                      result['raw_failures_blocked_in_application'])
        self.assertEqual(result['variants']['V3']['raw']['no_tool']['passed'], 17)
        self.assertEqual(result['variants']['V3']['application']['no_tool']['passed'], 18)
        self.assertEqual(result['candidate'], 'V0')

    def test_missing_duplicate_or_relabelled_results_are_rejected(self):
        duplicate = deepcopy(self.rows)
        duplicate[-1] = deepcopy(duplicate[0])
        relabelled = deepcopy(self.rows)
        relabelled[0]['expected_action'] = 'no_tool'
        for rows in (self.rows[:-1], duplicate, relabelled):
            with self.assertRaises(ValueError):
                summarize_t014(rows)

    def test_api_error_truncation_or_mixed_models_invalidates_comparison(self):
        for field, value in (('failure_stage', 'api'), ('finish_reason', 'length'),
                             ('response_model', 'different-model'), ('response_model', None)):
            rows = self.candidate_rows()
            rows[0][field] = value
            result = summarize_t014(rows)
            self.assertFalse(result['valid_comparison'])
            self.assertEqual(result['candidate'], 'V0')
