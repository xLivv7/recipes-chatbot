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
    def test_controlled_no_tool_decisions_cover_scope_conflicts_and_nonstandalone_queries(self):
        from evals.prepare_routing_v5 import ROOT, load_cases
        probes = [row for name in ("routing_cases.json", "application_routing_cases.json")
                  for row in load_cases(ROOT / "evals" / name)
                  if row.get("expected_action") == "no_tool"]
        probes += [case(query, "no_tool") for query in (
            "Kolacja wegetariańska z prawdziwą rybą, nie zamiennikiem",
            "Kolacja pescetariańska z mięsem, nie zamiennikiem",
            "Kolacja bez mięsa, ale koniecznie z mięsem, nie zamiennikiem",
            "", "jak poprzednio")]
        for probe in probes:
            for mode in ("raw", "application"):
                client = Mock()
                client.chat.completions.create.return_value = no_tool_response("CONTROLLED_MODEL_TEXT")
                with self.subTest(query=probe["user_message"], mode=mode):
                    result = evaluate_case(probe, mode, client)
                    self.assertTrue(result["passed"])
                    self.assertEqual(result["effective_action"], "no_tool")
                    self.assertEqual(result["backend_calls"], 0)
                    self.assertTrue(all(v is None for v in result["field_results"].values()))
                    if result["guard"]:
                        self.assertEqual(result["api_calls"], 0)
                        self.assertIsNone(result["model_decision_correct"])
                        client.chat.completions.create.assert_not_called()
                    else:
                        self.assertEqual(result["api_calls"], 1)
                        self.assertTrue(result["model_decision_correct"])

    def test_response_failures_are_not_business_decisions_in_either_mode(self):
        signals = (("length", None, "truncated_response"),
                   ("content_filter", None, "filtered_response"),
                   ("stop", "PROVIDER_REFUSAL_TEXT", "provider_refusal"))
        for finish, refusal, reason in signals:
            for count in (0, 1):
                for action in ("tool", "no_tool"):
                    for mode in ("raw", "application"):
                        value = response(count=count)
                        value.choices[0].finish_reason = finish
                        value.choices[0].message.refusal = refusal
                        value.choices[0].message.content = "DIAGNOSTIC_CONTENT"
                        client = Mock()
                        client.chat.completions.create.return_value = value
                        with self.subTest(finish=finish, count=count, action=action, mode=mode):
                            result = evaluate_case(case("Podaj przepis", action), mode, client)
                            self.assertFalse(result["passed"])
                            self.assertEqual(result["effective_action"], "error")
                            self.assertEqual(result["failure_stage"], "protocol")
                            self.assertEqual(result["response_failure_reason"], reason)
                            self.assertEqual(result["response_validation_version"], "T022-v1")
                            self.assertFalse(result["protocol_valid"])
                            self.assertIsNone(result["arguments_valid"])
                            self.assertIsNone(result["model_action"])
                            self.assertIsNone(result["model_decision_correct"])
                            self.assertIsNone(result["decision_correct"])
                            self.assertIsNone(result["actual"])
                            self.assertTrue(all(v is None for v in result["field_results"].values()))
                            self.assertEqual(result["tool_call_count"], count)
                            self.assertEqual(len(result["raw_tool_calls"]), count)
                            self.assertEqual(result["response_refusal"], refusal)
                            self.assertEqual(result["backend_calls"], 0)
                            self.assertEqual(result["api_calls"], 1)

    def test_empty_refusal_does_not_invalidate_a_complete_no_tool_decision(self):
        for refusal in (None, ""):
            for mode in ("raw", "application"):
                client = Mock()
                client.chat.completions.create.return_value = no_tool_response(None, refusal)
                with self.subTest(refusal=refusal, mode=mode):
                    result = evaluate_case(case("Jaka jest stolica Francji?", "no_tool"), mode, client)
                    self.assertTrue(result["passed"])
                    self.assertIsNone(result["response_failure_reason"])
                    self.assertEqual(result["backend_calls"], 0)

    def test_five_former_false_blocks_reach_interpretation_without_inventing_success(self):
        from evals.prepare_routing_v5 import ROOT, SPEC, DEVELOPMENT, guard_audit, load_cases, wire_args
        development = [row for name in DEVELOPMENT for row in load_cases(ROOT / name)]
        probes = guard_audit(development, (ROOT / SPEC).read_text(encoding="utf-8"))
        self.assertEqual(len(probes), 5)
        for probe in probes:
            self.assertFalse(probe["preflight_blocked"])
            for has_tool in (False, True):
                client = Mock()
                client.chat.completions.create.return_value = (response(json.dumps(wire_args(probe["expected"])))
                    if has_tool else no_tool_response("CONTROLLED_MODEL_TEXT"))
                with self.subTest(case=probe["id"], has_tool=has_tool):
                    result = evaluate_case(probe, "application", client)
                    self.assertIsNone(result["guard"])
                    self.assertEqual(result["passed"], has_tool)
                    self.assertEqual(result["failure_stage"], None if has_tool else "decision")
                    self.assertEqual(result["model_decision_correct"], has_tool)
                    self.assertEqual(result["backend_calls"], int(has_tool))
                    self.assertEqual(result["api_calls"], 1)
                    client.chat.completions.create.assert_called_once()

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
            self.assertEqual(result["response_validation_version"], "T022-v1")
            for field in ("no_tool_content", "no_tool_refusal", "finish_reason"):
                self.assertIsNone(result[field])
