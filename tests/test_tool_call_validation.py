import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
from openai import APIConnectionError, APITimeoutError, AuthenticationError, InternalServerError, RateLimitError

from core.tool_call_validation import ToolArgumentsError, parse_recipe_tool_arguments
from main import API_ERROR_RESPONSE, INVALID_TOOL_RESPONSE, chat_with_bot


def arguments():
    return {"diet": "none", "protein_preference": "none", "restrictions": [],
            "nutrition_goal": "standard", "category": "kolacja", "top_n": 3}


class ToolCallValidationTests(unittest.TestCase):
    def test_valid_arguments_preserve_values_and_optional_time_absence(self):
        args = arguments()
        self.assertEqual(parse_recipe_tool_arguments(json.dumps(args)), args)
        args.update(time_max=30, restrictions=["gluten_free", "lactose_free"])
        self.assertEqual(parse_recipe_tool_arguments(json.dumps(args)), args)

    def test_missing_required_fields_are_rejected(self):
        for key in arguments():
            args = arguments()
            del args[key]
            with self.subTest(key=key), self.assertRaises(ToolArgumentsError):
                parse_recipe_tool_arguments(json.dumps(args))

    def test_malformed_non_object_and_duplicate_json_are_rejected(self):
        for raw in (None, "", "{", "[]", "null", "1", '{"diet":"none","diet":"vegan"}'):
            with self.subTest(raw=raw), self.assertRaises(ToolArgumentsError):
                parse_recipe_tool_arguments(raw)

    def test_unknown_fields_and_enums_are_rejected(self):
        for key, value in (("extra", 1), ("diet", "vege"), ("category", "dinner"),
                           ("nutrition_goal", "unknown"), ("protein_preference", [])):
            args = arguments()
            args[key] = value
            with self.subTest(key=key), self.assertRaises(ToolArgumentsError):
                parse_recipe_tool_arguments(json.dumps(args))

    def test_numeric_values_are_not_coerced(self):
        for key in ("time_max", "top_n"):
            for value in (None, True, "3", 3.0, 0, -1, float("nan"), float("inf")):
                args = arguments()
                args[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ToolArgumentsError):
                    parse_recipe_tool_arguments(json.dumps(args))

    def test_invalid_restrictions_are_rejected(self):
        for value in (None, "gluten_free", ["gluten_free", "gluten_free"], ["milk_free"], [[]], [1]):
            args = arguments()
            args["restrictions"] = value
            with self.subTest(value=value), self.assertRaises(ToolArgumentsError):
                parse_recipe_tool_arguments(json.dumps(args))

    def test_conflicting_preferences_are_rejected(self):
        for diet, protein in (("vegan", "fish"), ("vegetarian", "meat"), ("pescetarian", "meat")):
            args = arguments()
            args.update(diet=diet, protein_preference=protein)
            with self.subTest(diet=diet), self.assertRaises(ToolArgumentsError):
                parse_recipe_tool_arguments(json.dumps(args))

    def test_invalid_calls_never_reach_backend(self):
        for raw in ("{", "{}", "null", json.dumps(dict(arguments(), top_n=True))):
            call = SimpleNamespace(function=SimpleNamespace(name="get_recommendations", arguments=raw))
            response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
            with self.subTest(raw=raw), patch("main.client.chat.completions.create", return_value=response):
                with patch("main.get_recommendations") as backend, self.assertLogs("main", level="WARNING"):
                    self.assertEqual(chat_with_bot("Zapytanie", "Winiary"), INVALID_TOOL_RESPONSE)
                    backend.assert_not_called()

    def test_multiple_calls_and_empty_choices_fail_closed(self):
        for response in (SimpleNamespace(choices=[]), SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(tool_calls=[object(), object()]))])):
            with patch("main.client.chat.completions.create", return_value=response), patch("main.get_recommendations") as backend:
                self.assertEqual(chat_with_bot("Zapytanie", "Winiary"), INVALID_TOOL_RESPONSE)
                backend.assert_not_called()

    def test_incomplete_filtered_or_refused_responses_stop_before_arguments_and_backend(self):
        signals = (("length", None), ("content_filter", None),
                   ("stop", "PROVIDER_REFUSAL_TEXT"), ("content_filter", "PROVIDER_REFUSAL_TEXT"))
        call = SimpleNamespace(function=SimpleNamespace(name="get_recommendations",
                                                       arguments=json.dumps(arguments())))
        for finish, refusal in signals:
            for calls in ([], [call]):
                value = SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish,
                    message=SimpleNamespace(tool_calls=calls, content="MODEL_CONTENT", refusal=refusal))])
                with self.subTest(finish=finish, refusal=bool(refusal), calls=len(calls)), \
                        patch("main.client.chat.completions.create", return_value=value) as api, \
                        patch("main.parse_recipe_tool_arguments") as parser, \
                        patch("main.get_recommendations") as backend:
                    result = chat_with_bot("Podaj przepis", "Winiary")
                    self.assertEqual(result, INVALID_TOOL_RESPONSE)
                    parser.assert_not_called()
                    backend.assert_not_called()
                    api.assert_called_once()
                    self.assertNotIn("PROVIDER_REFUSAL_TEXT", result)
                    self.assertNotIn("MODEL_CONTENT", result)

    def test_unknown_function_uses_the_same_invalid_response_without_dispatch(self):
        call = SimpleNamespace(function=SimpleNamespace(name="unknown", arguments=json.dumps(arguments())))
        value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
        with patch("main.client.chat.completions.create", return_value=value), \
                patch("main.get_recommendations") as backend:
            self.assertEqual(chat_with_bot("Podaj przepis", "Winiary"), INVALID_TOOL_RESPONSE)
            backend.assert_not_called()

    def test_api_errors_use_safe_response_without_exception_details(self):
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        errors = [APIConnectionError(request=request), APITimeoutError(request=request)]
        for error_class, status in ((AuthenticationError, 401), (RateLimitError, 429), (InternalServerError, 500)):
            errors.append(error_class("SECRET", response=httpx.Response(status, request=request), body=None))
        for error in errors:
            with self.subTest(error=type(error).__name__), patch("main.client.chat.completions.create", side_effect=error) as api:
                with patch("main.get_recommendations") as backend, self.assertLogs("main", level="WARNING") as logs:
                    self.assertEqual(chat_with_bot("Zapytanie", "Winiary"), API_ERROR_RESPONSE)
                    backend.assert_not_called()
                    self.assertNotIn("SECRET", " ".join(logs.output))
                api.assert_called_once()

    def test_unexpected_programming_errors_are_not_hidden(self):
        with patch("main.client.chat.completions.create", side_effect=RuntimeError("bug")):
            with self.assertRaises(RuntimeError):
                chat_with_bot("Zapytanie", "Winiary")
