import argparse
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from evals.run_llm_eval import load_cases
from evals.run_routing_eval import (DEFAULT_CASES_PATH, DEFAULT_ROUTING_CASES_PATH,
                                   GUARD_CASES_PATH, HOLDOUT_CASES_PATH, run_eval, summarize)
from test_separated_routing_eval import case, evaluate_case, response


class RoutingRepeatsHoldoutTests(unittest.TestCase):
    def args(self, **changes):
        values = dict(cases=DEFAULT_CASES_PATH, routing_cases=DEFAULT_ROUTING_CASES_PATH,
                      guard_cases=GUARD_CASES_PATH, limit=None, mode="raw", model="gpt-4o-mini",
                      brand_name="Winiary", dry_run=True, repeats=3, holdout=False, output=None)
        return argparse.Namespace(**dict(values, **changes))

    def test_holdout_is_separate_and_has_valid_fixed_labels(self):
        holdout = load_cases(HOLDOUT_CASES_PATH)
        self.assertEqual(len(holdout), 24)
        development = [case for path in (DEFAULT_CASES_PATH, DEFAULT_ROUTING_CASES_PATH,
                       GUARD_CASES_PATH, DEFAULT_CASES_PATH.with_name("time_goal_cases.json")) for case in load_cases(path)]
        self.assertTrue({c["id"] for c in holdout}.isdisjoint(c["id"] for c in development))
        self.assertTrue({c["user_message"] for c in holdout}.isdisjoint(c["user_message"] for c in development))
        self.assertEqual(sum(c["expected_action"] == "tool" for c in holdout), 16)

    def test_dry_run_counts_all_repeats_and_isolates_holdout(self):
        for holdout, mode, total, calls in ((False, "raw", 228, 228), (False, "application", 228, 198),
                                             (True, "raw", 72, 72), (True, "application", 72, 54)):
            with self.subTest(holdout=holdout, mode=mode), patch("evals.run_routing_eval.OpenAI") as api:
                report = run_eval(self.args(holdout=holdout, mode=mode))
                self.assertEqual(report["summary"], {"total": total, "planned_api_calls": calls})
                self.assertEqual(len(report["dataset_files"]), 1 if holdout else 3)
                api.assert_not_called()

    def test_stability_separates_stable_intermittent_and_persistent(self):
        client = Mock()
        client.chat.completions.create.return_value = response()
        base = evaluate_case(case(), "raw", client)
        rows = []
        for case_id, outcomes in (("stable", [True, True, True]), ("mixed", [False, True, True]),
                                  ("persistent", [False, False, False])):
            for attempt, success in enumerate(outcomes, 1):
                rows.append(dict(deepcopy(base), id=case_id, attempt=attempt, passed=success,
                                 failure_stage=None if success else "semantics"))
        summary = summarize(rows)
        self.assertEqual(summary["stable_cases"], 1)
        self.assertEqual(summary["case_stability"]["mixed"]["failure_type"], "intermittent")
        self.assertEqual(summary["case_stability"]["persistent"]["failure_type"], "persistent")
        self.assertEqual(summary["attempts"]["1"], {"passed": 1, "total": 3})

    def test_live_loop_uses_repeats_and_writes_incomplete_checkpoint(self):
        client = Mock()
        client.chat.completions.create.return_value = response()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            checkpoints = []
            def next_response(**kwargs):
                if output.exists():
                    checkpoints.append(json.loads(output.read_text(encoding="utf-8"))["complete"])
                return response()
            client.chat.completions.create.side_effect = next_response
            args = self.args(limit=1, dry_run=False, output=output)
            with patch("evals.run_routing_eval.OpenAI", return_value=client):
                report = run_eval(args)
            self.assertEqual(client.chat.completions.create.call_count, 3)
            self.assertEqual([r["attempt"] for r in report["results"]], [1, 2, 3])
            self.assertTrue(report["complete"])
            self.assertEqual(checkpoints, [False, False])
            self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["complete"])

    def test_nonpositive_repeat_count_is_rejected(self):
        with self.assertRaises(ValueError):
            run_eval(self.args(repeats=0))
