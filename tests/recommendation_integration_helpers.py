import importlib
import unittest


REQUIRED_RECOMMENDATION_FIELDS = {
    "recipe_id",
    "title_pl",
    "category",
    "dish_type",
    "time_min",
    "servings",
    "nutrition_total",
    "nutrition_per_serving",
    "ingredients",
    "steps_pl",
    "used_skus",
}


def load_real_recommendation_modules():
    """Load recommendation modules backed by the real PostgreSQL catalog."""
    try:
        recommendations = importlib.import_module("core.recommendations")
        normalization = importlib.import_module("core.recommendation_normalization")
    except Exception as exc:
        raise unittest.SkipTest(f"Real database is not available: {exc}") from exc

    if not recommendations.CATALOG.recipes:
        raise unittest.SkipTest("Real database catalog has no recipes.")

    return recommendations, normalization


class RealDatabaseRecommendationTestCase(unittest.TestCase):
    """Base class for read-only recommendation integration tests."""

    @classmethod
    def setUpClass(cls):
        cls.recommendations, cls.normalization = load_real_recommendation_modules()

    def get_normalized_recommendations(self, **query):
        raw_data = self.recommendations.get_recommendations(**query)
        normalized = self.normalization.normalize_recommendations_output(raw_data)
        errors = self.normalization.validate_recommendations_output(normalized)
        self.assertEqual(errors, [])
        return normalized


def assert_recommendation_payload_contract(test_case, recipe):
    missing_fields = REQUIRED_RECOMMENDATION_FIELDS.difference(recipe)
    test_case.assertEqual(missing_fields, set(), recipe.get("recipe_id"))
    test_case.assertTrue(str(recipe["dish_type"]).strip(), recipe["recipe_id"])
    test_case.assertIsInstance(recipe["steps_pl"], list, recipe["recipe_id"])
    test_case.assertGreater(len(recipe["steps_pl"]), 0, recipe["recipe_id"])

    for nutrition_field in ("nutrition_total", "nutrition_per_serving"):
        nutrition = recipe[nutrition_field]
        test_case.assertIsInstance(nutrition, dict, recipe["recipe_id"])
        for nutrient in ("kcal", "protein", "fat", "carbs"):
            value = nutrition.get(nutrient)
            test_case.assertIsInstance(value, (int, float), f"{recipe['recipe_id']} {nutrition_field}.{nutrient}")
            test_case.assertGreaterEqual(value, 0, f"{recipe['recipe_id']} {nutrition_field}.{nutrient}")
