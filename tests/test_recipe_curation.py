from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from apply_data_curation import R120_STEP_CORRECTIONS, curate_r120_steps
from core.database import Recipe, SessionLocal


class RecipeCurationTests(unittest.TestCase):
    def recipe(self):
        steps = ["unchanged 1", R120_STEP_CORRECTIONS[1][0], "unchanged 3",
                 "unchanged 4", R120_STEP_CORRECTIONS[4][0]]
        return SimpleNamespace(steps_pl=steps, ingredients_data=[{"concept_id": "C180", "grams": 200}],
                               servings=2, title_pl="unchanged title")

    def test_correction_changes_only_two_steps_and_is_idempotent(self):
        recipe = self.recipe()
        before = deepcopy(vars(recipe))
        db = Mock()
        db.get.return_value = recipe
        curate_r120_steps(db)
        expected = list(before["steps_pl"])
        for index, (_, corrected) in R120_STEP_CORRECTIONS.items():
            expected[index] = corrected
        self.assertEqual(recipe.steps_pl, expected)
        curate_r120_steps(db)
        self.assertEqual(vars(recipe), dict(before, steps_pl=expected))

    def test_changed_instruction_fails_without_partial_assignment(self):
        recipe = self.recipe()
        recipe.steps_pl[4] = "User edited this step."
        before = deepcopy(vars(recipe))
        db = Mock()
        db.get.return_value = recipe
        with self.assertRaises(ValueError):
            curate_r120_steps(db)
        self.assertEqual(vars(recipe), before)

    def test_missing_recipe_or_changed_structure_requires_review(self):
        for recipe in (None, SimpleNamespace(steps_pl=[]), SimpleNamespace(steps_pl="invalid")):
            db = Mock()
            db.get.return_value = recipe
            with self.assertRaises(ValueError):
                curate_r120_steps(db)


class RealDatabaseRecipeCurationTests(unittest.TestCase):
    def test_r120_persisted_steps_and_reapplication_are_unchanged(self):
        db = SessionLocal()
        try:
            recipe = db.get(Recipe, "R120")
            self.assertIsNotNone(recipe)
            before = deepcopy(recipe.steps_pl)
            for index, (_, corrected) in R120_STEP_CORRECTIONS.items():
                self.assertEqual(before[index], corrected)
            ingredients = deepcopy(recipe.ingredients_data)
            curate_r120_steps(db)
            db.flush()
            db.refresh(recipe)
            self.assertEqual(recipe.steps_pl, before)
            self.assertEqual(recipe.ingredients_data, ingredients)
        finally:
            db.rollback()
            db.close()
