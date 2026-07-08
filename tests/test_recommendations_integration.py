import importlib
import unittest


VEGETABLE_BROTH_SKU_ID = "WINIARY_BULION_WARZYWNY_SLOIK_160G"


class RealDatabaseRecommendationTests(unittest.TestCase):
    """Integration tests for recommendation logic running on the real database.

    These tests intentionally do not use fake in-memory data. They verify that
    the PostgreSQL catalog, SKU rules, nutrition values and recommendation code
    work together as one read-only flow.
    """

    @classmethod
    def setUpClass(cls):
        """Input: DATABASE_URL and populated PostgreSQL database from .env.

        Output: imported recommendation modules with a loaded real catalog.
        Behavior: skips the whole integration suite when the local database is
        not available, so unit tests can still run in lightweight environments.
        """
        try:
            cls.recommendations = importlib.import_module("core.recommendations")
            cls.normalization = importlib.import_module("core.recommendation_normalization")
        except Exception as exc:
            raise unittest.SkipTest(f"Real database is not available: {exc}") from exc

        if not cls.recommendations.CATALOG.recipes:
            raise unittest.SkipTest("Real database catalog has no recipes.")

    def test_lunch_recommendations_have_valid_output_shape(self):
        """Input: real lunch query requesting up to three recommendations.

        Output: non-empty, normalized and structurally valid recommendation
        payload.
        Behavior: verifies the main read path on production-like data:
        database catalog -> deterministic recommendation engine -> normalized
        response object that can be safely passed back to the LLM.
        """
        raw_data = self.recommendations.get_recommendations(
            user_pref="none",
            nutrition_goal="standard",
            category="lunch",
            top_n=3,
        )

        normalized = self.normalization.normalize_recommendations_output(raw_data)
        errors = self.normalization.validate_recommendations_output(normalized)

        self.assertEqual(errors, [])
        self.assertGreater(len(normalized["recommendations"]), 0)
        self.assertLessEqual(len(normalized["recommendations"]), 3)
        self.assertTrue(
            all(recipe["category"] == "lunch" for recipe in normalized["recommendations"])
        )

    def test_kolacja_recommendations_respect_top_n_and_time_limit(self):
        """Input: real dinner query limited to two recipes and max 30 minutes.

        Output: at most two recommendations, each no longer than 30 minutes.
        Behavior: checks that business filters from the user query are applied
        before the chatbot response is generated.
        """
        raw_data = self.recommendations.get_recommendations(
            user_pref="none",
            nutrition_goal="standard",
            category="kolacja",
            time_max=30,
            top_n=2,
        )

        recommendations = raw_data["recommendations"]

        self.assertLessEqual(len(recommendations), 2)
        self.assertTrue(all(recipe["time_min"] <= 30 for recipe in recommendations))

    def test_vegan_broth_rule_uses_vegetable_broth_sku(self):
        """Input: real C007 broth concept with user_pref=vegan.

        Output: Winiary vegetable broth SKU id.
        Behavior: protects the curated FMCG branding rule that prevents vegan
        requests from falling back to chicken broth.
        """
        selected_sku = self.recommendations.choose_sku(
            "C007",
            user_pref="vegan",
            nutrition_goal="standard",
        )

        self.assertEqual(selected_sku, VEGETABLE_BROTH_SKU_ID)

    def test_vegan_recommendations_use_only_vegan_allowed_concepts(self):
        """Input: real vegan dinner query.

        Output: recommendations whose ingredient concepts are vegan-compatible.
        Behavior: verifies that recipe-level diet filtering works against real
        diet_policies rows instead of only mocked flags.
        """
        raw_data = self.recommendations.get_recommendations(
            user_pref="vegan",
            nutrition_goal="standard",
            category="kolacja",
            top_n=5,
        )

        self.assertGreater(len(raw_data["recommendations"]), 0)

        for recipe in raw_data["recommendations"]:
            for ingredient in recipe["ingredients"]:
                concept_id = ingredient["concept_id"]
                policy = self.recommendations.CATALOG.diet_policy_by_concept.get(concept_id)
                self.assertIsNotNone(policy, f"Missing diet policy for {concept_id}")
                self.assertEqual(
                    int(policy["is_vegan_ok"]),
                    1,
                    f"{recipe['recipe_id']} contains non-vegan concept {concept_id}",
                )

    def test_keto_recommendations_respect_current_carb_limit(self):
        """Input: real keto dinner query.

        Output: every returned recommendation has max 15 g carbs per serving.
        Behavior: confirms that the current deterministic keto threshold is
        applied after nutrition calculation on real ingredient/SKU data.
        """
        raw_data = self.recommendations.get_recommendations(
            user_pref="none",
            nutrition_goal="keto",
            category="kolacja",
            top_n=5,
        )

        for recipe in raw_data["recommendations"]:
            carbs = float(recipe["nutrition_per_serving"]["carbs"])
            self.assertLessEqual(carbs, 15.0, recipe["recipe_id"])


if __name__ == "__main__":
    unittest.main()
