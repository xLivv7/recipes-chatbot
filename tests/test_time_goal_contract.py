import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.llm_tools import RECIPE_TOOLS
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
from core.tool_call_validation import parse_recipe_tool_arguments
from evals.run_llm_eval import DEFAULT_CASES_PATH, load_cases, score_case
from main import build_system_prompt, chat_with_bot


FOCUSED_CASES_PATH = DEFAULT_CASES_PATH.with_name("time_goal_cases.json")


class TimeGoalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in load_cases(FOCUSED_CASES_PATH)}

    def test_original_failed_labels_are_preserved(self):
        original = {case["id"]: case for case in load_cases(DEFAULT_CASES_PATH)}
        self.assertEqual(len(self.cases), 16)
        for case_id in ("intent_008", "intent_015", "intent_025"):
            with self.subTest(case=case_id):
                self.assertEqual(self.cases[case_id], original[case_id])

    def test_prompt_and_tool_descriptions_cover_forms_and_time_priority(self):
        prompt = build_system_prompt("Winiary").casefold()
        fields = RECIPE_TOOLS[0]["function"]["parameters"]["properties"]
        for text in (prompt, fields["time_max"]["description"].casefold()):
            for term in ("szybki", "szybka", "szybkie", "na szybko", "45", "pierwsze", "pomi"):
                with self.subTest(term=term):
                    self.assertIn(term, text)
        for text in (prompt, fields["nutrition_goal"]["description"].casefold()):
            for term in ("lekka", "lekkie", "low_kcal", "zanegowana"):
                self.assertIn(term, text)
        self.assertNotIn("time_max", RECIPE_TOOLS[0]["function"]["parameters"]["required"])

    def test_new_supported_cases_are_not_blocked_by_preflight(self):
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                self.assertFalse(mentions_unsupported_allergy(case["user_message"]))
                self.assertFalse(mentions_unsupported_exclusion(case["user_message"]))

    def assert_backend_receives_expected(self, case):
        args = dict(case["expected"])
        if args["time_max"] is None:
            del args["time_max"]
        call = SimpleNamespace(function=SimpleNamespace(
            name="get_recommendations", arguments=json.dumps(args)))
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
        with patch("main.client.chat.completions.create", return_value=response) as api:
            with patch("main.get_recommendations", return_value={"query": {}, "recommendations": []}) as backend:
                chat_with_bot(case["user_message"], "Winiary")
                backend.assert_called_once_with(**case["expected"])
            api.assert_called_once()

    def test_speed_and_explicit_limits_are_passed_without_rewriting(self):
        for case in self.cases.values():
            if case["expected"]["time_max"] is not None:
                with self.subTest(case=case["id"]):
                    self.assert_backend_receives_expected(case)

    def test_goal_and_negation_cases_do_not_get_default_30(self):
        for case in self.cases.values():
            if case["expected"]["time_max"] is None:
                with self.subTest(case=case["id"]):
                    self.assert_backend_receives_expected(case)

    def test_runtime_does_not_silently_repair_model_omission(self):
        case = self.cases["intent_025"]
        args = dict(case["expected"])
        del args["time_max"]
        actual = parse_recipe_tool_arguments(json.dumps(args))
        self.assertNotIn("time_max", actual)
        self.assertFalse(score_case(case["expected"], actual)["field_results"]["time_max"])

    def test_grader_detects_spurious_30_and_missed_low_kcal(self):
        light = self.cases["time_goal_004"]["expected"]
        self.assertIsNone(light["time_max"])
        self.assertFalse(score_case(light, dict(light, time_max=30))["passed"])
        old_failure = self.cases["intent_015"]["expected"]
        self.assertFalse(score_case(old_failure, dict(old_failure, nutrition_goal="standard"))["passed"])
