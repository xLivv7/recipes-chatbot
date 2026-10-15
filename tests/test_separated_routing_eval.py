import argparse
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import httpx
from openai import APIConnectionError

from evals.run_routing_eval import (DEFAULT_CASES_PATH, DEFAULT_ROUTING_CASES_PATH,
                                   GUARD_CASES_PATH, evaluate_case, observe_response,
                                   run_eval, summarize)


def tool_args():
    return {"diet": "none", "protein_preference": "none", "restrictions": [],
            "nutrition_goal": "standard", "category": "kolacja", "top_n": 3}


def response(raw=None, count=1, name="get_recommendations"):
    calls = [SimpleNamespace(function=SimpleNamespace(name=name, arguments=raw or json.dumps(tool_args())))] * count
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=calls))])


def case(message="Kolacja", action="tool"):
    return {"id": "test", "user_message": message, "expected_action": action,
            **({"expected": dict(tool_args(), time_max=None)} if action == "tool" else {})}


class SeparatedRoutingEvalTests(unittest.TestCase):
    def test_multiple_calls_preserve_raw_trace_and_separate_decision_from_protocol(self):
        client = Mock()
        client.chat.completions.create.return_value = response(count=2)
        result = evaluate_case(case(), "raw", client)
        self.assertEqual(result["tool_call_count"], 2)
        self.assertEqual(len(result["raw_tool_calls"]), 2)
        self.assertTrue(result["model_decision_correct"])
        self.assertFalse(result["protocol_valid"])
        self.assertIsNone(result["decision_correct"])
        self.assertEqual(result["failure_stage"], "protocol")

    def test_argument_errors_are_not_semantic_errors(self):
        for raw in ("{", "{}", json.dumps(dict(tool_args(), top_n=True))):
            with self.subTest(raw=raw):
                observed = observe_response(response(raw))
                self.assertTrue(observed["protocol_valid"])
                self.assertFalse(observed["arguments_valid"])
                self.assertEqual(observed["failure_stage"], "arguments")

    def test_wrong_function_and_empty_choices_are_protocol_errors(self):
        for value in (response(name="unknown"), SimpleNamespace(choices=[])):
            self.assertEqual(observe_response(value)["failure_stage"], "protocol")

    def test_wrong_parameter_value_has_semantic_diagnosis(self):
        client = Mock()
        client.chat.completions.create.return_value = response(json.dumps(dict(tool_args(), time_max=30)))
        result = evaluate_case(case(), "raw", client)
        self.assertTrue(result["arguments_valid"])
        self.assertFalse(result["field_results"]["time_max"])
        self.assertEqual(result["failure_stage"], "semantics")

    def test_guard_pass_does_not_become_model_success(self):
        client = Mock()
        result = evaluate_case(case("Mam alergie na orzechy", "no_tool"), "application", client)
        self.assertTrue(result["passed"])
        self.assertEqual(result["guard"], "allergy")
        self.assertIsNone(result["model_decision_correct"])
        self.assertEqual(result["api_calls"], 0)
        self.assertEqual(result["backend_calls"], 0)
        client.chat.completions.create.assert_not_called()
        self.assertEqual(summarize([result])["metrics"]["model_decision_correct"]["total"], 0)

    def test_guard_false_positive_is_a_failure(self):
        result = evaluate_case(case("Nie musi byc bez jaj, chce kolacje"), "application", Mock())
        self.assertFalse(result["passed"])
        self.assertEqual(result["failure_stage"], "preflight")

    def test_raw_mode_does_not_use_application_guard(self):
        client = Mock()
        client.chat.completions.create.return_value = response()
        result = evaluate_case(case("Mam alergie na orzechy", "no_tool"), "raw", client)
        self.assertIsNone(result["guard"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["failure_stage"], "decision")
        self.assertEqual(result["api_calls"], 1)

    def test_application_dispatch_is_observed_without_real_backend(self):
        client = Mock()
        client.chat.completions.create.return_value = response()
        with patch("main.get_recommendations", side_effect=AssertionError("Database must not run")):
            result = evaluate_case(case(), "application", client)
        self.assertTrue(result["passed"])
        self.assertEqual(result["backend_calls"], 1)
        self.assertEqual(result["actual"], tool_args())
        self.assertIs(client.chat.completions.create.call_args.kwargs["parallel_tool_calls"], False)

    def test_application_rejects_multiple_calls_without_backend(self):
        client = Mock()
        client.chat.completions.create.return_value = response(count=2)
        result = evaluate_case(case(), "application", client)
        self.assertEqual(result["backend_calls"], 0)
        self.assertEqual(result["failure_stage"], "protocol")

    def test_no_tool_decision_is_scored_without_inventing_field_errors(self):
        client = Mock()
        client.chat.completions.create.return_value = response(count=0)
        result = evaluate_case(case(), "raw", client)
        self.assertEqual(result["failure_stage"], "decision")
        self.assertTrue(all(value is None for value in result["field_results"].values()))
        self.assertEqual(summarize([result])["field_accuracy_conditional"]["diet"]["total"], 0)

    def test_api_failure_is_not_a_no_tool_success_or_parameter_failure(self):
        for mode in ("raw", "application"):
            client = Mock()
            client.chat.completions.create.side_effect = APIConnectionError(
                request=httpx.Request("POST", "https://api.openai.com"), message="SECRET")
            with self.subTest(mode=mode):
                result = evaluate_case(case("Jaka jest pogoda?", "no_tool"), mode, client)
                self.assertFalse(result["passed"])
                self.assertEqual(result["failure_stage"], "api")
                self.assertIsNone(result["model_decision_correct"])
                self.assertNotIn("SECRET", json.dumps(result))

    def test_dry_runs_validate_datasets_without_api_client(self):
        for mode, planned in (("raw", 76), ("application", 66)):
            args = argparse.Namespace(cases=DEFAULT_CASES_PATH, routing_cases=DEFAULT_ROUTING_CASES_PATH,
                                      guard_cases=GUARD_CASES_PATH, limit=None, mode=mode,
                                      model="gpt-4o-mini", brand_name="Winiary", dry_run=True)
            with self.subTest(mode=mode), patch("evals.run_routing_eval.OpenAI") as api:
                report = run_eval(args)
                api.assert_not_called()
                self.assertEqual(report["summary"], {"total": 76, "planned_api_calls": planned})
                self.assertEqual(len(report["dataset_files"]), 3)
