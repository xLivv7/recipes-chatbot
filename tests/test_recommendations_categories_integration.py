from recommendation_integration_helpers import (
    RealDatabaseRecommendationTestCase,
    assert_recommendation_payload_contract,
)


class RecommendationCategoryIntegrationTests(RealDatabaseRecommendationTestCase):
    """Category coverage against the real PostgreSQL recommendation catalog."""

    def test_each_supported_category_returns_matching_recommendations(self):
        """Input: every supported recipe category with top_n=3.

        Output: non-empty normalized recommendations for each category.
        Behavior: protects the business taxonomy used by the chatbot and
        verifies that category filtering does not leak recipes from another
        category or exceed the requested result limit.
        """
        categories = ("śniadanie", "lunch", "obiad", "kolacja", "deser", "przekąska")
        top_n = 3

        for category in categories:
            with self.subTest(category=category):
                normalized = self.get_normalized_recommendations(
                    user_pref="none",
                    nutrition_goal="standard",
                    category=category,
                    top_n=top_n,
                )
                recipes = normalized["recommendations"]

                self.assertGreater(len(recipes), 0, category)
                self.assertLessEqual(len(recipes), top_n, category)

                for recipe in recipes:
                    self.assertEqual(recipe["category"], category, recipe["recipe_id"])
                    assert_recommendation_payload_contract(self, recipe)
