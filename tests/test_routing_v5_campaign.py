"""T023 instrumentation tests. Every model response is controlled locally."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import tempfile
import unittest
from unittest.mock import Mock, patch

import httpx
from openai import APIConnectionError

import main as application
from evals.prepare_routing_v5 import build_preparation, wire_args
from evals.run_routing_eval import evaluate_case
from evals.run_routing_v5 import (BudgetedClient, CampaignStopped, comparison, digest, execute,
                                 prepare, read_json, save, validate_frozen, audit_guards)

MODEL_ACCESS = dict(status="visible", returned_model="gpt-4o-mini", method="GET",
                    generation_requests=0, metadata_requests=1, test_only=True)


class RoutingV5CampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, _, cls.prompts, cls.cases, _ = build_preparation()
        cls.by_query = {case["user_message"]: case for case in cls.cases}
        cls.rows = []
        for attempt, variant, mode in cls.base["schedule"]:
            client = cls.client(False)
            for case in cls.cases:
                cls.rows.append(dict(evaluate_case(case, mode, client, system_prompt=cls.prompts[variant]),
                                     attempt=attempt, variant=variant, mode=mode))

    @classmethod
    def reply(cls, kwargs, wrong_v4=False):
        case = cls.by_query[kwargs["messages"][1]["content"]]
        args = deepcopy(case.get("expected"))
        if args is not None and wrong_v4 and kwargs["messages"][0]["content"] == cls.prompts["V4"] and case["id"] == "intent_032":
            args["protein_preference"] = "fish"
        calls = [] if args is None else [NS(function=NS(name="get_recommendations", arguments=json.dumps(wire_args(args))))]
        return NS(model="gpt-4o-mini-2024-07-18", _request_id="controlled-test-request",
                  usage=NS(prompt_tokens=100, completion_tokens=50, total_tokens=150),
                  choices=[NS(finish_reason="tool_calls" if calls else "stop",
                              message=NS(tool_calls=calls, content=None, refusal=None))])

    @classmethod
    def client(cls, wrong_v4):
        return NS(chat=NS(completions=NS(create=Mock(side_effect=lambda **kw: cls.reply(kw, wrong_v4)))))

    def prepared(self, tmp):
        directory = Path(tmp) / "campaign"
        plan = prepare(directory, MODEL_ACCESS)
        return directory, plan, digest(directory / "plan.json")

    def winning_rows(self):
        rows = deepcopy(self.rows)
        for row in rows:
            if row["variant"] == "V4" and row["id"] == "intent_032":
                row["actual"]["protein_preference"] = "fish"
                row["field_results"]["protein_preference"] = False
                row.update(passed=False, semantics_correct=False, failure_stage="semantics")
        return rows

    @staticmethod
    def drop_tool(row):
        row.update(model_action="no_tool", effective_action="no_tool", tool_call_count=0,
                   raw_tool_calls=[], actual=None, arguments_valid=None, semantics_correct=None,
                   passed=False, failure_stage="decision", model_decision_correct=False,
                   decision_correct=False, backend_calls=0,
                   field_results={field: None for field in row["field_results"]})

    def test_prepare_freezes_payloads_schedule_and_post_T022_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, _ = self.prepared(tmp)
            validate_frozen(directory)
            self.assertEqual((plan["planned_evaluations"], plan["planned_api_calls"]), (384, 354))
            self.assertLess(plan["estimated_reservation_usd"], plan["budget_guard_usd"])
            self.assertIn("core/llm_response_validation.py", plan["source_hashes"])
            self.assertEqual(len(read_json(directory / "payloads.json")), 64)
            self.assertEqual(read_json(directory / "state.json")["actual_api_calls"], 0)
            self.assertTrue(plan["execution_requires_explicit_approval"])
            self.assertTrue(read_json(directory / "manifest.json")["application_status"]["T022_marked_complete"])
            for payload in read_json(directory / "payloads.json").values():
                self.assertEqual(len(payload["messages"]), 2)
                self.assertNotIn("expected", payload)
                self.assertNotIn("rules", payload)

    def test_missing_or_wrong_approval_cannot_construct_a_client(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved_hash = self.prepared(tmp)
            factory = Mock()
            for value, budget in ((None, None), ("wrong", 1.0), (approved_hash, .5),
                                  (approved_hash, 1.1), (approved_hash, True)):
                with self.subTest(hash=value, budget=budget), self.assertRaises(ValueError):
                    execute(directory, value, budget, client_factory=factory)
            factory.assert_not_called()
            self.assertEqual(read_json(directory / "state.json")["status"], "prepared")

    def test_changed_payload_or_labels_are_rejected_before_client_creation(self):
        for name in ("payloads.json", "cases.json"):
            with self.subTest(file=name), tempfile.TemporaryDirectory() as tmp:
                directory, _, approved_hash = self.prepared(tmp)
                (directory / name).write_text("[]", encoding="utf-8")
                factory = Mock()
                with self.assertRaisesRegex(ValueError, "artifact changed"):
                    execute(directory, approved_hash, 1.0, client_factory=factory)
                factory.assert_not_called()

    def test_changed_frozen_source_or_rule_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, _ = self.prepared(tmp)
            plan["rule"]["target_successes"] = 1
            save(directory / "plan.json", plan)
            with self.assertRaisesRegex(ValueError, "rule"):
                validate_frozen(directory)
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, _ = self.prepared(tmp)
            (directory / "frozen_inputs/main.py").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source changed"):
                validate_frozen(directory)

    def test_existing_campaign_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, original_hash = self.prepared(tmp)
            with self.assertRaises(FileExistsError):
                prepare(directory, MODEL_ACCESS)
            self.assertEqual(digest(directory / "plan.json"), original_hash)

    def test_full_mock_campaign_uses_exact_prompts_and_restores_active_application(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved_hash = self.prepared(tmp)
            original = application.build_system_prompt
            factory = Mock(return_value=self.client(True))
            result = execute(directory, approved_hash, 1.0, client_factory=factory)
            self.assertIs(application.build_system_prompt, original)
            factory.assert_called_once_with(base_url="https://api.openai.com/v1", max_retries=0, timeout=30)
            self.assertEqual(result["candidate"], "V5")
            self.assertTrue(all(result["conditions"].values()))
            self.assertFalse(result["is_model_measurement"])
            self.assertEqual(result["execution_kind"], "mock")
            self.assertEqual(len(result["guard_audit"]), 5)
            self.assertTrue(all(not row["passed"] and row["api_calls"] == row["backend_calls"] == 0 for row in result["guard_audit"]))
            self.assertTrue(all(row["preflight_passed"] and row["passed"] is None
                                and row["model_decision_correct"] is None for row in result["guard_audit"]))
            state = read_json(directory / "state.json")
            self.assertEqual((state["actual_api_calls"], state["completed_evaluations"]), (354, 384))
            self.assertEqual(len(state["reservations"]), 354)
            self.assertEqual(len(list((directory / "groups").glob("*.json"))), 12)
            self.assertEqual(state["status"], "complete")
            self.assertEqual(state["approved_plan_sha256"], approved_hash)
            with self.assertRaisesRegex(ValueError, "already started"):
                execute(directory, approved_hash, 1.0, client_factory=Mock())

    def test_reservation_is_saved_before_an_api_error_and_campaign_cannot_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved_hash = self.prepared(tmp)
            def fail(**kwargs):
                state = read_json(directory / "state.json")
                self.assertEqual(state["actual_api_calls"], 1)
                self.assertGreater(state["reserved_usd"], 0)
                raise APIConnectionError(request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"), message="PRIVATE_ERROR_TEXT")
            factory = Mock(return_value=NS(chat=NS(completions=NS(create=Mock(side_effect=fail)))))
            with self.assertRaisesRegex(CampaignStopped, "api_error"):
                execute(directory, approved_hash, 1.0, client_factory=factory)
            state = read_json(directory / "state.json")
            self.assertEqual(state["status"], "incomplete")
            self.assertEqual(state["actual_api_calls"], 1)
            self.assertEqual(len(read_json(directory / "results.json")["results"]), 1)
            self.assertFalse(read_json(directory / "results.json")["complete"])
            self.assertFalse((directory / "comparison.json").exists())
            self.assertNotIn("PRIVATE_ERROR_TEXT", (directory / "results.json").read_text(encoding="utf-8"))
            with self.assertRaisesRegex(ValueError, "already started"):
                execute(directory, approved_hash, 1.0, client_factory=Mock())

    def test_completion_failures_stop_after_one_reserved_request(self):
        for finish, refusal in (("length", None), ("content_filter", None), ("stop", "CONTROLLED_REFUSAL")):
            with self.subTest(finish=finish), tempfile.TemporaryDirectory() as tmp:
                directory, _, approved_hash = self.prepared(tmp)
                def reply(**kwargs):
                    value = self.reply(kwargs)
                    value.choices[0].finish_reason = finish
                    value.choices[0].message.refusal = refusal
                    return value
                factory = Mock(return_value=NS(chat=NS(completions=NS(create=Mock(side_effect=reply)))))
                with self.assertRaises(CampaignStopped):
                    execute(directory, approved_hash, 1.0, client_factory=factory)
                self.assertEqual(read_json(directory / "state.json")["actual_api_calls"], 1)
                row = read_json(directory / "results.json")["results"][0]
                self.assertEqual(row["failure_stage"], "protocol")
                self.assertEqual(row["backend_calls"], 0)

    def test_payload_call_and_reservation_limits_prevent_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, _ = self.prepared(tmp)
            payloads, schedule = read_json(directory / "payloads.json"), read_json(directory / "schedule.json")
            state = read_json(directory / "state.json")
            client = self.client(False)
            wrapped = BudgetedClient(client, directory, plan, state, payloads, schedule)
            payload = deepcopy(payloads[schedule[0]["payload"]])
            changed = deepcopy(payload)
            changed["messages"][1]["content"] = "UNAPPROVED_QUERY"
            with self.assertRaisesRegex(CampaignStopped, "payload_mismatch"):
                wrapped.create(**changed)
            state["actual_api_calls"] = plan["planned_api_calls"]
            with self.assertRaisesRegex(CampaignStopped, "request_limit"):
                wrapped.create(**payload)
            state.update(actual_api_calls=0, reserved_usd=1.0)
            with self.assertRaisesRegex(CampaignStopped, "reservation_limit"):
                wrapped.create(**payload)
            client.chat.completions.create.assert_not_called()

    def test_incomplete_duplicate_or_relabelled_observations_cannot_qualify(self):
        changed_label = deepcopy(self.rows)
        changed_label[0]["user_message"] = "CHANGED_QUERY"
        changed_version = deepcopy(self.rows)
        changed_version[0]["response_validation_version"] = "old"
        for rows in (self.rows[:-1], self.rows + [self.rows[0]], changed_label, changed_version):
            with self.assertRaises(ValueError):
                comparison(rows, self.base, self.cases)

    def test_tie_preserves_active_V0_without_claiming_prompt_improvement(self):
        result = comparison(deepcopy(self.rows), self.base, self.cases)
        self.assertTrue(result["valid_comparison"])
        self.assertIsNone(result["candidate"])
        self.assertFalse(result["conditions"]["fish_errors_decrease"])
        self.assertEqual(result["keep_active_prompt"], "V0")

    def test_one_trial_regression_is_rejected_despite_high_aggregate_accuracy(self):
        rows = self.winning_rows()
        row = next(r for r in rows if r["variant"] == "V5" and r["mode"] == "application" and r["id"] == "intent_013")
        self.drop_tool(row)
        result = comparison(rows, self.base, self.cases)
        self.assertTrue(result["conditions"]["application_accuracy"])
        self.assertFalse(result["conditions"]["no_case_regression"])
        self.assertIsNone(result["candidate"])

    def test_losing_explicit_fish_is_not_a_fix_for_unrequested_fish(self):
        rows = self.winning_rows()
        row = next(r for r in rows if r["variant"] == "V5" and r["mode"] == "raw" and r["id"] == "intent_010")
        self.drop_tool(row)
        result = comparison(rows, self.base, self.cases)
        self.assertFalse(result["conditions"]["targets_all"])
        self.assertFalse(result["conditions"]["no_fish_loss_increase"])
        self.assertIsNone(result["candidate"])

    def test_structurally_valid_wrong_semantics_reaching_backend_disqualify_candidate(self):
        rows = self.winning_rows()
        row = next(r for r in rows if r["variant"] == "V5" and r["mode"] == "application" and r["id"] == "intent_003")
        row["actual"]["protein_preference"] = "fish"
        row["field_results"]["protein_preference"] = False
        row.update(semantics_correct=False, passed=False, failure_stage="semantics")
        result = comparison(rows, self.base, self.cases)
        self.assertFalse(result["conditions"]["no_semantic_dispatch"])
        self.assertEqual(result["semantic_dispatch_errors"]["V5"][0]["id"], "intent_003")
        self.assertIsNone(result["candidate"])

    def test_raw_boundary_failure_is_visible_when_application_guard_blocks_it(self):
        rows = self.winning_rows()
        row = next(r for r in rows if r["variant"] == "V5" and r["mode"] == "raw" and r["id"] == "routing_004")
        row.update(model_action="tool", effective_action="tool", actual=wire_args(self.cases[0]["expected"]),
                   passed=False, failure_stage="decision", decision_correct=False)
        result = comparison(rows, self.base, self.cases)
        self.assertFalse(result["conditions"]["no_tool_all"])
        self.assertEqual(result["variants"]["V5"]["application"]["no_tool"]["passed"], 21)
        self.assertIsNone(result["candidate"])

    def test_mixed_models_or_technical_failures_invalidate_comparison(self):
        for kind in ("model", "api", "truncation"):
            rows = self.winning_rows()
            row = next(r for r in rows if r["api_calls"])
            if kind == "model":
                row["response_model"] = "other-model"
            elif kind == "api":
                row.update(failure_stage="api", passed=False, response_model=None)
            else:
                row.update(failure_stage="protocol", passed=False, response_failure_reason="truncated_response")
            with self.subTest(kind=kind):
                result = comparison(rows, self.base, self.cases)
                self.assertFalse(result["valid_comparison"])
                self.assertIsNone(result["candidate"])

    def test_transient_windows_lock_preserves_old_checkpoint_until_atomic_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            save(path, dict(status="old"))
            original = Path.replace
            observed = []

            def locked_once(source, destination):
                observed.append(read_json(destination))
                if len(observed) == 1:
                    raise PermissionError("controlled sharing violation")
                return original(source, destination)

            with patch.object(Path, "replace", new=locked_once), patch("evals.run_routing_v5.time.sleep"):
                save(path, dict(status="new"))
            self.assertEqual(observed, [dict(status="old"), dict(status="old")])
            self.assertEqual(read_json(path), dict(status="new"))
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_persistent_checkpoint_lock_is_bounded_and_preserves_last_committed_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            save(path, dict(status="old"))
            with patch.object(Path, "replace", side_effect=PermissionError("controlled lock")) as replace:
                with patch("evals.run_routing_v5.time.sleep") as sleep, self.assertRaises(PermissionError):
                    save(path, dict(status="new"))
            self.assertLessEqual(replace.call_count, 6)
            self.assertLessEqual(sum(call.args[0] for call in sleep.call_args_list), 1.55)
            self.assertEqual(read_json(path), dict(status="old"))

    def test_failed_reservation_commit_cannot_reach_model_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory, plan, _ = self.prepared(tmp)
            state = read_json(directory / "state.json")
            payloads = read_json(directory / "payloads.json")
            schedule = read_json(directory / "schedule.json")
            client = self.client(False)
            budgeted = BudgetedClient(client, directory, plan, state, payloads, schedule)
            first = next(slot for slot in schedule if slot["requires_api"])
            with patch.object(Path, "replace", side_effect=PermissionError("controlled lock")):
                with patch("evals.run_routing_v5.time.sleep"), self.assertRaises(PermissionError):
                    budgeted.create(**deepcopy(payloads[first["payload"]]))
            client.chat.completions.create.assert_not_called()
            self.assertEqual(read_json(directory / "state.json")["actual_api_calls"], 0)

    def test_preflight_audit_distinguishes_a_remaining_false_block_from_a_released_probe(self):
        blocked = dict(id="remaining_false_block", user_message="Nie wymagam dania bez orzechów",
                       expected_action="tool", preflight_blocked=True)
        released = dict(id="released", user_message="Bez laktozy i szybki obiad",
                        expected_action="tool", preflight_blocked=False)
        results = audit_guards([blocked, released])
        self.assertFalse(results[0]["preflight_passed"])
        self.assertFalse(results[0]["passed"])
        self.assertEqual(results[0]["failure_stage"], "preflight")
        self.assertTrue(results[1]["preflight_passed"])
        self.assertIsNone(results[1]["passed"])
        self.assertIsNone(results[1]["model_decision_correct"])
        self.assertTrue(all(row["api_calls"] == row["backend_calls"] == 0 for row in results))

    def test_changed_frozen_preflight_snapshot_stops_before_paid_client_creation(self):
        from evals.prepare_routing_v5 import guard as current_guard
        with tempfile.TemporaryDirectory() as tmp:
            directory, _, approved_hash = self.prepared(tmp)
            factory = Mock()
            audit_ids = {row["id"] for row in read_json(directory / "guard_audit.json")}
            def changed_guard(probe):
                return True if probe["id"] in audit_ids else current_guard(probe)
            with patch("evals.run_routing_v5.guard", side_effect=changed_guard), self.assertRaisesRegex(CampaignStopped, "guard_audit_changed"):
                execute(directory, approved_hash, 1.0, client_factory=factory)
            factory.assert_not_called()
            self.assertEqual(read_json(directory / "state.json")["actual_api_calls"], 0)


if __name__ == "__main__":
    unittest.main()
