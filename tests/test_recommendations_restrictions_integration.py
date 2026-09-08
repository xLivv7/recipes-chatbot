from recommendation_integration_helpers import RealDatabaseRecommendationTestCase


class RecommendationRestrictionsIntegrationTests(RealDatabaseRecommendationTestCase):
    """Additional restriction tests against real policies, recipes and SKU data."""

    def get_gluten_free_lunches(self, diet="none"):
        normalized = self.get_normalized_recommendations(
            diet=diet,
            protein_preference="none",
            restrictions=["gluten_free"],
            nutrition_goal="standard",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]
        self.assertGreater(len(recipes), 0, diet)
        return recipes

    def test_gluten_free_recommendations_exist_in_every_category(self):
        categories = ("śniadanie", "lunch", "obiad", "kolacja", "deser", "przekąska")

        for category in categories:
            with self.subTest(category=category):
                normalized = self.get_normalized_recommendations(
                    diet="none",
                    protein_preference="none",
                    restrictions=["gluten_free"],
                    nutrition_goal="standard",
                    category=category,
                    top_n=3,
                )
                self.assertGreater(len(normalized["recommendations"]), 0, category)

    def test_gluten_free_recommendations_use_only_allowed_concepts(self):
        for recipe in self.get_gluten_free_lunches():
            for ingredient in recipe["ingredients"]:
                policy = self.recommendations.CATALOG.diet_policy_by_concept.get(
                    ingredient["concept_id"]
                )
                self.assertIsNotNone(policy, ingredient["concept_id"])
                self.assertEqual(int(policy["is_gluten_free"]), 1, recipe["recipe_id"])

    def test_gluten_free_recommendations_use_only_allowed_skus(self):
        for recipe in self.get_gluten_free_lunches():
            for used_sku in recipe["used_skus"]:
                sku = self.recommendations.CATALOG.skus_by_id[used_sku["client_sku_id"]]
                self.assertEqual(int(sku["is_gluten_free"]), 1, recipe["recipe_id"])

    def test_vegan_gluten_free_combination_enforces_both_policies(self):
        for recipe in self.get_gluten_free_lunches(diet="vegan"):
            for ingredient in recipe["ingredients"]:
                policy = self.recommendations.CATALOG.diet_policy_by_concept[
                    ingredient["concept_id"]
                ]
                self.assertEqual(int(policy["is_vegan_ok"]), 1, recipe["recipe_id"])
                self.assertEqual(int(policy["is_gluten_free"]), 1, recipe["recipe_id"])
