from copy import deepcopy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from evals.run_llm_eval import DEFAULT_CASES_PATH, extract_tool_args, load_cases
from main import INVALID_TOOL_RESPONSE, build_system_prompt, chat_with_bot
from test_response_renderer import payload


class SingleRecommendationCallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in load_cases(DEFAULT_CASES_PATH)}

    def tool_response(self, case, count=1):
        args = dict(case["expected"])
        if args["time_max"] is None:
            del args["time_max"]
        call = SimpleNamespace(function=SimpleNamespace(
            name="get_recommendations", arguments=json.dumps(args)))
        return SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(tool_calls=[call] * count))])

    def assert_two_results_in_one_call(self, case_id):
        case = self.cases[case_id]
        self.assertEqual(case["expected"]["top_n"], 2)
        data = payload()
        second = deepcopy(data["recommendations"][0])
        second.update(recipe_id="R2", title_pl="Drugi przepis")
        data["recommendations"].append(second)
        with patch("main.client.chat.completions.create", return_value=self.tool_response(case)) as api:
            with patch("main.get_recommendations", return_value=data) as backend:
                result = chat_with_bot(case["user_message"], "Winiary")
                backend.assert_called_once_with(**case["expected"])
            api.assert_called_once()
            self.assertIs(api.call_args.kwargs["parallel_tool_calls"], False)
            self.assertEqual(api.call_args.kwargs["tool_choice"], "auto")
        self.assertEqual(sum(line.startswith("### ") for line in result.splitlines()), 2)

    def test_intent_007_two_vegetarian_snacks_use_one_search(self):
        self.assert_two_results_in_one_call("intent_007")

    def test_intent_059_two_lactose_free_desserts_use_one_search(self):
        self.assert_two_results_in_one_call("intent_059")

    def test_multiple_valid_calls_still_reject_entire_response(self):
        for case_id in ("intent_007", "intent_059"):
            case = self.cases[case_id]
            with self.subTest(case=case_id), patch(
                    "main.client.chat.completions.create", return_value=self.tool_response(case, 2)) as api:
                with patch("main.get_recommendations") as backend:
                    self.assertEqual(chat_with_bot(case["user_message"], "Winiary"), INVALID_TOOL_RESPONSE)
                    backend.assert_not_called()
                api.assert_called_once()

    def test_intent_eval_preserves_top_n_in_single_call(self):
        for case_id in ("intent_007", "intent_059"):
            case = self.cases[case_id]
            client = Mock()
            client.chat.completions.create.return_value = self.tool_response(case)
            with self.subTest(case=case_id):
                args = extract_tool_args(client, "gpt-4o-mini", case["user_message"], "Winiary")
                self.assertEqual(args["top_n"], 2)
                client.chat.completions.create.assert_called_once()
                self.assertIs(client.chat.completions.create.call_args.kwargs["parallel_tool_calls"], False)

    def test_intent_eval_rejects_multiple_calls(self):
        client = Mock()
        client.chat.completions.create.return_value = self.tool_response(self.cases["intent_007"], 2)
        with self.assertRaisesRegex(ValueError, "exactly one tool call"):
            extract_tool_args(client, "gpt-4o-mini", "dwie przekaski", "Winiary")

    def test_prompt_distinguishes_proposal_count_from_call_count(self):
        self.assertIn("jeden call z top_n=2", build_system_prompt("Winiary"))
