from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from core.tool_call_validation import ToolArgumentsError
from evals.legacy_final_answer_prompt import build_legacy_final_answer_prompt
from evals.run_final_answer_eval import build_messages, load_cases as load_final, DEFAULT_CASES_PATH as FINAL_PATH
from evals.run_llm_eval import (extract_tool_args, score_intent_case, summarize,
                               load_cases, DEFAULT_ROUTING_CASES_PATH)
from evals.run_renderer_eval import run_eval, DEFAULT_CASES_PATH
from main import build_system_prompt


class CurrentEvaluationTests(unittest.TestCase):
    def test_current_prompt_assigns_presentation_to_application(self):
        prompt = build_system_prompt("Winiary")
        self.assertIn("Odpowiedź końcową tworzy aplikacja", prompt)
        self.assertNotIn("ZASADY FORMATOWANIA", prompt)
        self.assertNotEqual(prompt, build_legacy_final_answer_prompt("Winiary"))

    def test_historical_eval_uses_frozen_prompt(self):
        case = load_final(FINAL_PATH)[0]
        self.assertEqual(build_messages(case, "Winiary")[0]["content"],
                         build_legacy_final_answer_prompt("Winiary"))

    def test_intent_eval_matches_application_tool_choice_and_temperature(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(tool_calls=None))])
        self.assertIsNone(extract_tool_args(client, "gpt-4o-mini", "Zapytanie", "Winiary"))
        args = client.chat.completions.create.call_args.kwargs
        self.assertEqual(args["tool_choice"], "auto")
        self.assertEqual(args["temperature"], 0.1)
        self.assertEqual(args["messages"][0]["content"], build_system_prompt("Winiary"))

    def test_eval_rejects_invalid_model_arguments_before_scoring(self):
        client = Mock()
        call = SimpleNamespace(function=SimpleNamespace(name="get_recommendations", arguments='{}'))
        client.chat.completions.create.return_value = SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
        with self.assertRaises(ToolArgumentsError):
            extract_tool_args(client, "gpt-4o-mini", "Zapytanie", "Winiary")

    def test_no_tool_cases_have_separate_action_score_and_field_denominator(self):
        routing = load_cases(DEFAULT_ROUTING_CASES_PATH)
        self.assertEqual(len(routing), 6)
        result = score_intent_case(routing[0], None)
        self.assertTrue(result["passed"])
        self.assertFalse(score_intent_case(routing[0], {"diet": "none"})["passed"])
        summary = summarize([result])
        self.assertEqual(summary["action_accuracy"], 1)
        self.assertEqual(summary["field_accuracy"]["diet"]["total"], 0)

    def test_missing_tool_for_recipe_request_is_failure(self):
        result = score_intent_case({"expected": {}}, None)
        self.assertFalse(result["passed"])
        self.assertFalse(result["action_correct"])

    def test_renderer_dataset_passes_offline(self):
        report = run_eval(DEFAULT_CASES_PATH)
        self.assertEqual(report["api_calls"], 0)
        self.assertEqual(report["summary"], {"total": 6, "passed": 6, "failed": 0})
