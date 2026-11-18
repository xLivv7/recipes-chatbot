"""Offline preparation boundary; no assertions about model accuracy."""
from copy import deepcopy
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from evals.prepare_routing_v5 import (ROOT, DIAGNOSTICS, LEGACY, RECIPE_TOOLS,
    build_preparation, load_cases, parse_examples, prepare, request,
    validate_prompt, validate_separation)


class RoutingV5PreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v4 = (ROOT / "evals/routing_prompts/V4.txt").read_text(encoding="utf-8")
        cls.v5 = (ROOT / "evals/routing_prompts/V5.txt").read_text(encoding="utf-8")

    def test_preparation_freezes_reviewable_inputs_without_network_or_credentials(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,
                {"OPENAI_API_KEY": "unused-offline", "DATABASE_URL": "unused-offline"}), \
                patch.object(socket, "create_connection", side_effect=AssertionError("No network")), \
                patch.object(socket.socket, "connect", side_effect=AssertionError("No network")):
            directory = Path(tmp) / "preparation"
            manifest, checks = prepare(directory)
            self.assertFalse(manifest["execution_enabled"])
            self.assertIsNone(manifest["approved_budget_usd"])
            self.assertEqual(manifest["actual_api_calls"], 0)
            self.assertEqual(manifest["planned_evaluations"], 384)
            self.assertEqual(manifest["planned_api_calls"], 354)
            self.assertEqual(checks["supported_cases"], 25)
            self.assertEqual((checks["valid_tool_examples"], checks["no_tool_examples"]), (14, 4))
            self.assertEqual(json.loads((directory / "tool_schema.json").read_text(encoding="utf-8")), RECIPE_TOOLS)
            for variant, expected in (("V4", self.v4), ("V5", self.v5)):
                self.assertEqual((directory / f"{variant}.txt").read_text(encoding="utf-8"), expected)
            self.assertEqual((directory / "frozen_inputs/main.py").read_bytes(), (ROOT / "main.py").read_bytes())

    def test_existing_preparation_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "already_exists"
            directory.mkdir()
            marker = directory / "marker.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                prepare(directory)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
            self.assertEqual(list(directory.iterdir()), [marker])

    def test_unapproved_instruction_change_is_rejected(self):
        changed = self.v5.replace("Nie redaguj przepisów", "Redaguj przepisy", 1)
        with self.assertRaisesRegex(ValueError, "outside the approved scope"):
            validate_prompt(self.v4, changed)

    def test_structurally_legal_but_unrequested_fish_breaks_the_contrast(self):
        changed = self.v5.replace('"diet":"pescetarian","protein_preference":"none"',
                                 '"diet":"pescetarian","protein_preference":"fish"', 1)
        with self.assertRaisesRegex(ValueError, "Invalid contrast"):
            validate_prompt(self.v4, changed)

    def test_no_tool_is_not_a_fake_function_with_arguments(self):
        changed = self.v5.replace("Narzędzie: brak wywołania\nArgumenty: nie dotyczy",
                                 "Narzędzie: no_tool\nArgumenty: {}", 1)
        with self.assertRaisesRegex(ValueError, "synthetic no_tool"):
            parse_examples(changed)

    def test_normalized_demonstration_cannot_be_used_as_diagnostic_query(self):
        examples = parse_examples(self.v5)
        cases = load_cases(ROOT / DIAGNOSTICS)
        cases[0]["user_message"] = "  " + examples[0]["query"].upper().rstrip(".") + "!!! "
        with self.assertRaisesRegex(ValueError, "leaked"):
            validate_separation(examples, cases, [])

    def test_duplicate_ids_invalid_arguments_and_refusal_arguments_are_rejected(self):
        original = load_cases(ROOT / DIAGNOSTICS)
        mutations = []
        duplicate = deepcopy(original)
        duplicate[1]["id"] = duplicate[0]["id"]
        mutations.append(duplicate)
        invalid = deepcopy(original)
        invalid[0]["expected"]["nutrition_goal"] = "unknown"
        mutations.append(invalid)
        no_tool = deepcopy(original)
        no_tool[-1]["expected"] = deepcopy(no_tool[0]["expected"])
        mutations.append(no_tool)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            for cases in mutations:
                with self.subTest(case=cases[-1]["id"]):
                    path.write_text(json.dumps(cases), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_cases(path)

    def test_legacy_labels_and_known_false_blocks_are_preserved_in_separate_cohorts(self):
        manifest, checks, _, cases, audit = build_preparation()
        self.assertEqual(cases[:20], load_cases(ROOT / LEGACY))
        self.assertEqual(checks["total_cases"], 32)
        self.assertEqual(len(checks["compatibility_matrix"]), 12)
        self.assertEqual(sum(row["accepted"] for row in checks["compatibility_matrix"]), 7)
        self.assertEqual({row["id"] for row in audit}, {"guard_005", "guard_006", "DP-02", "DP-03", "DP-22"})
        self.assertTrue(all(row.get("expected_action", "tool") == "tool" for row in audit))
        self.assertFalse({row["id"] for row in audit} & {row["id"] for row in cases})
        self.assertEqual(checks["guard_audit_false_blocks"], sum(row["preflight_blocked"] for row in audit))
        self.assertEqual(manifest["schedule"][4], (2, "V5", "raw"))

    def test_request_contains_query_and_common_schema_without_expected_labels(self):
        case = load_cases(ROOT / DIAGNOSTICS)[0]
        payload = request(self.v5, case)
        self.assertEqual(payload["messages"], [{"role": "system", "content": self.v5},
                                              {"role": "user", "content": case["user_message"]}])
        self.assertEqual(payload["tools"], RECIPE_TOOLS)
        self.assertNotIn("expected", payload)
        self.assertNotIn("rules", payload)


if __name__ == "__main__":
    unittest.main()
