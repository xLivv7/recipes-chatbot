import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from evals.run_routing_eval import evaluate_case, observe_response
from test_separated_routing_eval import case, response, tool_args


def no_tool_response(content, refusal=None, finish_reason="stop"):
    return SimpleNamespace(choices=[SimpleNamespace(finish_reason=finish_reason,
        message=SimpleNamespace(tool_calls=None, content=content, refusal=refusal))])


class NoToolDiagnosticTests(unittest.TestCase):
    def test_content_is_preserved_verbatim_without_dispatching_json(self):
        content = "```json\n" + json.dumps(tool_args()) + "\n```"
        client = Mock()
        client.chat.completions.create.return_value = no_tool_response(content)
        with patch("main.get_recommendations") as backend:
            result = evaluate_case(case(), "application", client)
            backend.assert_not_called()
        self.assertEqual(result["no_tool_content"], content)
        self.assertEqual(result["finish_reason"], "stop")
        self.assertEqual(result["model_action"], "no_tool")
        self.assertEqual(result["failure_stage"], "decision")
        self.assertIsNone(result["actual"])

    def test_refusal_and_finish_reason_are_distinct_from_content(self):
        result = observe_response(no_tool_response(None, "refusal text", "content_filter"))
        self.assertIsNone(result["no_tool_content"])
        self.assertEqual(result["no_tool_refusal"], "refusal text")
        self.assertEqual(result["finish_reason"], "content_filter")

    def test_empty_content_is_not_lost_or_replaced(self):
        for content in (None, "", "   "):
            with self.subTest(content=content):
                self.assertEqual(observe_response(no_tool_response(content))["no_tool_content"], content)

    def test_actual_tool_call_does_not_log_content_as_no_tool(self):
        value = response()
        value.choices[0].message.content = "Optional model prose"
        observed = observe_response(value)
        self.assertIsNone(observed["no_tool_content"])
        self.assertEqual(observed["model_action"], "tool")

    def test_guard_and_missing_choices_do_not_invent_model_text(self):
        guarded = evaluate_case(case("alergia na mleko", "no_tool"), "application", Mock())
        empty = observe_response(SimpleNamespace(choices=[]))
        for result in (guarded, empty):
            for field in ("no_tool_content", "no_tool_refusal", "finish_reason"):
                self.assertIsNone(result[field])
