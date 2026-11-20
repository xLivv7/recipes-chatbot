from dataclasses import replace

from recommendation_integration_helpers import (
    RealDatabaseRecommendationTestCase,
    assert_recommendation_payload_contract,
)


class RecommendationBrandingIntegrationTests(RealDatabaseRecommendationTestCase):
    """Branding and SKU tests against real selection rules and recipe payloads."""

    def test_supported_preference_rules_use_dimension_specific_condition_types(self):
        supported_values = {"vegetarian", "vegan", "pescetarian", "meat", "fish"}
        legacy_rules = [
            rule
            for rules in self.recommendations.CATALOG.rules_by_concept.values()
            for rule in rules
            if rule["condition_type"] == "user_pref"
            and rule["condition_value"] in supported_values
        ]

        self.assertEqual(legacy_rules, [])

    def test_volume_products_require_an_authored_volume_and_compatible_diet(self):
        for concept, diet, sku in [("C001", "vegan", "WINIARY_MAJONEZ_WEGANSKI_300ML"),
                                   ("C004", "none", "WINIARY_SOS_CZOSNKOWY_BUTELKA_300ML"),
                                   ("C007", "none", "WINIARY_BULION_DROBIOWY_160G"),
                                   ("C007", "vegan", "WINIARY_BULION_WARZYWNY_SLOIK_160G")]:
            with self.subTest(concept=concept, diet=diet):
                self.assertEqual(self.recommendations.choose_sku(concept, diet, "none", [], "standard"), sku)
                self.assertIsNone(self.recommendations.choose_sku(concept, diet, "none", [], "standard", has_volume=False))
        self.assertIsNone(self.recommendations.choose_sku("C007", "pescetarian", "none", [], "standard"))
        self.assertIsNone(self.recommendations.choose_sku("C004", "vegan", "none", [], "standard"))
        self.assertEqual(self.recommendations.choose_sku("C001", "none", "none", [], "low_kcal"),
                         "WINIARY_MAJONEZ_LEKKI_300ML")

    def test_decorative_mayonnaise_400ml_uses_accepted_per_100g_table(self):
        selected = self.recommendations.choose_sku("C001", "none", "none", [], "standard")
        self.assertEqual(selected, "WINIARY_MAJONEZ_DEKORACYJNY_400ML")
        sku = self.recommendations.CATALOG.skus_by_id[selected]
        fields = ("energy_kcal_100", "protein_g_100", "fat_g_100", "carbs_g_100")
        self.assertEqual(tuple(sku[field] for field in fields), (704, 1.5, 76.3, 2.9))

    def test_generic_mayonnaise_cannot_be_served_to_a_vegan(self):
        with self.assertRaises(ValueError):
            self.recommendations.orchestrate_recipe("R013", diet="vegan")

    def test_vegan_mayonnaise_volume_uses_the_catalog_table(self):
        catalog = self.recommendations.CATALOG
        # Exercise the product and portion without changing the live C001 diet policy.
        rules = [dict(rule, condition_type="default") for rule in catalog.rules_by_concept["C001"]
                 if rule["preferred_sku_id"] == "WINIARY_MAJONEZ_WEGANSKI_300ML"]
        recipe = dict(catalog.recipes[0], ingredients=[{"concept_id": "C001", "grams": 20, "sku_ml": 15}], servings=1)
        fixture = replace(catalog, recipes=[recipe], rules_by_concept={"C001": rules})
        result = self.recommendations.orchestrate_recipe(recipe["recipe_id"], catalog=fixture)
        self.assertEqual(result["used_skus"], ["WINIARY_MAJONEZ_WEGANSKI_300ML"])
        self.assertAlmostEqual(result["nutrition_per_serving"]["kcal"], 95.55)

    def test_generic_broth_and_garlic_sauce_respect_the_reviewed_ingredient_definitions(self):
        for diet in ("vegan", "vegetarian", "pescetarian"):
            results = self.recommendations.get_recommendations(category="", top_n=180, diet=diet)
            self.assertTrue(results["recommendations"])
            for recipe in results["recommendations"]:
                generic = {i["concept_id"] for i in recipe["ingredients"] if "client_sku_id" not in i}
                self.assertNotIn("C007", generic)
                if diet == "vegan":
                    self.assertTrue(generic.isdisjoint({"C001", "C004"}))

    def test_used_skus_match_brandified_ingredient_skus(self):
        """Input: real standard lunch recommendations.

        Output: used_skus equal the SKU ids attached to brandified ingredients.
        Behavior: protects payload consistency between the recipe-level SKU
        summary and ingredient-level client_sku_id fields.
        """
        raw_data = self.recommendations.get_recommendations(
            diet="none",
            protein_preference="none",
            restrictions=[],
            nutrition_goal="standard",
            category="lunch",
            top_n=5,
        )
        recipes = raw_data["recommendations"]

        self.assertGreater(len(recipes), 0)
        self.assertTrue(any(recipe["used_skus"] for recipe in recipes))

        for recipe in recipes:
            used_sku_ids = {sku["client_sku_id"] for sku in recipe["used_skus"]}
            ingredient_sku_ids = {
                ingredient["client_sku_id"]
                for ingredient in recipe["ingredients"]
                if ingredient.get("client_sku_id")
            }

            self.assertEqual(used_sku_ids, ingredient_sku_ids, recipe["recipe_id"])
            for sku_id in used_sku_ids:
                self.assertIn(sku_id, self.recommendations.CATALOG.skus_by_id)

    def test_normalized_recommendations_keep_required_payload_fields(self):
        """Input: real standard lunch query normalized for chatbot payload use.

        Output: every recommendation has required fields, non-empty dish_type
        and steps, and non-negative numeric nutrition values.
        Behavior: protects the stable payload contract consumed after the
        deterministic recommendation step.
        """
        normalized = self.get_normalized_recommendations(
            diet="none",
            protein_preference="none",
            restrictions=[],
            nutrition_goal="standard",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]

        self.assertGreater(len(recipes), 0)
        for recipe in recipes:
            assert_recommendation_payload_contract(self, recipe)
