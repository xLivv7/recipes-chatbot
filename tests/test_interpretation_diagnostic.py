"""T027 protocol tests. Every response and error is controlled locally."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import httpx
from openai import APIConnectionError

from evals import run_interpretation_diagnostic as diagnostic


def receipt():
    return dict(status="visible", returned_model="gpt-4o-mini", method="GET", metadata_requests=1,
                generation_requests=0, checked_at_utc=diagnostic.now(), test_only=True)


class InterpretationDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.payloads, cls.schedule, cls.review = diagnostic.build_inputs()
        cls.labels = {case["id"]: case for case in cls.cases}
        cls.queries = {case["user_message"]: case for case in cls.cases}

    @classmethod
    def reply(cls, slot, modifier=None):
        case = cls.labels[slot["id"]]
        if slot["variant"] == "IR1":
            name, args = "submit_recipe_interpretation", deepcopy(case["interpretation"])
        else:
            name, args = "get_recommendations", deepcopy(case["expected"])
            if args and args.get("time_max") is None:
                args.pop("time_max", None)
        if modifier:
            args = modifier(slot, args)
        calls = [] if args is None else [dict(id="call_mock", type="function", function=dict(name=name, arguments=json.dumps(args, ensure_ascii=False)))]
        return dict(model="gpt-4o-mini-2024-07-18", _request_id=f"mock_{slot['attempt']}_{slot['variant']}_{slot['id']}",
            usage=dict(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            choices=[dict(finish_reason="tool_calls" if calls else "stop", message=dict(tool_calls=calls, content="UNTRUSTED_MODEL_TEXT", refusal=None))])

    def rows(self, modifier=None):
        return [diagnostic.observation(slot, self.labels[slot["id"]], self.reply(slot, modifier)) for slot in self.schedule]

    def prepared(self, tmp):
        directory = Path(tmp) / "campaign"
        plan = diagnostic.prepare(directory, receipt())
        return directory, plan, diagnostic.digest(directory / "plan.json")

    def client(self, modifier=None, response_modifier=None):
        index = 0
        def create(**payload):
            nonlocal index
            slot = self.schedule[index]
            self.assertEqual(payload, self.payloads[slot["payload"]])
            response = self.reply(slot, modifier)
            index += 1
            if response_modifier:
                response = response_modifier(slot, response)
            return diagnostic.namespace(response)
        return Mock(chat=Mock(completions=Mock(create=Mock(side_effect=create))))

    def test_plan_preserves_labels_and_has_72_calls_without_doubled_replay_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, _ = self.prepared(tmp)
            diagnostic.validate_frozen(directory)
            self.assertEqual(len(self.cases), 12)
            self.assertEqual(len(self.payloads), 24)
            self.assertEqual(len(self.schedule), 72)
            self.assertEqual([self.schedule[i]["variant"] for i in (0, 12, 24, 36, 48, 60)], ["V4", "IR1", "IR1", "V4", "V4", "IR1"])
            self.assertEqual(plan["planned_api_calls"], 72)
            self.assertEqual(plan["dependent_application_replays"], 72)
            self.assertLess(plan["estimated_reservation_usd"], diagnostic.BUDGET_USD)
            self.assertEqual(diagnostic.read(directory / "state.json")["api_attempts"], 0)
            self.assertFalse(plan["model_quality_measured"])
            for payload in self.payloads.values():
                self.assertEqual(payload["max_completion_tokens"], 1024)
                self.assertEqual(len(payload["messages"]), 2)
                self.assertNotIn("expected", payload)
                self.assertNotIn("interpretation", payload)
            self.assertEqual(self.review["status"], "reviewed_offline")

    def test_preparation_is_offline_and_import_does_not_load_application_sdk_or_database(self):
        script = "import sys; import evals.run_interpretation_diagnostic; assert not any(n in sys.modules for n in ('main','openai','sqlalchemy'))"
        subprocess.run([sys.executable, "-c", script], cwd=diagnostic.ROOT, check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp, patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            directory, _, _ = self.prepared(tmp)
            with self.assertRaises(FileExistsError):
                diagnostic.prepare(directory, receipt())

    def test_missing_or_wrong_approval_cannot_create_a_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved = self.prepared(tmp)
            factory = Mock()
            for hash_value, budget in ((None, None), ("wrong", .5), (approved, .4), (approved, True), (approved, float("nan"))):
                with self.subTest(hash=hash_value, budget=budget), self.assertRaises(ValueError):
                    diagnostic.execute(directory, hash_value, budget, client_factory=factory)
            factory.assert_not_called()

    def test_changed_artifacts_rule_and_copied_source_stop_before_client_creation(self):
        for target in ("payloads.json", "cases.json", "schedule.json", "annotation_review.json", "rule", "source", "runtime", "scope"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                directory, plan, _ = self.prepared(tmp)
                if target in ("rule", "runtime", "scope"):
                    plan[{"rule": "rule", "runtime": "runtime_versions", "scope": "source_hashes"}[target]] = {}
                    diagnostic.save(directory / "plan.json", plan)
                elif target == "source":
                    (directory / "frozen_inputs/core/interpretation_compiler.py").write_text("changed", encoding="utf-8")
                else:
                    diagnostic.save(directory / target, [])
                factory = Mock()
                with self.assertRaises(ValueError):
                    diagnostic.execute(directory, diagnostic.digest(directory / "plan.json"), .5, client_factory=factory)
                factory.assert_not_called()

    def test_rehashed_payload_tampering_does_not_bypass_semantic_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, _ = self.prepared(tmp)
            payloads = diagnostic.read(directory / "payloads.json")
            payloads[next(iter(payloads))]["messages"][1]["content"] = "changed"
            diagnostic.save(directory / "payloads.json", payloads)
            plan["artifact_hashes"]["payloads.json"] = diagnostic.digest(directory / "payloads.json")
            diagnostic.save(directory / "plan.json", plan)
            with self.assertRaisesRegex(ValueError, "semantics changed"):
                diagnostic.validate_frozen(directory)

    def test_full_mock_measurement_uses_one_reserved_call_and_no_live_or_catalog_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, approved = self.prepared(tmp)
            client = self.client()
            original = client.chat.completions.create.side_effect
            def reserved(**payload):
                state = diagnostic.read(directory / "state.json")
                self.assertEqual(state["reserved_requests"], state["api_attempts"] + 1)
                self.assertGreater(state["reserved_usd"], 0)
                return original(**payload)
            client.chat.completions.create.side_effect = reserved
            factory = Mock(return_value=client)
            report = diagnostic.execute(directory, approved, .5, client_factory=factory)
            factory.assert_called_once_with(**diagnostic.CLIENT_CONFIGURATION)
            client.chat.completions.create.assert_called()
            self.assertEqual(client.chat.completions.create.call_count, 72)
            client.close.assert_called_once()
            state = diagnostic.read(directory / "state.json")
            self.assertEqual(state["status"], "complete")
            self.assertEqual(state["api_attempts"], 72)
            self.assertEqual(state["responses_received"], 72)
            self.assertAlmostEqual(state["reserved_usd"], plan["estimated_reservation_usd"])
            self.assertEqual(report["execution_kind"], "mock")
            self.assertFalse(report["is_model_measurement"])
            self.assertEqual(report["actual_model_requests"], 0)
            self.assertFalse(report["candidate_qualifies"])  # A perfect tie does not demonstrate improvement.
            self.assertEqual(report["actual_backend_calls"], 0)
            self.assertTrue(all(row["application_replay"]["real_api_calls"] == 0 for row in diagnostic.read(directory / "results.json")["results"]))

    def test_api_error_stops_after_one_attempt_without_exposing_exception_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved = self.prepared(tmp)
            client = self.client()
            client.chat.completions.create.side_effect = APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"), message="PRIVATE_ERROR")
            with self.assertRaises(diagnostic.CampaignStopped):
                diagnostic.execute(directory, approved, .5, client_factory=Mock(return_value=client))
            client.chat.completions.create.assert_called_once()
            self.assertEqual(diagnostic.read(directory / "state.json")["status"], "incomplete")
            self.assertNotIn("PRIVATE_ERROR", (directory / "results.json").read_text(encoding="utf-8"))

    def test_T022_metadata_failures_stop_both_arms_without_retry(self):
        for arm in ("V4", "IR1"):
            for failure in ("length", "content_filter", "refusal", "empty"):
                def modify(slot, response):
                    if slot["variant"] == arm:
                        if failure == "empty":
                            response["choices"] = []
                        elif failure == "refusal":
                            response["choices"][0]["message"]["refusal"] = "PRIVATE_REFUSAL"
                        else:
                            response["choices"][0]["finish_reason"] = failure
                    return response
                with self.subTest(arm=arm, failure=failure), tempfile.TemporaryDirectory() as tmp:
                    directory, _, approved = self.prepared(tmp)
                    client = self.client(response_modifier=modify)
                    with self.assertRaises(diagnostic.CampaignStopped):
                        diagnostic.execute(directory, approved, .5, client_factory=Mock(return_value=client))
                    self.assertEqual(client.chat.completions.create.call_count, 1 if arm == "V4" else 13)

    def test_invalid_IR_call_is_a_failed_observation_and_does_not_stop_remaining_trials(self):
        def modify(slot, response):
            if slot["variant"] == "IR1" and slot["id"] == "intent_004":
                response["choices"][0]["message"]["tool_calls"] = []
            return response
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved = self.prepared(tmp)
            client = self.client(response_modifier=modify)
            report = diagnostic.execute(directory, approved, .5, client_factory=Mock(return_value=client))
            self.assertEqual(client.chat.completions.create.call_count, 72)
            self.assertEqual(report["variants"]["IR1"]["raw"]["per_case"]["intent_004"], 0)
            self.assertFalse(report["conditions"]["no_IR_protocol_or_validation_errors"])
            self.assertFalse(report["candidate_qualifies"])

    def test_omitted_facts_keep_semantic_failure_and_no_search_has_no_field_scores(self):
        slot = next(s for s in self.schedule if s["variant"] == "IR1" and s["id"] == "intent_004")
        def omitted(slot, args):
            args["facts"] = []
            return args
        row = diagnostic.observation(slot, self.labels[slot["id"]], self.reply(slot, omitted))
        self.assertEqual(row["raw"]["failure_stage"], "semantics")
        self.assertFalse(row["facts"]["signature_exact"])
        self.assertEqual(len(row["facts"]["missing"]), 2)
        def no_search(slot, args):
            args["request_kind"] = "other"
            args["facts"] = []
            return args
        row = diagnostic.observation(slot, self.labels[slot["id"]], self.reply(slot, no_search))
        self.assertEqual(row["raw"]["failure_stage"], "decision")
        self.assertTrue(all(value is None for value in row["raw"]["field_results"].values()))

    def test_invalid_source_is_a_validation_failure_without_defaults_or_dispatch(self):
        def modify(slot, args):
            if slot["variant"] == "IR1" and slot["id"] == "intent_004":
                args["facts"][0]["source"] = "NOT_IN_CONTROLLED_QUERY"
            return args
        report = diagnostic.comparison(self.rows(modify), self.cases, self.schedule)
        errors = [row for row in report["all_failures"] if row["variant"] == "IR1"]
        self.assertEqual(len(errors), 3)
        self.assertTrue(all(row["raw"]["failure_stage"] == "interpretation" for row in errors))
        self.assertTrue(all(row["raw"]["actual"] is None and row["facts"]["signature_exact"] is None for row in errors))
        self.assertTrue(all(row["application_replay"]["simulated_backend_calls"] == 0 for row in errors))
        self.assertFalse(report["conditions"]["no_IR_protocol_or_validation_errors"])

    def test_fact_scoring_ignores_span_boundaries_and_duplicates_but_counts_wrong_labels(self):
        gold = self.labels["intent_004"]["interpretation"]
        value = deepcopy(gold)
        value["facts"][0]["source"] = "deser bez mięsa"
        value["facts"].append(deepcopy(value["facts"][0]))
        self.assertTrue(diagnostic.fact_score(value, gold)["signature_exact"])
        value["facts"][0]["value"] = "kolacja"
        self.assertFalse(diagnostic.fact_score(value, gold)["signature_exact"])

    def test_IR1_D1_requires_improvement_and_reports_all_regressions(self):
        def weaker_v4(slot, args):
            if slot["variant"] == "V4" and slot["id"] == "intent_004":
                args["diet"] = "none"
            return args
        report = diagnostic.comparison(self.rows(weaker_v4), self.cases, self.schedule)
        self.assertTrue(report["candidate_qualifies"])
        self.assertEqual(len(report["all_failures"]), 3)
        self.assertFalse(report["deployment_allowed"])
        self.assertFalse(diagnostic.comparison(self.rows(), self.cases, self.schedule)["candidate_qualifies"])
        def worse_ir(slot, args):
            if slot["variant"] == "IR1" and slot["id"] == "intent_032":
                args["facts"] = []
            return args
        report = diagnostic.comparison(self.rows(worse_ir), self.cases, self.schedule)
        self.assertIn("intent_032", report["per_case_regressions"])
        self.assertFalse(report["conditions"]["no_incorrect_dispatches"])
        self.assertFalse(report["conditions"]["targets_all"])

    def test_comparison_rejects_incomplete_duplicate_or_edited_success_flags(self):
        rows = self.rows()
        edited = deepcopy(rows)
        edited[0]["raw"]["passed"] = False
        for value in (rows[:-1], rows + rows[:1], [*rows[:-1], rows[0]], list(reversed(rows)), edited):
            with self.assertRaises(ValueError):
                diagnostic.comparison(value, self.cases, self.schedule)

    def test_wrong_resolved_model_stops_before_the_next_request(self):
        def modify(slot, response):
            response["model"] = "unapproved-model"
            return response
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved = self.prepared(tmp)
            client = self.client(response_modifier=modify)
            with self.assertRaisesRegex(diagnostic.CampaignStopped, "resolved_model_mismatch"):
                diagnostic.execute(directory, approved, .5, client_factory=Mock(return_value=client))
            client.chat.completions.create.assert_called_once()

    def test_reservation_write_failure_prevents_the_first_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved = self.prepared(tmp)
            client, original, failed = self.client(), diagnostic.save, False
            def failing(path, value):
                nonlocal failed
                if path.name == "state.json" and value.get("reserved_requests") == 1 and not failed:
                    failed = True
                    raise PermissionError("controlled local failure")
                original(path, value)
            with patch.object(diagnostic, "save", side_effect=failing), self.assertRaises(PermissionError):
                diagnostic.execute(directory, approved, .5, client_factory=Mock(return_value=client))
            client.chat.completions.create.assert_not_called()
            self.assertEqual(diagnostic.read(directory / "state.json")["api_attempts"], 0)

    def test_reservation_limit_stops_before_sending_and_campaign_cannot_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved = self.prepared(tmp)
            client, original, count = self.client(), diagnostic.reservation, 0
            def expensive(payload):
                nonlocal count
                count += 1
                return original(payload) if count <= 72 else .51
            with patch.object(diagnostic, "reservation", side_effect=expensive), self.assertRaisesRegex(diagnostic.CampaignStopped, "reservation_limit"):
                diagnostic.execute(directory, approved, .5, client_factory=Mock(return_value=client))
            client.chat.completions.create.assert_not_called()
            factory = Mock()
            with self.assertRaisesRegex(ValueError, "already started"):
                diagnostic.execute(directory, approved, .5, client_factory=factory)
            factory.assert_not_called()

    def test_model_receipt_requires_fresh_GET_and_expected_model_without_generation(self):
        for changes in (dict(returned_model="other"), dict(generation_requests=1), dict(method="POST"),
                        dict(checked_at_utc=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat())):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                diagnostic.validate_access(dict(receipt(), **changes))

    def test_replay_matches_actual_application_guards_validation_and_dispatch(self):
        import main
        for slot in self.schedule[:24]:
            case = self.labels[slot["id"]]
            response = diagnostic.namespace(self.reply(slot))
            row = diagnostic.observation(slot, case, self.reply(slot))
            fake = Mock(chat=Mock(completions=Mock(create=Mock(return_value=response))))
            kwargs = dict(interpretation_mode="facts_v1", interpretation_client=fake) if slot["variant"] == "IR1" else {}
            with self.subTest(id=slot["id"], variant=slot["variant"]), patch.object(main, "client", fake), patch.object(main, "build_system_prompt", return_value=self.payloads[slot["payload"]]["messages"][0]["content"]), patch.object(main, "run_recommendation_tool", return_value={"query": {}, "recommendations": []}) as backend:
                result = main.chat_with_bot(case["user_message"], "Winiary", **kwargs)
                self.assertEqual(backend.call_count, row["application_replay"]["simulated_backend_calls"])
                self.assertEqual(fake.chat.completions.create.call_count, 0 if row["application_replay"]["guard"] else 1)
                if backend.call_count:
                    self.assertEqual(diagnostic.canonical_args(backend.call_args.args[0]), diagnostic.canonical_args(row["application_replay"]["actual"]))
                elif row["application_replay"]["guard"]:
                    self.assertEqual(result, main.UNSUPPORTED_EXCLUSION_RESPONSE)
                else:
                    self.assertEqual(result, main.NO_TOOL_RESPONSE)


if __name__ == "__main__":
    unittest.main()
