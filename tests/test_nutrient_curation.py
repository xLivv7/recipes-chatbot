import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from apply_data_curation import curate_concept_nutrition
from core.database import Nutrient


def values(row):
    return row.energy_kcal_100g, row.protein_g_100g, row.fat_g_100g, row.carbs_g_100g


class NutrientCurationTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        self.addCleanup(engine.dispose)
        Nutrient.__table__.create(engine)
        self.db = Session(engine)
        self.addCleanup(self.db.close)
        for concept, kcal, protein, fat, carbs in (
            ("C012", 282, 14.1, 12.9, 54.7), ("C338", 227, 19.6, 13.7, 57.9),
            ("C357", 282, 14, 13, 54), ("C367", 247, 4, 1.2, 81), ("C001", 100, 1, 2, 3),
        ):
            self.db.add(Nutrient(ingredient_id=concept, energy_kcal_100g=kcal,
                                 protein_g_100g=protein, fat_g_100g=fat, carbs_g_100g=carbs))
        self.db.commit()

    def test_replay_persists_exact_values_and_second_run_is_a_noop(self):
        self.assertEqual(curate_concept_nutrition(self.db), 4)
        self.db.commit()
        actual = {r.ingredient_id: values(r) for r in self.db.query(Nutrient)}
        self.assertEqual(actual, {
            "C012": (279, 15.4, 13.8, 23.2), "C338": (303, 23.5, 10.5, 13),
            "C357": (232, 15.3, 10.8, 18.6), "C367": (247, 4, 1.2, 60.6), "C001": (100, 1, 2, 3),
        })
        self.assertEqual(curate_concept_nutrition(self.db), 0)
        self.assertFalse(self.db.dirty)

    def test_missing_or_independently_edited_row_preserves_other_rows(self):
        row = self.db.get(Nutrient, "C367")
        row.carbs_g_100g = 7.49
        self.db.commit()
        with self.assertRaisesRegex(ValueError, "C367"):
            curate_concept_nutrition(self.db)
        self.assertFalse(self.db.dirty)
        self.assertEqual(row.carbs_g_100g, 7.49)
        self.db.delete(row)
        self.db.commit()
        with self.assertRaisesRegex(ValueError, "C367"):
            curate_concept_nutrition(self.db)
        self.assertFalse(self.db.dirty)
        self.assertEqual(values(self.db.get(Nutrient, "C012")), (282, 14.1, 12.9, 54.7))
