import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

import apply_data_curation as curation
from core.database import Client, ClientSku, DietPolicy, Ingredient


class LactoseCurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.concepts = Path(self.directory.name) / "concepts.csv"
        self.skus = Path(self.directory.name) / "skus.csv"

    def write_policy(self, path, id_field, rows):
        with path.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow([id_field, "is_lactose_free"])
            writer.writerows(rows)

    def test_loader_preserves_three_states(self):
        self.write_policy(self.concepts, "concept_id", [("C001", "1"), ("C002", "0"), ("C003", "")])
        self.assertEqual(curation.load_lactose_statuses(self.concepts, "concept_id"),
                         {"C001": 1, "C002": 0, "C003": None})

    def test_loader_rejects_duplicates_invalid_values_and_empty_ids(self):
        for rows in ([("C001", "1"), ("C001", "0")], [("C001", "1.0")], [("", "1")]):
            with self.subTest(rows=rows):
                self.write_policy(self.concepts, "concept_id", rows)
                with self.assertRaises(ValueError):
                    curation.load_lactose_statuses(self.concepts, "concept_id")

    def test_loader_rejects_empty_or_wrong_schema(self):
        for field in ("concept_id", "wrong_id"):
            with self.subTest(field=field):
                self.write_policy(self.concepts, field, [])
                with self.assertRaises(ValueError):
                    curation.load_lactose_statuses(self.concepts, "concept_id")

    def test_id_validation_rejects_missing_and_unknown_records(self):
        for statuses in ({}, {"C001": 1, "C999": 1}):
            with self.subTest(statuses=statuses):
                with self.assertRaises(ValueError):
                    curation.validate_lactose_policy_ids(statuses, {"C001"}, "concept")

    def make_database(self):
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        for model in (Ingredient, Client, DietPolicy, ClientSku):
            model.__table__.create(engine)
        db = Session(engine)
        self.addCleanup(db.close)
        db.add_all([Ingredient(id="C001", name_pl="test"), Client(id=1, name="Winiary"),
                    DietPolicy(ingredient_id="C001", is_gluten_free=1, is_lactose_free=0),
                    ClientSku(id="SKU", client_id=1, concept_id="C001", is_gluten_free=0,
                              is_lactose_free=1)])
        db.commit()
        return db

    def test_import_is_idempotent_preserves_null_and_other_flags(self):
        db = self.make_database()
        self.write_policy(self.concepts, "concept_id", [("C001", "1")])
        self.write_policy(self.skus, "client_sku_id", [("SKU", "")])
        with patch.object(curation, "LACTOSE_CONCEPT_POLICY_PATH", self.concepts), \
                patch.object(curation, "WINIARY_SKU_LACTOSE_POLICY_PATH", self.skus):
            for _ in range(2):
                curation.curate_lactose_free_policies(db, 1)
                db.commit()
                self.assertEqual(db.get(DietPolicy, "C001").is_lactose_free, 1)
                self.assertIsNone(db.get(ClientSku, "SKU").is_lactose_free)
                self.assertEqual(db.get(DietPolicy, "C001").is_gluten_free, 1)
                self.assertEqual(db.get(ClientSku, "SKU").is_gluten_free, 0)

    def test_invalid_sku_scope_does_not_assign_concept_flags(self):
        db = self.make_database()
        self.write_policy(self.concepts, "concept_id", [("C001", "1")])
        self.write_policy(self.skus, "client_sku_id", [("OTHER", "1")])
        with patch.object(curation, "LACTOSE_CONCEPT_POLICY_PATH", self.concepts), \
                patch.object(curation, "WINIARY_SKU_LACTOSE_POLICY_PATH", self.skus):
            with self.assertRaises(ValueError):
                curation.curate_lactose_free_policies(db, 1)
        self.assertEqual(db.get(DietPolicy, "C001").is_lactose_free, 0)
        self.assertEqual(db.get(ClientSku, "SKU").is_lactose_free, 1)

    def test_model_columns_are_nullable_without_default_allow(self):
        for model in (DietPolicy, ClientSku):
            column = inspect(model).columns.is_lactose_free
            self.assertTrue(column.nullable)
            self.assertIsNone(column.default)
            self.assertIsNone(column.server_default)
