from recommendation_integration_helpers import RealDatabaseRecommendationTestCase


class RecommendationDietIntegrationTests(RealDatabaseRecommendationTestCase):
    """Diet preference tests against real recipe ingredients and diet policies."""

    def assert_recipes_returned_for_pref(self, user_pref):
        normalized = self.get_normalized_recommendations(
            user_pref=user_pref,
            nutrition_goal="standard",
            category="lunch",
            top_n=5,
        )
        recipes = normalized["recommendations"]
        self.assertGreater(len(recipes), 0, user_pref)
        return recipes

    def policy_for(self, recipe, ingredient):
        concept_id = ingredient["concept_id"]
        policy = self.recommendations.CATALOG.diet_policy_by_concept.get(concept_id)
        self.assertIsNotNone(policy, f"{recipe['recipe_id']} missing diet policy for {concept_id}")
        return policy

    def test_vegan_recommendations_use_only_vegan_allowed_concepts(self):
        """Input: real lunch query with user_pref=vegan.

        Output: recipes whose ingredient concepts are all vegan-compatible.
        Behavior: protects strict vegan filtering across the PostgreSQL diet
        policy table and actual recipe ingredient payloads.
        """
        for recipe in self.assert_recipes_returned_for_pref("vegan"):
            for ingredient in recipe["ingredients"]:
                policy = self.policy_for(recipe, ingredient)
                self.assertEqual(int(policy["is_vegan_ok"]), 1, recipe["recipe_id"])

    def test_vegetarian_recommendations_use_only_vegetarian_allowed_concepts(self):
        """Input: real lunch query with user_pref=vegetarian.

        Output: recipes whose ingredient concepts are all vegetarian-compatible.
        Behavior: verifies vegetarian filtering on real catalog rows, including
        recipes that may still contain dairy or egg concepts.
        """
        for recipe in self.assert_recipes_returned_for_pref("vegetarian"):
            for ingredient in recipe["ingredients"]:
                policy = self.policy_for(recipe, ingredient)
                self.assertEqual(int(policy["is_vegetarian_ok"]), 1, recipe["recipe_id"])

    def test_meat_recommendations_contain_meat_concept(self):
        """Input: real lunch query with user_pref=meat.

        Output: every returned recipe contains at least one meat ingredient.
        Behavior: protects the positive preference filter for meat-oriented
        recipe recommendations.
        """
        for recipe in self.assert_recipes_returned_for_pref("meat"):
            has_meat = any(
                int(self.policy_for(recipe, ingredient)["is_meat"]) == 1
                for ingredient in recipe["ingredients"]
            )
            self.assertTrue(has_meat, recipe["recipe_id"])

    def test_fish_recommendations_contain_fish_concept(self):
        """Input: real lunch query with user_pref=fish.

        Output: every returned recipe contains at least one fish ingredient.
        Behavior: protects the positive preference filter for fish-oriented
        recipe recommendations.
        """
        for recipe in self.assert_recipes_returned_for_pref("fish"):
            has_fish = any(
                int(self.policy_for(recipe, ingredient)["is_fish"]) == 1
                for ingredient in recipe["ingredients"]
            )
            self.assertTrue(has_fish, recipe["recipe_id"])

    def test_pescetarian_recommendations_do_not_contain_meat_concepts(self):
        """Input: real lunch query with user_pref=pescetarian.

        Output: recipes without meat concepts; fish concepts remain allowed.
        Behavior: verifies the pescetarian exclusion rule without treating fish
        as a violation.
        """
        for recipe in self.assert_recipes_returned_for_pref("pescetarian"):
            for ingredient in recipe["ingredients"]:
                policy = self.policy_for(recipe, ingredient)
                self.assertEqual(int(policy["is_meat"]), 0, recipe["recipe_id"])
