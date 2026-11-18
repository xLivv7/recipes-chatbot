import json
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

import httpx
from openai import APIConnectionError, APITimeoutError, OpenAI

from core.interpretation_contract import TOOL_NAME, build_interpretation_request
from core.interpretation_adapter import decode_interpretation_response, execute_interpretation_request
from test_interpretation_contract import DATA


def ir_reply(interpretation=None, *, raw=None, name=TOOL_NAME, count=1, finish="tool_calls", refusal=None):
    raw = raw if raw is not None else json.dumps(interpretation or dict(contract_version="IR-1", request_kind="recipe", facts=[]))
    calls = [NS(function=NS(name=name, arguments=raw)) for _ in range(count)]
    return NS(model="controlled-model", _request_id="controlled-request", usage=NS(prompt_tokens=100, completion_tokens=20, total_tokens=120),
        choices=[NS(finish_reason=finish, message=NS(tool_calls=calls, content="MODEL_TEXT 999 kcal SECRET", refusal=refusal))])


class InterpretationAdapterTests(unittest.TestCase):
    def test_every_valid_interpretation_has_separate_transport_and_business_results(self):
        for row in DATA["valid"]:
            with self.subTest(case=row["id"]):
                result = decode_interpretation_response(ir_reply(row["interpretation"]), row["user_message"])
                self.assertEqual(result.action, "search" if row["expected_action"] == "tool" else "no_search")
                self.assertEqual(result.diagnostics["interpretation_tool_calls"], 1)
                self.assertIsNone(result.diagnostics["model_decision_correct"])
                self.assertIsNone(result.diagnostics["model_action"])
                self.assertEqual(result.diagnostics["backend_calls"], 0)
                self.assertEqual(result.diagnostics["request_kind"], row["interpretation"]["request_kind"])
                self.assertEqual(result.diagnostics["interpretation"], row["interpretation"])

    def test_protocol_errors_never_become_business_no_search_or_parse_content(self):
        for value in (ir_reply(count=0), ir_reply(count=2), ir_reply(name="get_recommendations"),
                      ir_reply(name="unknown"), NS(choices=[]), NS(choices=[NS(message=None)])):
            with self.subTest(response=value), patch("core.interpretation_adapter.parse_interpretation_arguments") as parser:
                result = decode_interpretation_response(value, "Podaj przepis")
                self.assertEqual(result.action, "error")
                self.assertEqual(result.diagnostics["failure_stage"], "protocol")
                self.assertIsNone(result.arguments)
                parser.assert_not_called()

    def test_T022_metadata_failures_take_priority_even_over_valid_looking_calls(self):
        for finish, refusal, reason in (("length", None, "truncated_response"),
                ("content_filter", None, "filtered_response"), ("stop", "PRIVATE_PROVIDER_TEXT", "provider_refusal")):
            for count in (0, 1):
                with self.subTest(finish=finish, count=count), patch("core.interpretation_adapter.parse_interpretation_arguments") as parser:
                    result = decode_interpretation_response(ir_reply(count=count, finish=finish, refusal=refusal), "Podaj przepis")
                    self.assertEqual(result.action, "error")
                    self.assertEqual(result.diagnostics["response_failure_reason"], reason)
                    self.assertEqual(result.diagnostics["response_validation_version"], "T022-v1")
                    parser.assert_not_called()

    def test_invalid_facts_are_interpretation_errors_not_defaults_or_model_decisions(self):
        for row in DATA["invalid"]:
            with self.subTest(case=row["id"]):
                result = decode_interpretation_response(ir_reply(row["interpretation"]), row["user_message"])
                self.assertEqual(result.action, "error")
                self.assertEqual(result.diagnostics["failure_stage"], "interpretation")
                self.assertIsNone(result.arguments)
                self.assertIsNone(result.diagnostics["compiler_action"])

    def test_one_request_has_forced_tool_configuration_and_no_labels_or_history(self):
        fake = NS(chat=NS(completions=NS(create=Mock(return_value=ir_reply()))))
        request = build_interpretation_request("Podaj przepis", "Winiary")
        result = execute_interpretation_request(fake, "Podaj przepis", request)
        fake.chat.completions.create.assert_called_once_with(**request)
        self.assertEqual(result.diagnostics["api_calls"], 1)
        self.assertEqual(request["tool_choice"], dict(type="function", function=dict(name=TOOL_NAME)))
        self.assertIs(request["tools"][0]["function"]["strict"], True)
        self.assertEqual(request["max_completion_tokens"], 1024)
        self.assertEqual([message["role"] for message in request["messages"]], ["system", "user"])
        self.assertNotIn("expected", request)

    def test_api_errors_have_one_attempt_and_no_exception_text(self):
        errors = [APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"), message="PRIVATE_EXCEPTION"),
                  APITimeoutError(request=httpx.Request("POST", "https://api.openai.com"))]
        for error in errors:
            fake = NS(chat=NS(completions=NS(create=Mock(side_effect=[error, AssertionError("Retry forbidden")]))))
            with self.subTest(error=type(error).__name__):
                result = execute_interpretation_request(fake, "Podaj przepis", build_interpretation_request("Podaj przepis", "Winiary"))
                self.assertEqual(result.action, "error")
                self.assertEqual(result.diagnostics["failure_stage"], "api")
                self.assertEqual(result.diagnostics["api_calls"], 1)
                self.assertNotIn("PRIVATE_EXCEPTION", json.dumps(result.diagnostics))
                fake.chat.completions.create.assert_called_once()

    def test_real_sdk_client_requires_first_party_endpoint_zero_retry_and_timeout(self):
        for changes in (dict(max_retries=2), dict(base_url="https://example.com/v1"), dict(timeout=60)):
            config = dict(api_key="unused-offline", max_retries=0, timeout=30, base_url="https://api.openai.com/v1")
            config.update(changes)
            with self.subTest(changes=changes), OpenAI(**config) as client, patch.object(client.chat.completions, "create") as create:
                result = execute_interpretation_request(client, "Podaj przepis", build_interpretation_request("Podaj przepis", "Winiary"))
                self.assertEqual(result.diagnostics["failure_stage"], "configuration")
                self.assertEqual(result.diagnostics["api_calls"], 0)
                create.assert_not_called()

    def test_unexpected_compiler_errors_propagate_instead_of_becoming_no_search(self):
        with patch("core.interpretation_adapter.compile_interpretation", side_effect=RuntimeError("Programming error")):
            with self.assertRaises(RuntimeError):
                decode_interpretation_response(ir_reply(), "Podaj przepis")

    def test_correctly_configured_sdk_client_uses_one_mocked_request(self):
        with OpenAI(api_key="unused-offline", max_retries=0, timeout=30, base_url="https://api.openai.com/v1") as client:
            with patch.object(client.chat.completions, "create", return_value=ir_reply()) as create:
                result = execute_interpretation_request(client, "Podaj przepis", build_interpretation_request("Podaj przepis", "Winiary"))
                self.assertEqual(result.action, "search")
                self.assertEqual(result.diagnostics["api_calls"], 1)
                create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
