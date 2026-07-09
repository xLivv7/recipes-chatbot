from recommendation_integration_helpers import (
    RealDatabaseRecommendationTestCase,
    assert_recommendation_payload_contract,
)


VEGETABLE_BROTH_SKU_ID = "WINIARY_BULION_WARZYWNY_SLOIK_160G"
DEFAULT_BROTH_SKU_ID = "WINIARY_BULION_DROBIOWY_160G"


class RecommendationBrandingIntegrationTests(RealDatabaseRecommendationTestCase):
    """Branding and SKU tests against real selection rules and recipe payloads."""

    def test_c007_vegan_pref_selects_vegetable_broth_sku(self):
        """Input: C007 broth concept with user_pref=vegan.

        Output: Winiary vegetable broth SKU id.
        Behavior: protects the curated rule that prevents vegan requests from
        falling back to a non-vegan/default broth SKU.
        """
        selected_sku = self.recommendations.choose_sku(
            "C007",
            user_pref="vegan",
            nutrition_goal="standard",
        )

        self.assertEqual(selected_sku, VEGETABLE_BROTH_SKU_ID)

    def test_c007_without_pref_uses_default_broth_sku(self):
        """Input: C007 broth concept with no diet preference.

        Output: default Winiary chicken broth SKU id.
        Behavior: verifies that the default SKU rule remains available for
        standard non-restricted recommendations.
        """
        selected_sku = self.recommendations.choose_sku(
            "C007",
            user_pref="none",
            nutrition_goal="standard",
        )

        self.assertEqual(selected_sku, DEFAULT_BROTH_SKU_ID)

    def test_used_skus_match_brandified_ingredient_skus(self):
        """Input: real standard lunch recommendations.

        Output: used_skus equal the SKU ids attached to brandified ingredients.
        Behavior: protects payload consistency between the recipe-level SKU
        summary and ingredient-level client_sku_id fields.
        """
        raw_data = self.recommendations.get_recommendations(
            user_pref="none",
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
            user_pref="none",
            nutrition_goal="standard",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]

        self.assertGreater(len(recipes), 0)
        for recipe in recipes:
            assert_recommendation_payload_contract(self, recipe)
