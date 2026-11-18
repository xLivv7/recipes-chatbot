import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from evals.prepare_interpretation_v1 import ROOT, prepare, validate_preparation


class InterpretationPreparationTests(unittest.TestCase):
    def test_preparation_needs_no_network_credentials_or_catalog(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"OPENAI_API_KEY": "unused", "DATABASE_URL": "unused"}):
            with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
                directory = Path(tmp) / "candidate"
                manifest = prepare(directory)
                self.assertFalse(manifest["execution_enabled"])
                self.assertTrue(manifest["not_a_campaign_plan"])
                self.assertIsNone(manifest["approved_budget_usd"])
                self.assertEqual(manifest["actual_api_calls"], 0)
                self.assertEqual(manifest["active_mode"], "legacy")
                validate_preparation(directory)
                request = json.loads((directory / "request_template.json").read_text(encoding="utf-8"))
                self.assertEqual(request["messages"][1]["content"], "CONTROLLED_QUERY_PLACEHOLDER")
                self.assertEqual(request["max_completion_tokens"], 1024)
                self.assertNotIn("expected", request)

    def test_existing_candidate_is_not_overwritten_and_changed_assets_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "candidate"
            prepare(directory)
            with self.assertRaises(FileExistsError):
                prepare(directory)
            (directory / "IR1.txt").write_text("changed", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_preparation(directory)

    def test_preparer_import_does_not_import_sdk_application_or_database(self):
        script = "import sys; import evals.prepare_interpretation_v1; assert not any(n in sys.modules for n in ('openai','main','sqlalchemy'))"
        subprocess.run([sys.executable, "-c", script], cwd=ROOT, check=True, capture_output=True)

    def test_manifest_cannot_drop_sources_or_claim_execution_or_measurement(self):
        for field, value in (("source_hashes", {}), ("execution_enabled", True), ("model_quality_measured", True)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp) / "candidate"
                prepare(directory)
                path = directory / "manifest.json"
                manifest = json.loads(path.read_text(encoding="utf-8"))
                manifest[field] = value
                path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises(ValueError):
                    validate_preparation(directory)


if __name__ == "__main__":
    unittest.main()
