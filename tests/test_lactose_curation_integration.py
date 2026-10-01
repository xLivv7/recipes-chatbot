import unittest

from sqlalchemy import inspect

import apply_data_curation as curation
from core.database import ClientSku, DietPolicy, SessionLocal, engine


class RealDatabaseLactoseCurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            with engine.connect():
                pass
        except Exception as exc:
            raise unittest.SkipTest(f"Real database is not available: {exc}") from exc

    def test_migrated_columns_are_nullable_without_server_defaults(self):
        for table in ("diet_policies", "client_skus"):
            columns = {c["name"]: c for c in inspect(engine).get_columns(table)}
            self.assertIn("is_lactose_free", columns)
            self.assertTrue(columns["is_lactose_free"]["nullable"])
            self.assertIsNone(columns["is_lactose_free"]["default"])

    def snapshot(self, db, client_id):
        return (
            {r.ingredient_id: r.is_lactose_free for r in db.query(DietPolicy).all()},
            {r.id: r.is_lactose_free for r in db.query(ClientSku).filter(ClientSku.client_id == client_id).all()},
        )

    def test_persisted_policies_match_sources_and_reimport_is_idempotent(self):
        db = SessionLocal()
        try:
            client = curation.get_required_client(db)
            expected = (
                curation.load_lactose_statuses(curation.LACTOSE_CONCEPT_POLICY_PATH, "concept_id"),
                curation.load_lactose_statuses(curation.WINIARY_SKU_LACTOSE_POLICY_PATH, "client_sku_id"),
            )
            self.assertEqual(self.snapshot(db, client.id), expected)
            for _ in range(2):
                curation.curate_lactose_free_policies(db, client.id)
                db.flush()
                db.expire_all()
                self.assertEqual(self.snapshot(db, client.id), expected)
        finally:
            # Integration tests never persist curation changes.
            db.rollback()
            db.close()
