import unittest

from core.recommendation_catalog import load_recipe_catalog
from core.recommendation_normalization import normalize_recommendations_output, validate_recommendations_output
from core.recommendations import choose_sku, get_recommendations, orchestrate_recipe, recipe_matches_preferences


class RealDatabaseLactoseRecommendationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_recipe_catalog()

    def test_all_eligible_recipes_are_returned_without_unknown_concepts_or_skus(self):
        for restrictions in (["lactose_free"], ["gluten_free", "lactose_free"]):
            with self.subTest(restrictions=restrictions):
                expected = {r["recipe_id"] for r in self.catalog.recipes if all(
                    all(self.catalog.diet_policy_by_concept.get(i["concept_id"], {}).get("is_" + restriction) == 1
                        for restriction in restrictions) for i in r["ingredients"])}
                self.assertTrue(expected, "Catalog must contain eligible recipes for this integration test.")
                result = get_recommendations(category="", top_n=len(self.catalog.recipes),
                                             restrictions=restrictions, catalog=self.catalog)
                self.assertEqual({r["recipe_id"] for r in result["recommendations"]}, expected)
                self.assertEqual(validate_recommendations_output(normalize_recommendations_output(result)), [])
                for recipe in result["recommendations"]:
                    source = next(r for r in self.catalog.recipes if r["recipe_id"] == recipe["recipe_id"])
                    self.assertEqual(recipe["category"], source["category"])
                    assigned = {i["client_sku_id"] for i in recipe["ingredients"] if "client_sku_id" in i}
                    self.assertEqual(assigned, {s["client_sku_id"] for s in recipe["used_skus"]})
                    for sku_id in assigned:
                        for restriction in restrictions:
                            self.assertEqual(self.catalog.skus_by_id[sku_id]["is_" + restriction], 1)

    def test_vegan_broth_remains_generic_when_sku_is_unverified(self):
        self.assertIsNone(choose_sku("C007", "vegan", "none", ["lactose_free"], "standard", self.catalog))
        recipes = [r for r in self.catalog.recipes if any(i["concept_id"] == "C007" for i in r["ingredients"])
                   and all(self.catalog.diet_policy_by_concept[i["concept_id"]]["is_lactose_free"] == 1
                           and self.catalog.diet_policy_by_concept[i["concept_id"]]["is_vegan_ok"] == 1
                           for i in r["ingredients"])]
        self.assertTrue(recipes)
        result = orchestrate_recipe(recipes[0]["recipe_id"], diet="vegan", restrictions=["lactose_free"], catalog=self.catalog)
        self.assertTrue(all("sku_id" not in i for i in result["brandified_ingredients"] if i["concept_id"] == "C007"))

    def test_final_nutrition_uses_only_selected_skus_or_generic_concepts(self):
        result = get_recommendations(category="", top_n=len(self.catalog.recipes),
                                     restrictions=["lactose_free"], catalog=self.catalog)
        self.assertTrue(result["recommendations"])
        for recipe in result["recommendations"]:
            expected = {key: 0.0 for key in ("kcal", "protein", "fat", "carbs")}
            for ingredient in recipe["ingredients"]:
                sku_id = ingredient.get("client_sku_id")
                row = self.catalog.skus_by_id[sku_id] if sku_id else self.catalog.nutrients_by_concept[ingredient["concept_id"]]
                fields = {"kcal": "energy_kcal", "protein": "protein_g", "fat": "fat_g", "carbs": "carbs_g"}
                for key, field in fields.items():
                    expected[key] += row[field + ("_100" if sku_id else "_100g")] * ingredient["grams_total"] / 100
            for key, value in expected.items():
                self.assertAlmostEqual(recipe["nutrition_total"][key], value)
                self.assertAlmostEqual(recipe["nutrition_per_serving"][key], value / recipe["servings"])

    def test_categories_and_top_n_are_preserved_with_lactose_filter(self):
        for category in {r["category"] for r in self.catalog.recipes}:
            result = get_recommendations(category=category, top_n=3, restrictions=["lactose_free"], catalog=self.catalog)
            self.assertLessEqual(len(result["recommendations"]), 3)
            self.assertTrue(all(r["category"] == category for r in result["recommendations"]))

    def test_real_milk_policies_distinguish_regular_lactose_free_and_vegan(self):
        regular = {"ingredients": [{"concept_id": "C091"}]}
        lactose_free = {"ingredients": [{"concept_id": "C094"}]}
        self.assertFalse(recipe_matches_preferences(regular, restrictions=["lactose_free"], catalog=self.catalog))
        self.assertTrue(recipe_matches_preferences(lactose_free, restrictions=["lactose_free"], catalog=self.catalog))
        self.assertFalse(recipe_matches_preferences(lactose_free, diet="vegan", restrictions=["lactose_free"], catalog=self.catalog))
