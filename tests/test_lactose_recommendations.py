import unittest

from test_recommendations import build_catalog
from core.recommendation_preferences import validate_preference_contract
from core.recommendations import (
    choose_sku, get_recommendations, orchestrate_recipe,
    recipe_matches_preferences, sku_allows_restrictions,
)


class LactoseRecommendationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = build_catalog()
        for row in self.catalog.diet_policy_by_concept.values():
            row["is_lactose_free"] = 1
        for row in self.catalog.skus_by_id.values():
            row["is_lactose_free"] = None

    def test_backend_accepts_both_restrictions_and_removes_duplicates(self):
        self.assertEqual(validate_preference_contract("none", "none",
            ["lactose_free", "gluten_free", "lactose_free"]), ["lactose_free", "gluten_free"])

    def test_recipe_rejects_any_incompatible_or_unknown_ingredient(self):
        recipe = self.catalog.recipes[0]
        for status in (0, None):
            self.catalog.diet_policy_by_concept["C007"]["is_lactose_free"] = status
            self.assertFalse(recipe_matches_preferences(recipe, restrictions=["lactose_free"], catalog=self.catalog))

    def test_lactose_free_does_not_make_milk_vegan(self):
        self.catalog.diet_policy_by_concept["C007"]["is_vegan_ok"] = 0
        self.assertTrue(recipe_matches_preferences(self.catalog.recipes[0], restrictions=["lactose_free"], catalog=self.catalog))
        self.assertFalse(recipe_matches_preferences(self.catalog.recipes[0], diet="vegan", restrictions=["lactose_free"], catalog=self.catalog))

    def test_missing_policy_rejects_recipe(self):
        del self.catalog.diet_policy_by_concept["C007"]
        self.assertFalse(recipe_matches_preferences(self.catalog.recipes[0], restrictions=["lactose_free"], catalog=self.catalog))

    def test_unknown_skus_are_skipped_to_generic_nutrients(self):
        result = orchestrate_recipe("R_TEST", restrictions=["lactose_free"], catalog=self.catalog)
        self.assertEqual(result["used_skus"], [])
        self.assertNotIn("sku_id", result["brandified_ingredients"][0])
        self.assertEqual(result["nutrition_total"]["kcal"], 10)
        self.assertEqual(result["nutrition_per_serving"]["kcal"], 5)

    def test_next_matching_rule_can_select_verified_sku(self):
        self.catalog.rules_by_concept["C007"][0]["condition_type"] = "default"
        self.catalog.skus_by_id["CHICKEN_BROTH"]["is_lactose_free"] = 1
        selected = choose_sku("C007", "none", "none", ["lactose_free"], "standard", self.catalog)
        self.assertEqual(selected, "CHICKEN_BROTH")
        result = orchestrate_recipe("R_TEST", restrictions=["lactose_free"], catalog=self.catalog)
        self.assertEqual(result["used_skus"], ["CHICKEN_BROTH"])
        self.assertEqual(result["nutrition_total"]["kcal"], 6)

    def test_sku_requires_both_restrictions(self):
        sku = self.catalog.skus_by_id["CHICKEN_BROTH"]
        sku["is_lactose_free"] = 1
        self.assertFalse(sku_allows_restrictions("CHICKEN_BROTH", ["lactose_free", "gluten_free"], self.catalog))
        sku["is_gluten_free"] = 1
        self.assertTrue(sku_allows_restrictions("CHICKEN_BROTH", ["lactose_free", "gluten_free"], self.catalog))
        self.assertFalse(sku_allows_restrictions("MISSING", ["lactose_free"], self.catalog))

    def test_direct_orchestration_cannot_rescue_incompatible_concept(self):
        self.catalog.diet_policy_by_concept["C007"]["is_lactose_free"] = 0
        self.catalog.skus_by_id["CHICKEN_BROTH"]["is_lactose_free"] = 1
        with self.assertRaises(ValueError):
            orchestrate_recipe("R_TEST", restrictions=["lactose_free"], catalog=self.catalog)

    def test_no_results_does_not_relax_restrictions(self):
        for row in self.catalog.diet_policy_by_concept.values():
            row["is_lactose_free"] = 0
        result = get_recommendations(restrictions=["lactose_free"], catalog=self.catalog)
        self.assertEqual(result["recommendations"], [])

    def test_without_restrictions_default_branding_is_unchanged(self):
        result = orchestrate_recipe("R_TEST", catalog=self.catalog)
        self.assertEqual(result["used_skus"], ["CHICKEN_BROTH"])

    def test_payload_skus_match_final_ingredient_assignments(self):
        self.catalog.skus_by_id["CHICKEN_BROTH"]["is_lactose_free"] = 1
        result = get_recommendations(restrictions=["lactose_free"], catalog=self.catalog)
        for recipe in result["recommendations"]:
            assigned = {i["client_sku_id"] for i in recipe["ingredients"] if "client_sku_id" in i}
            self.assertEqual(assigned, {s["client_sku_id"] for s in recipe["used_skus"]})
