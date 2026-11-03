"""T015 instrumentation checks on mock answers; not measurements of V4 quality."""
from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import Mock, patch

import main
from core.tool_call_validation import parse_recipe_tool_arguments
from evals.run_llm_eval import load_cases
from evals.run_routing_eval import evaluate_case
from evals.run_routing_experiment import ROOT, write_json
from evals.run_routing_pilot import (CASES, campaign_schedule, execute, prepare, summarize_t015)
from test_routing_t014 import correct_response
from test_separated_routing_eval import response


class RoutingT015Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(ROOT / CASES)
        cls.rows = []
        for attempt, variant, mode in campaign_schedule('t015'):
            for case in cls.cases:
                client = Mock()
                client.chat.completions.create.return_value = correct_response(case)
                cls.rows.append(dict(evaluate_case(case, mode, client),
                                     variant=variant, mode=mode, attempt=attempt))

    def failing(self, rows, variant, mode, ids, attempts=(1, 2, 3)):
        rows = deepcopy(rows)
        for row in rows:
            if row['variant'] == variant and row['mode'] == mode and row['id'] in ids and row['attempt'] in attempts:
                row.update(passed=False, failure_stage='decision')
        return rows

    def candidate_rows(self):
        rows = self.rows
        for mode in ('raw', 'application'):
            rows = self.failing(rows, 'V0', mode, ('intent_003', 'intent_013', 'intent_031', 'intent_051'))
        return rows

    def test_v4_preserves_v3_and_examples_without_literal_test_queries(self):
        v3 = (ROOT / 'evals/routing_prompts/V3.txt').read_text(encoding='utf-8')
        v4 = (ROOT / 'evals/routing_prompts/V4.txt').read_text(encoding='utf-8')
        added = [line for line in v4.splitlines(keepends=True) if line.startswith('OBSŁUGIWANE PREFERENCJE:')]
        self.assertEqual(len(added), 1)
        self.assertEqual(v4.replace(added[0], '', 1), v3)
        pattern = r'Zapytanie: ([^\n]+)\nNarzędzie: get_recommendations\nArgumenty: ([^\n]+)'
        self.assertEqual(re.findall(pattern, v4), re.findall(pattern, v3))
        self.assertEqual(len(re.findall(pattern, v4)), 5)
        for _, raw in re.findall(pattern, v4):
            parse_recipe_tool_arguments(raw)
        for case in self.cases:
            if case['id'] in ('intent_004', 'intent_010', 'intent_032'):
                self.assertNotIn(case['user_message'], added[0])
        self.assertLess(v4.index('PRIORYTET ZAKRESU:'), v4.index('OBSŁUGIWANE PREFERENCJE:'))
        self.assertEqual(main.build_system_prompt('Winiary'),
                         (ROOT / 'evals/routing_prompts/V0.txt').read_text(encoding='utf-8'))

    def test_dry_run_freezes_profile_scope_rule_and_provenance_without_api(self):
        with tempfile.TemporaryDirectory() as tmp, patch('evals.run_routing_pilot.OpenAI') as api:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory, 't015')
            self.assertEqual(manifest['selection_rule'], 'T015-v1')
            self.assertEqual(manifest['cases'], self.cases)
            self.assertEqual(manifest['planned_calls'], 216)
            self.assertEqual(manifest['planned_evaluations'], 240)
            self.assertEqual(set(manifest['prompt_hashes']), {'V0', 'V4'})
            self.assertIn('evals/routing_prompts/V3.txt', manifest['files'])
            self.assertEqual(manifest['actual_calls'], 0)
            self.assertLess(manifest['estimated_max_output_cost_usd'], .50)
            self.assertEqual(manifest['schedule'][4], (2, 'V4', 'raw'))
            with self.assertRaises(FileExistsError):
                prepare(directory, 't015')
            api.assert_not_called()

    def test_full_mock_campaign_uses_exact_prompts_and_keeps_active_application(self):
        original = main.build_system_prompt
        lookup = {case['user_message']: case for case in self.cases}
        seen = []
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory, 't015')
            def reply(**kwargs):
                seen.append(kwargs)
                case = lookup[kwargs['messages'][1]['content']]
                if kwargs['messages'][0]['content'] == manifest['prompts']['V0'] and case['id'] in (
                        'intent_003', 'intent_013', 'intent_031', 'intent_051'):
                    value = response(count=0)
                    value.model = 'test-model'
                    value.choices[0].finish_reason = 'stop'
                    return value
                return correct_response(case)
            client = Mock()
            client.chat.completions.create.side_effect = reply
            with patch('evals.run_routing_pilot.OpenAI', return_value=client) as constructor:
                result = execute(directory)
            self.assertEqual(result['candidate'], 'V4')
            self.assertTrue(all(result['conditions'].values()))
            self.assertEqual(len(seen), 216)
            offset = 0
            for _, variant, mode in manifest['schedule']:
                count = 20 if mode == 'raw' else 16
                batch = seen[offset:offset + count]
                self.assertTrue(all(k['messages'][0]['content'] == manifest['prompts'][variant] for k in batch))
                self.assertTrue(all(k['max_completion_tokens'] == 512 for k in batch))
                offset += count
            self.assertEqual(constructor.call_args.kwargs['max_retries'], 0)
            self.assertEqual(constructor.call_args.kwargs['base_url'], 'https://api.openai.com/v1')
            self.assertIs(main.build_system_prompt, original)
            self.assertFalse(result['active_prompt_changed'])
            self.assertEqual(len(json.loads((directory / 'results.json').read_text(encoding='utf-8'))['results']), 240)
            with self.assertRaises(ValueError):
                execute(directory)

    def test_target_success_is_required_in_each_mode_and_ties_keep_v0(self):
        self.assertEqual(summarize_t015(self.rows)['candidate'], 'V0')
        self.assertEqual(summarize_t015(self.candidate_rows())['candidate'], 'V4')
        for mode in ('raw', 'application'):
            for cid in ('intent_004', 'intent_010', 'intent_032'):
                with self.subTest(mode=mode, case=cid):
                    rows = self.failing(self.candidate_rows(), 'V4', mode, (cid,), (1,))
                    result = summarize_t015(rows)
                    self.assertFalse(result['conditions']['targets_all'])
                    self.assertEqual(result['candidate'], 'V0')

    def test_single_case_loss_and_loss_of_already_unstable_case_are_rejected(self):
        rows = self.failing(self.candidate_rows(), 'V4', 'application', ('intent_007',), (1,))
        result = summarize_t015(rows)
        self.assertEqual(result['case_regressions']['application'],
                         [dict(id='intent_007', baseline_passed=3, candidate_passed=2)])
        self.assertEqual(result['candidate'], 'V0')
        rows = self.failing(self.candidate_rows(), 'V0', 'raw', ('intent_007',), (1,))
        rows = self.failing(rows, 'V4', 'raw', ('intent_007',), (1, 2))
        result = summarize_t015(rows)
        self.assertEqual(result['case_regressions']['raw'],
                         [dict(id='intent_007', baseline_passed=2, candidate_passed=1)])
        self.assertEqual(result['candidate'], 'V0')

    def test_wrong_arguments_dispatched_to_backend_disqualify_despite_score_improvement(self):
        rows = self.candidate_rows()
        case = next(c for c in self.cases if c['id'] == 'intent_003')
        args = dict(case['expected'], nutrition_goal='standard')
        args.pop('time_max')
        client = Mock()
        value = response(json.dumps(args))
        value.model, value.choices[0].finish_reason = 'test-model', 'stop'
        client.chat.completions.create.return_value = value
        bad = dict(evaluate_case(case, 'application', client), variant='V4', mode='application', attempt=1)
        self.assertEqual(bad['backend_calls'], 1)
        self.assertFalse(bad['semantics_correct'])
        rows = [bad if (r['variant'], r['mode'], r['attempt'], r['id']) == ('V4', 'application', 1, case['id'])
                else r for r in rows]
        result = summarize_t015(rows)
        self.assertEqual(result['candidate'], 'V0')
        self.assertFalse(result['conditions']['no_semantic_dispatch'])
        self.assertTrue(all(v for k, v in result['conditions'].items() if k != 'no_semantic_dispatch'))
        self.assertEqual(result['semantic_dispatch_errors']['V4'][0]['id'], 'intent_003')

    def test_exact_supported_and_stability_thresholds(self):
        rows = self.candidate_rows()
        for cid in ('intent_003', 'intent_013'):
            rows = self.failing(rows, 'V4', 'application', (cid,), (1, 2))
        result = summarize_t015(rows)
        self.assertEqual(result['variants']['V4']['application']['supported']['passed'], 38)
        self.assertTrue(result['conditions']['supported_accuracy'])
        rows = self.failing(rows, 'V4', 'application', ('intent_031',), (1,))
        result = summarize_t015(rows)
        self.assertEqual(result['variants']['V4']['application']['supported']['passed'], 37)
        self.assertFalse(result['conditions']['supported_accuracy'])
        self.assertTrue(result['conditions']['application_accuracy'])
        self.assertTrue(result['conditions']['application_stability'])  # 17/20 exactly.
        rows = self.failing(rows, 'V4', 'application', ('intent_051',), (1,))
        self.assertFalse(summarize_t015(rows)['conditions']['application_stability'])
        rows = self.failing(rows, 'V4', 'application', ('intent_051',), (2,))
        self.assertFalse(summarize_t015(rows)['conditions']['application_accuracy'])

    def test_raw_error_is_not_hidden_by_application_preflight(self):
        rows = self.failing(self.candidate_rows(), 'V4', 'raw', ('routing_004',), (1,))
        result = summarize_t015(rows)
        self.assertFalse(result['conditions']['no_tool_all'])
        self.assertEqual(result['candidate'], 'V0')
        self.assertIn(dict(variant='V4', attempt=1, id='routing_004'),
                      result['raw_failures_blocked_in_application'])

    def test_incomplete_relabelled_or_changed_message_is_rejected(self):
        duplicate = deepcopy(self.rows)
        duplicate[-1] = deepcopy(duplicate[0])
        relabelled = deepcopy(self.rows)
        relabelled[0]['expected_action'] = 'no_tool'
        message = deepcopy(self.rows)
        message[0]['user_message'] = 'changed'
        for rows in (self.rows[:-1], duplicate, relabelled, message):
            with self.assertRaises(ValueError):
                summarize_t015(rows)

    def test_api_error_truncation_and_mixed_models_prevent_qualification(self):
        for field, value in (('failure_stage', 'api'), ('finish_reason', 'length'), ('response_model', 'different')):
            rows = self.candidate_rows()
            rows[0][field] = value
            result = summarize_t015(rows)
            self.assertFalse(result['valid_comparison'])
            self.assertEqual(result['candidate'], 'V0')

    def test_changed_selection_rule_is_rejected_before_client_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory, 't015')
            manifest['selection_rule'] = 'relaxed'
            write_json(directory / 'manifest.json', manifest)
            with patch('evals.run_routing_pilot.OpenAI') as api:
                with self.assertRaises(ValueError):
                    execute(directory)
                api.assert_not_called()
