from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

import httpx
from openai import APIConnectionError

import main
from core.interpretation_contract import CLIENT_CONFIGURATION
from core.recommendation_errors import RecommendationDataError
from core.response_renderer import ResponsePayloadError
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion
from test_interpretation_contract import DATA, wire
from test_interpretation_adapter import ir_reply
from test_response_renderer import payload
from test_preflight_grammar import KNOWN_FALSE_BLOCKS


def fake_client(value=None, error=None):
    return NS(chat=NS(completions=NS(create=Mock(return_value=value or ir_reply(), side_effect=error))))


class InterpretationApplicationTests(unittest.TestCase):
    def invoke(self, row, client=None, trace=None):
        return main.chat_with_bot(row["user_message"], "Winiary", interpretation_mode="facts_v1",
            interpretation_client=client or fake_client(ir_reply(row["interpretation"])), diagnostics=trace)

    def test_every_design_case_uses_actual_preflight_compiler_and_dispatch(self):
        for row in DATA["valid"]:
            client, trace = fake_client(ir_reply(row["interpretation"])), {}
            with self.subTest(case=row["id"]), patch("main.run_recommendation_tool", return_value={"query": {}, "recommendations": []}) as lookup:
                result = self.invoke(row, client, trace)
                blocked = mentions_unsupported_allergy(row["user_message"]) or mentions_unsupported_exclusion(row["user_message"])
                if blocked:
                    client.chat.completions.create.assert_not_called()
                    lookup.assert_not_called()
                    self.assertEqual(trace["api_calls"], 0)
                elif row["expected_action"] == "tool":
                    client.chat.completions.create.assert_called_once()
                    lookup.assert_called_once_with(wire(row["expected"]))
                    self.assertEqual(trace["backend_calls"], 1)
                    self.assertIn("Nie znaleziono", result)
                else:
                    client.chat.completions.create.assert_called_once()
                    lookup.assert_not_called()
                    self.assertEqual(result, main.NO_TOOL_RESPONSE)
                    self.assertEqual(trace["interpretation_tool_calls"], 1)
                    self.assertEqual(trace["backend_calls"], 0)
                self.assertIsNone(trace["model_decision_correct"])

    def test_all_five_released_requests_reach_ir_adapter_and_keep_protocol_errors(self):
        for query in KNOWN_FALSE_BLOCKS:
            client, trace = fake_client(ir_reply(count=0)), {}
            with self.subTest(query=query), patch("main.run_recommendation_tool") as lookup:
                result = main.chat_with_bot(query, "Winiary", interpretation_mode="facts_v1",
                    interpretation_client=client, diagnostics=trace)
                client.chat.completions.create.assert_called_once()
                self.assertEqual(client.chat.completions.create.call_args.kwargs["messages"][1]["content"], query)
                self.assertEqual(result, main.INVALID_TOOL_RESPONSE)
                self.assertIsNone(trace["guard"])
                self.assertIsNone(trace["model_decision_correct"])
                self.assertEqual(trace["failure_stage"], "protocol")
                self.assertEqual(trace["api_calls"], 1)
                self.assertEqual(trace["backend_calls"], 0)
                lookup.assert_not_called()

    def test_facts_mode_renders_backend_facts_without_model_text_or_second_request(self):
        row = next(row for row in DATA["valid"] if row["id"] == "F-01")
        client, trace = fake_client(), {}
        with patch("main.get_recommendations", return_value=payload()) as lookup:
            result = self.invoke(row, client, trace)
        client.chat.completions.create.assert_called_once()
        lookup.assert_called_once_with(**wire(row["expected"]), time_max=None)
        self.assertIn("Ryż", result)
        self.assertNotIn("MODEL_TEXT", result)
        self.assertNotIn("SECRET", result)
        self.assertEqual(trace["api_calls"], trace["interpretation_tool_calls"])
        self.assertEqual(trace["backend_calls"], 1)

    def test_invalid_or_missing_interpretations_never_use_content_as_fallback(self):
        values = [ir_reply(count=0), ir_reply(count=2), ir_reply(name="get_recommendations"),
                  ir_reply(finish="length"), ir_reply(refusal="PRIVATE_PROVIDER_TEXT")]
        values += [ir_reply(row["interpretation"]) for row in DATA["invalid"]]
        for value in values:
            trace = {}
            with self.subTest(value=value), patch("main.run_recommendation_tool") as lookup:
                result = main.chat_with_bot("Kolacja do 30 minut", "Winiary", interpretation_mode="facts_v1",
                    interpretation_client=fake_client(value), diagnostics=trace)
                self.assertEqual(result, main.INVALID_TOOL_RESPONSE)
                self.assertEqual(trace["effective_action"], "error")
                self.assertEqual(trace["backend_calls"], 0)
                lookup.assert_not_called()

    def test_api_error_keeps_safe_message_and_one_attempt(self):
        client = fake_client(error=APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"), message="PRIVATE_ERROR"))
        with patch("main.run_recommendation_tool") as lookup:
            result = main.chat_with_bot("Podaj przepis", "Winiary", interpretation_mode="facts_v1", interpretation_client=client)
            self.assertEqual(result, main.API_ERROR_RESPONSE)
            self.assertNotIn("PRIVATE_ERROR", result)
            client.chat.completions.create.assert_called_once()
            lookup.assert_not_called()

    def test_allergy_priority_and_following_requests_do_not_reuse_diagnostics_or_history(self):
        trace = {"interpretation": "STALE"}
        with patch("main.OpenAI") as factory, patch("main.run_recommendation_tool") as lookup:
            result = main.chat_with_bot("Alergia na mleko, bez jaj", "Winiary", interpretation_mode="facts_v1", diagnostics=trace)
            self.assertEqual(result, main.UNSUPPORTED_ALLERGY_RESPONSE)
            self.assertEqual(trace["guard"], "allergy")
            self.assertNotIn("interpretation", trace)
            factory.assert_not_called()
            lookup.assert_not_called()
        for query in ("", "jak poprzednio"):
            client = fake_client(ir_reply(dict(contract_version="IR-1", request_kind="context_dependent", facts=[])))
            result = main.chat_with_bot(query, "Winiary", interpretation_mode="facts_v1", interpretation_client=client, diagnostics=trace)
            self.assertEqual(result, main.NO_TOOL_RESPONSE)
            self.assertEqual(trace["request_kind"], "context_dependent")
            self.assertIsNone(trace["guard"])
            self.assertEqual(client.chat.completions.create.call_args.kwargs["messages"][1]["content"], query)

    def test_missing_schema_stops_before_client_factory_or_backend(self):
        with patch("core.interpretation_contract.SCHEMA_PATH", Path("missing-T026-schema.json")):
            with patch("main.OpenAI") as factory, patch("main.run_recommendation_tool") as lookup:
                trace = {}
                result = main.chat_with_bot("Podaj przepis", "Winiary", interpretation_mode="facts_v1", diagnostics=trace)
                self.assertEqual(result, main.INVALID_TOOL_RESPONSE)
                self.assertEqual(trace["failure_stage"], "configuration")
                factory.assert_not_called()
                lookup.assert_not_called()

    def test_owned_facts_client_configuration_is_fixed_and_legacy_client_unused(self):
        with patch("main.OpenAI") as factory, patch.object(main.client.chat.completions, "create") as legacy:
            factory.return_value.__enter__.return_value = fake_client()
            with patch("main.run_recommendation_tool", return_value={"query": {}, "recommendations": []}):
                main.chat_with_bot("Podaj przepis", "Winiary", interpretation_mode="facts_v1")
            factory.assert_called_once_with(**CLIENT_CONFIGURATION)
            factory.return_value.__exit__.assert_called_once()
            legacy.assert_not_called()

    def test_default_remains_legacy_and_misconfigured_modes_do_not_call_any_client(self):
        raw = json.dumps(dict(diet="none", protein_preference="none", restrictions=[], nutrition_goal="standard", category="kolacja", top_n=3))
        with patch.object(main.client.chat.completions, "create", return_value=ir_reply(raw=raw, name="get_recommendations")) as legacy:
            with patch("main.OpenAI") as factory, patch("main.run_recommendation_tool", return_value={"query": {}, "recommendations": []}):
                main.chat_with_bot("Podaj przepis", "Winiary")
                legacy.assert_called_once()
                factory.assert_not_called()
                self.assertEqual(legacy.call_args.kwargs["tool_choice"], "auto")
                self.assertNotIn("max_completion_tokens", legacy.call_args.kwargs)
        for kwargs in (dict(interpretation_mode="unknown"), dict(interpretation_client=fake_client())):
            with self.subTest(kwargs=kwargs), patch.object(main.client.chat.completions, "create") as legacy, self.assertRaises(ValueError):
                main.chat_with_bot("Podaj przepis", "Winiary", **kwargs)
            legacy.assert_not_called()

    def test_data_and_payload_errors_keep_their_boundaries_after_one_dispatch(self):
        for error, text, stage in ((RecommendationDataError("controlled"), "przygotować", "dispatch"),
                                   (ResponsePayloadError("controlled"), "wyświetlić", "render")):
            trace, client = {}, fake_client()
            with self.subTest(stage=stage), patch("main.run_recommendation_tool", side_effect=error) as lookup:
                result = main.chat_with_bot("Podaj przepis", "Winiary", interpretation_mode="facts_v1", interpretation_client=client, diagnostics=trace)
                self.assertIn(text, result)
                self.assertEqual(trace["backend_calls"], 1)
                self.assertEqual(trace["failure_stage"], stage)
                self.assertEqual(trace["effective_action"], "error")
                lookup.assert_called_once()
                client.chat.completions.create.assert_called_once()
        with patch("main.run_recommendation_tool", side_effect=RuntimeError("programming error")), self.assertRaises(RuntimeError):
            main.chat_with_bot("Podaj przepis", "Winiary", interpretation_mode="facts_v1", interpretation_client=fake_client())


if __name__ == "__main__":
    unittest.main()
