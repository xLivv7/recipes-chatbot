import json
import re
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.llm_tools import RECIPE_TOOLS
from core.tool_call_validation import ToolArgumentsError, parse_recipe_tool_arguments
from evals.run_llm_eval import DEFAULT_CASES_PATH, load_cases
from main import INVALID_TOOL_RESPONSE, build_system_prompt, chat_with_bot


class CompletePromptExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = re.findall(r"Zapytanie: ([^\n]+)\n```json\n(.*?)\n```",
                                  build_system_prompt("Winiary"), re.DOTALL)
        cls.schema = RECIPE_TOOLS[0]["function"]["parameters"]

    def test_every_example_is_complete_and_valid_under_current_schema(self):
        self.assertEqual(len(self.examples), 5)
        for query, raw in self.examples:
            with self.subTest(query=query):
                args = parse_recipe_tool_arguments(raw)
                self.assertTrue(set(self.schema["required"]).issubset(args))
                self.assertTrue(set(args).issubset(self.schema["properties"]))
                self.assertEqual(args["protein_preference"], "none")

    def test_original_regression_examples_keep_expected_meaning(self):
        examples = {query: json.loads(raw) for query, raw in self.examples}
        cases = {case["id"]: case for case in load_cases(DEFAULT_CASES_PATH)}
        for case_id in ("intent_008", "intent_015", "intent_025"):
            with self.subTest(case=case_id):
                case = cases[case_id]
                self.assertEqual(examples[case["user_message"]], case["expected"])

    def test_no_time_examples_omit_only_optional_field(self):
        without_time = [json.loads(raw) for _, raw in self.examples if "time_max" not in json.loads(raw)]
        self.assertEqual(len(without_time), 2)
        for args in without_time:
            self.assertEqual(set(args), set(self.schema["required"]))
            self.assertIn(args["nutrition_goal"], ("low_kcal", "keto"))

    def test_missing_required_field_is_rejected_for_every_example(self):
        for query, raw in self.examples:
            for field in self.schema["required"]:
                args = json.loads(raw)
                del args[field]
                with self.subTest(query=query, field=field), self.assertRaises(ToolArgumentsError):
                    parse_recipe_tool_arguments(json.dumps(args))

    def test_runtime_does_not_fill_missing_protein_preference(self):
        cases = {case["id"]: case for case in load_cases(DEFAULT_CASES_PATH)}
        for case_id in ("intent_015", "intent_025"):
            case = cases[case_id]
            args = dict(case["expected"])
            del args["protein_preference"]
            call = SimpleNamespace(function=SimpleNamespace(
                name="get_recommendations", arguments=json.dumps(args)))
            response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
            with self.subTest(case=case_id), patch("main.client.chat.completions.create", return_value=response):
                with patch("main.run_recommendation_tool") as backend, self.assertLogs("main", level="WARNING"):
                    self.assertEqual(chat_with_bot(case["user_message"], "Winiary"), INVALID_TOOL_RESPONSE)
                    backend.assert_not_called()
