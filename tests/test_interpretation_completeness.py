from copy import deepcopy
import json
import unittest
from unittest.mock import patch

import main
from core.interpretation_adapter import decode_interpretation_response
from core.interpretation_compiler import compile_interpretation
from core.interpretation_completeness import check_completeness
from core.interpretation_contract import parse_interpretation_arguments
from test_interpretation_adapter import ir_reply
from test_interpretation_application import fake_client
from test_interpretation_contract import DATA, ROOT
from test_preflight_grammar import KNOWN_FALSE_BLOCKS


CASES = json.loads((ROOT / "specs/001-mvp-stabilization/contracts/interpretation-completeness.examples.json"
                   ).read_text(encoding="utf-8"))["cases"]


class CompletenessTests(unittest.TestCase):
    def test_design_contrasts_from_text_only_and_compiler_invariants(self):
        for row in CASES:
            with self.subTest(case=row["id"]):
                text, expected = row["user_message"], row["expected"]
                ir = parse_interpretation_arguments(json.dumps(row["interpretation"]), text)
                proposed = compile_interpretation(ir)
                before = deepcopy((ir, proposed))
                coverage = check_completeness(text, ir, proposed)
                self.assertEqual((ir, proposed), before)
                self.assertEqual(proposed.arguments, expected["proposed_arguments"])
                self.assertEqual(coverage.status, expected["completeness_status"])
                self.assertEqual(coverage.block_search, expected["block_search"])
                self.assertEqual(coverage.policy_version, "CMP-1")
                facts = {(f.kind, f.value, f.status) for f in ir.facts}
                if proposed.action == "search" and not row["annotated_unresolved_scope"]:
                    cues = row["annotated_cues"]
                    missing = {(c["rule_id"], c["source"], tuple(c["expected_signature"])) for c in cues
                               if tuple(c["expected_signature"]) not in facts}
                    self.assertEqual(set(coverage.checked_rules), {c["rule_id"] for c in cues})
                    self.assertEqual({(f.rule_id, f.source, f.expected_signature) for f in coverage.findings}, missing)
                    # Removing all facts reveals every positive, permitted and waived witness.
                    empty = parse_interpretation_arguments(json.dumps(dict(row["interpretation"], facts=[])), text)
                    detected = check_completeness(text, empty, compile_interpretation(empty))
                    self.assertEqual({(f.source, f.expected_signature) for f in detected.findings},
                                     {(c["source"], tuple(c["expected_signature"])) for c in cues})
                duplicate = dict(row["interpretation"], facts=list(reversed(row["interpretation"]["facts"]))
                                 + row["interpretation"]["facts"])
                reordered = parse_interpretation_arguments(json.dumps(duplicate), text)
                self.assertEqual(check_completeness(text, reordered, compile_interpretation(reordered)), coverage)

    def test_all_35_valid_ir_examples_keep_actions_and_arguments(self):
        for row in DATA["valid"]:
            with self.subTest(case=row["id"]):
                response = ir_reply(row["interpretation"])
                control = decode_interpretation_response(response, row["user_message"])
                checked = decode_interpretation_response(response, row["user_message"], checked=True)
                self.assertEqual((control.action, control.arguments), (checked.action, checked.arguments))
                self.assertFalse(checked.diagnostics["block_search"])

    def test_raw_spans_quotes_operators_and_word_boundaries(self):
        for text, status, sources in [
            ('„FIT z rybą bez mleka deser” «obiad»', "no_supported_cues", []),
            ("McDonald's deser", "inconsistent", ["deser"]),
            ("obiadowy lunchbox outfit", "no_supported_cues", []),
            ("BEZ\n\tMIE\u0328SA", "inconsistent", ["BEZ\n\tMIE\u0328SA"]),
            ("Nie chcę deseru", "unresolved", ["Nie chcę deseru"]),
            ("zamiast z rybą", "unresolved", ["zamiast z rybą"]),
            ("bez fit", "unresolved", ["bez fit"]),
            ("obiad lub deser", "unresolved", ["obiad lub deser"]),
            ("keto albo fit", "unresolved", ["keto albo fit"]),
            ("Nie, deser; zamiast. Fit", "inconsistent", ["deser", "Fit"]),
            ("nie muszą być bez mleka oraz bez ryb", "inconsistent", ["nie muszą być bez mleka", "bez ryb"]),
            ("nie musi być z rybą, z mięsem", "inconsistent", ["nie musi być z rybą", "z mięsem"]),
        ]:
            with self.subTest(text=text):
                result = decode_interpretation_response(ir_reply(), text, checked=True)
                self.assertEqual(result.diagnostics["completeness_status"], status)
                self.assertEqual([f["source"] for f in result.diagnostics["findings"]], sources)
                if status == "unresolved":
                    self.assertTrue(all(f["reason"] == "unresolved_scope" for f in result.diagnostics["findings"]))

    def test_invalid_source_json_or_envelope_never_reach_coverage(self):
        wrong_source = ir_reply(dict(contract_version="IR-1", request_kind="recipe", facts=[
            dict(kind="category", value="lunch", status="required", source="not present")]))
        for response, stage in [(wrong_source, "interpretation"), (ir_reply(raw="{"), "interpretation"),
                                (ir_reply(count=0), "protocol"), (ir_reply(finish="length"), "protocol")]:
            with self.subTest(stage=stage), patch("core.interpretation_adapter.check_completeness") as check:
                result = decode_interpretation_response(response, "Podaj deser", checked=True)
                self.assertEqual(result.diagnostics["failure_stage"], stage)
                self.assertEqual(result.diagnostics["protocol_valid"], stage != "protocol")
                self.assertEqual(result.diagnostics["completeness_status"], "not_attempted")
                check.assert_not_called()

    def test_checked_mode_shares_request_and_returns_msg06_before_backend(self):
        calls = []
        for mode in ("facts_v1", "facts_checked_v1"):
            client, trace = fake_client(), {}
            with patch("main.run_recommendation_tool", return_value={"query": {}, "recommendations": []}) as lookup:
                reply = main.chat_with_bot("deser", "Winiary", interpretation_mode=mode,
                                           interpretation_client=client, diagnostics=trace)
                client.chat.completions.create.assert_called_once()
                calls.append(client.chat.completions.create.call_args)
                if mode == "facts_v1":
                    lookup.assert_called_once()
                    self.assertNotIn("completeness_status", trace)
                else:
                    lookup.assert_not_called()
                    self.assertEqual(reply, main.INVALID_TOOL_RESPONSE)
                    self.assertEqual(trace["validation_status"], "valid")
                    self.assertTrue(trace["protocol_valid"])
                    self.assertEqual(trace["compiler_action"], "search")
                    self.assertEqual(trace["failure_stage"], "coverage")
                    self.assertEqual(trace["effective_action"], "error")
                    self.assertEqual(trace["backend_calls"], 0)
                    self.assertIsNone(trace["model_decision_correct"])
        self.assertEqual(*calls)

    def test_preflight_priority_and_all_five_t024_releases(self):
        by_text = {r["user_message"]: r["interpretation"] for r in CASES if r["id"] in
                   {"CMC-20", "CMC-21", "CMC-25", "CMC-26"}}
        query = "Bez laktozy i szybki obiad"
        by_text[query] = dict(contract_version="IR-1", request_kind="recipe", facts=[
            dict(kind=kind, value=value, status="required", source=source) for kind, value, source in
            [("exclusion", "lactose", "Bez laktozy"), ("quick", "quick", "szybki"), ("category", "obiad", "obiad")]])
        for text in KNOWN_FALSE_BLOCKS:
            with self.subTest(text=text), patch("main.run_recommendation_tool", return_value={"query": {}, "recommendations": []}) as lookup:
                trace = {}
                main.chat_with_bot(text, "Winiary", interpretation_mode="facts_checked_v1", diagnostics=trace,
                                   interpretation_client=fake_client(ir_reply(by_text[text])))
                lookup.assert_called_once()
                self.assertIsNone(trace["guard"])
                self.assertEqual(trace["completeness_status"], "consistent")
        with patch("main.OpenAI") as create, patch("main.run_recommendation_tool") as lookup:
            reply = main.chat_with_bot("Alergia na mleko, bez jaj", "Winiary", interpretation_mode="facts_checked_v1",
                                       diagnostics=trace)
            self.assertEqual(reply, main.UNSUPPORTED_ALLERGY_RESPONSE)
            self.assertEqual(trace["completeness_status"], "not_attempted")
            self.assertEqual(trace["api_calls"], 0)
            create.assert_not_called()
            lookup.assert_not_called()
