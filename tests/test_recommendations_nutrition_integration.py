from recommendation_integration_helpers import RealDatabaseRecommendationTestCase


class RecommendationNutritionIntegrationTests(RealDatabaseRecommendationTestCase):
    """Nutrition goal tests against real calculated recipe nutrition."""

    def test_keto_recommendations_have_max_15g_carbs_per_serving(self):
        """Input: real keto lunch query.

        Output: recommendations with at most 15 g carbs per serving.
        Behavior: protects the deterministic keto threshold after SKU
        substitution and nutrition calculation on real data.
        """
        normalized = self.get_normalized_recommendations(
            user_pref="none",
            nutrition_goal="keto",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]

        self.assertGreater(len(recipes), 0)
        for recipe in recipes:
            carbs = float(recipe["nutrition_per_serving"]["carbs"])
            self.assertLessEqual(carbs, 15.0, recipe["recipe_id"])

    def test_low_kcal_goal_orders_lower_kcal_first(self):
        """Input: real low_kcal lunch query.

        Output: recommendations ordered by ascending kcal per serving.
        Behavior: verifies that the scoring function promotes lower-calorie
        recipes for the low_kcal nutrition goal.
        """
        normalized = self.get_normalized_recommendations(
            user_pref="none",
            nutrition_goal="low_kcal",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]
        kcal_values = [float(recipe["nutrition_per_serving"]["kcal"]) for recipe in recipes]

        self.assertGreater(len(kcal_values), 1)
        self.assertEqual(kcal_values, sorted(kcal_values))

    def test_high_protein_goal_orders_higher_protein_first(self):
        """Input: real high_protein lunch query.

        Output: recommendations ordered by descending protein per serving.
        Behavior: verifies that the scoring function promotes protein-dense
        recipes for the high_protein nutrition goal.
        """
        normalized = self.get_normalized_recommendations(
            user_pref="none",
            nutrition_goal="high_protein",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]
        protein_values = [float(recipe["nutrition_per_serving"]["protein"]) for recipe in recipes]

        self.assertGreater(len(protein_values), 1)
        self.assertEqual(protein_values, sorted(protein_values, reverse=True))
