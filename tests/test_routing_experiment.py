from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import Mock, patch

import main
from core.tool_call_validation import parse_recipe_tool_arguments
from evals.run_routing_eval import evaluate_case
from evals.run_routing_experiment import (ROOT, VARIANTS, prepare, execute, schedule,
    validate_frozen, aggregate, group_summary, load_development_cases, content_json_matches, write_json)
from test_separated_routing_eval import case, response, tool_args
from test_no_tool_diagnostics import no_tool_response


class RoutingExperimentTests(unittest.TestCase):
    def prompts(self):
        return {v: (ROOT / 'evals/routing_prompts' / (v + '.txt')).read_text(encoding='utf-8') for v in VARIANTS}

    def test_frozen_control_matches_active_and_example_semantics_are_preserved(self):
        prompts = self.prompts()
        self.assertEqual(prompts['V0'], main.build_system_prompt('Winiary'))
        pattern = r'Zapytanie: ([^\n]+)\n```json\n(.*?)\n```'
        examples = re.findall(pattern, prompts['V0'], flags=re.DOTALL)
        self.assertEqual(len(examples), 5)
        self.assertEqual(re.findall(pattern, prompts['V1'], flags=re.DOTALL), examples)
        v2 = re.findall(r'Zapytanie: ([^\n]+)\nNarzędzie: get_recommendations\nArgumenty: ([^\n]+)', prompts['V2'])
        self.assertEqual(examples, v2)
        for _, raw in v2:
            parse_recipe_tool_arguments(raw)
        self.assertNotIn('```', prompts['V2'])

    def test_selected_prompt_is_sent_in_both_modes_and_restored(self):
        original = main.build_system_prompt
        for variant, prompt in self.prompts().items():
            for mode in ('raw', 'application'):
                client = Mock()
                client.chat.completions.create.return_value = response()
                with self.subTest(variant=variant, mode=mode):
                    result = evaluate_case(case(), mode, client, system_prompt=prompt)
                    self.assertTrue(result['passed'])
                    kwargs = client.chat.completions.create.call_args.kwargs
                    self.assertEqual(kwargs['messages'][0]['content'], prompt)
                    self.assertFalse(kwargs['parallel_tool_calls'])
                    self.assertEqual(result['backend_calls'], 1 if mode == 'application' else 0)
                    self.assertIs(main.build_system_prompt, original)

    def test_wrong_channel_is_diagnosed_without_becoming_success(self):
        client = Mock()
        client.chat.completions.create.return_value = no_tool_response('```json\n' + json.dumps(tool_args()) + '\n```')
        row = evaluate_case(case(), 'application', client, system_prompt=self.prompts()['V2'])
        self.assertEqual(row['backend_calls'], 0)
        self.assertFalse(row['passed'])
        self.assertTrue(content_json_matches(row))

    def test_protocol_argument_errors_and_unsupported_cases_keep_their_meaning(self):
        for value, stage in [(response(count=2), 'protocol'), (response(name='unknown'), 'protocol'),
                             (response('{}'), 'arguments')]:
            client = Mock()
            client.chat.completions.create.return_value = value
            row = evaluate_case(case(), 'application', client, system_prompt=self.prompts()['V1'])
            self.assertEqual(row['failure_stage'], stage)
            self.assertEqual(row['backend_calls'], 0)
        for c in load_development_cases():
            if c['id'] not in ('guard_001', 'guard_005'):
                continue
            client = Mock()
            client.chat.completions.create.return_value = no_tool_response(None)
            row = evaluate_case(c, 'application', client, system_prompt=self.prompts()['V1'])
            self.assertEqual(row['passed'], c['id'] == 'guard_001')
            if c['id'] == 'guard_001':
                client.chat.completions.create.assert_not_called()
            else:
                client.chat.completions.create.assert_called_once()
                self.assertEqual(row['failure_stage'], 'decision')

    def test_dry_run_freezes_complete_plan_without_client(self):
        with tempfile.TemporaryDirectory() as tmp, patch('evals.run_routing_experiment.OpenAI') as api:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory)
            self.assertEqual(manifest['plan']['evaluations'], 1368)
            # A newly prepared plan after T024 releases guard_005/006.
            self.assertEqual(manifest['plan']['sdk_calls'], 1296)
            self.assertEqual(len(manifest['schedule']), 18)
            api.assert_not_called()
            loaded = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
            validate_frozen(directory, loaded)
            with self.assertRaises(FileExistsError):
                prepare(directory)
            (directory / 'V1.txt').write_text('changed', encoding='utf-8')
            with self.assertRaises(ValueError):
                validate_frozen(directory, loaded)

    def test_rotation_uses_global_rounds(self):
        self.assertEqual([v for r,v,m in schedule() if m == 'raw'],
                         ['V0','V1','V2','V1','V2','V0','V2','V0','V1'])

    def make_reports(self, directory, manifest):
        for round_no, variant, mode in manifest['schedule']:
            rows = []
            for c in manifest['cases']:
                action = c.get('expected_action', 'tool')
                rows.append(dict(id=c['id'], expected=c.get('expected'), expected_action=action,
                    passed=True, attempt=round_no, failure_stage=None, guard=None,
                    api_calls=1, backend_calls=int(mode == 'application' and action == 'tool'),
                    response_model='frozen-model', model_action=action, actual=c.get('expected'),
                    no_tool_content=None, field_results=dict.fromkeys(tool_args(), True),
                    decision_correct=True, model_decision_correct=True, protocol_valid=True,
                    arguments_valid=action == 'tool', semantics_correct=action == 'tool',
                    usage=dict(prompt_tokens=100, completion_tokens=10, total_tokens=110)))
                rows[-1]['field_results']['time_max'] = True
            write_json(directory / f'round{round_no}_{variant}_{mode}.json', dict(
                complete=True, round=round_no, variant=variant, mode=mode,
                prompt_sha256=manifest['prompt_hashes'][variant], results=rows))

    def test_aggregation_tie_break_and_rejects_missing_duplicate_or_wrong_round(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory)
            self.make_reports(directory, manifest)
            summary = aggregate(directory, manifest)
            self.assertEqual(summary['winner'], 'V0')
            self.assertEqual(summary['total_evaluations'], 1368)
            self.assertEqual(summary['variants']['V1']['application']['supported'], dict(passed=198, total=198))
            path = directory / 'round1_V0_raw.json'
            original = json.loads(path.read_text(encoding='utf-8'))
            for change in ('incomplete', 'missing', 'duplicate', 'round', 'labels'):
                report = deepcopy(original)
                if change == 'incomplete': report['complete'] = False
                elif change == 'missing': report['results'].pop()
                elif change == 'duplicate': report['results'][0] = report['results'][1]
                elif change == 'round': report['results'][0]['attempt'] = 2
                else: report['results'][0]['expected_action'] = 'no_tool'
                write_json(path, report)
                with self.subTest(change=change), self.assertRaises(ValueError):
                    aggregate(directory, manifest)

    def test_api_failure_stops_with_checkpoint_and_cannot_resume_selectively(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            prepare(directory)
            row = dict(id='intent_001', failure_stage='api', error='AuthenticationError', api_calls=1, attempt=1)
            with patch('evals.run_routing_experiment.OpenAI'), patch(
                    'evals.run_routing_experiment.evaluate_case', return_value=row):
                with self.assertRaises(RuntimeError): execute(directory)
            manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['status'], 'incomplete')
            checkpoint = json.loads((directory / 'round1_V0_raw.json').read_text(encoding='utf-8'))
            self.assertFalse(checkpoint['complete'])
            self.assertEqual(len(checkpoint['results']), 1)
            with self.assertRaises(ValueError): execute(directory)

    def test_selection_and_invalid_model_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            manifest = prepare(directory)
            self.make_reports(directory, manifest)
            for round_no, variant, mode in manifest['schedule']:
                if variant == 'V2' or mode == 'raw':
                    continue
                path = directory / f'round{round_no}_{variant}_{mode}.json'
                report = json.loads(path.read_text(encoding='utf-8'))
                report['results'][0].update(passed=False, failure_stage='decision')
                write_json(path, report)
            self.assertEqual(aggregate(directory, manifest)['winner'], 'V2')
            path = directory / 'round1_V2_raw.json'
            report = json.loads(path.read_text(encoding='utf-8'))
            report['results'][0]['response_model'] = 'different-model'
            write_json(path, report)
            result = aggregate(directory, manifest)
            self.assertFalse(result['valid_comparison'])
            self.assertIsNone(result['winner'])

    def test_changed_cases_or_configuration_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'campaign'
            prepare(directory)
            original = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
            for key in ('cases', 'configuration', 'schedule'):
                changed = deepcopy(original)
                if key == 'cases': changed[key][0]['user_message'] = 'changed'
                elif key == 'configuration': changed[key]['temperature'] = 1
                else: changed[key].reverse()
                with self.subTest(key=key), self.assertRaises(ValueError):
                    validate_frozen(directory, changed)
