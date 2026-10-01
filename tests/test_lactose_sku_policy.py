import csv
from datetime import date
from pathlib import Path
import unittest


class LactoseSkuPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1] / "curation"
        with (cls.root / "winiary_sku_lactose_policy.csv").open(encoding="utf-8", newline="") as source:
            cls.rows = list(csv.DictReader(source))
        cls.by_id = {row["client_sku_id"]: row for row in cls.rows}

    def test_policy_covers_existing_sku_catalog_without_duplicates(self):
        with (self.root / "winiary_sku_gluten_policy.csv").open(encoding="utf-8", newline="") as source:
            expected = {row["client_sku_id"] for row in csv.DictReader(source)}
        self.assertEqual(len(self.rows), len(self.by_id))
        self.assertEqual(set(self.by_id), expected)

    def test_decisions_have_sources_dates_and_pending_actions(self):
        for row in self.rows:
            with self.subTest(sku=row["client_sku_id"]):
                self.assertIn(row["is_lactose_free"], ("", "0", "1"))
                self.assertTrue(row["reason"].strip())
                self.assertTrue(row["source_url"].strip())
                date.fromisoformat(row["reviewed_at"])
                if row["is_lactose_free"] == "1":
                    self.assertTrue(row["source_url"].startswith("https://www.winiary.pl/"))
                    self.assertEqual(row["manual_review_action"], "")
                elif not row["is_lactose_free"]:
                    self.assertTrue(row["manual_review_action"].strip())

    def test_milk_trace_declarations_do_not_become_confirmed_exclusions(self):
        for sku in ("BULION_DROBIOWY_160G", "BULION_WARZYWNY_SLOIK_160G", "BULION_GRZYBOWY_6KOSTEK_60G"):
            self.assertEqual(self.by_id["WINIARY_" + sku]["is_lactose_free"], "")

    def test_new_packaging_does_not_approve_old_variants(self):
        for sku in ("KETCHUP_PIKANTNY_560G", "KETCHUP_BEZ_CUKRU_410G", "SOS_AMERYKANSKI_BBQ_348G", "SOS_CZOSNKOWY_BUTELKA_300ML"):
            self.assertEqual(self.by_id["WINIARY_" + sku]["is_lactose_free"], "")

    def test_verified_compositions_are_explicitly_allowed(self):
        for sku in ("MAJONEZ_DEKORACYJNY_250ML", "MAJONEZ_LEKKI_300ML", "MAJONEZ_WEGANSKI_300ML", "BULION_WOLOWY_160G"):
            self.assertEqual(self.by_id["WINIARY_" + sku]["is_lactose_free"], "1")
