import csv
from pathlib import Path
import unittest


class LactoseConceptPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "curation" / "lactose_concept_policy.csv"
        with path.open(encoding="utf-8", newline="") as source:
            cls.rows = list(csv.DictReader(source))

    def test_reviewed_catalog_has_one_explicit_row_per_concept(self):
        ids = [row["concept_id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {f"C{i:03d}" for i in range(1, 377)})

    def test_status_and_review_metadata_are_valid(self):
        for row in self.rows:
            with self.subTest(concept=row["concept_id"]):
                self.assertIn(row["is_lactose_free"], ("", "0", "1"))
                for field in ("name_pl", "reason", "source", "reviewed_at"):
                    self.assertTrue(row[field].strip())
                if not row["is_lactose_free"]:
                    self.assertTrue(row["manual_review_action"].strip())

    def test_clear_and_uncertain_cases_keep_distinct_states(self):
        rows = {row["concept_id"]: row for row in self.rows}
        for concept, status in {"C091": "0", "C094": "1", "C104": "", "C108": "", "C004": "", "C329": "", "C340": "0", "C173": "1"}.items():
            self.assertEqual(rows[concept]["is_lactose_free"], status)
