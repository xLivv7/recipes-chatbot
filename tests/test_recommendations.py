from types import SimpleNamespace
import unittest

from core.recommendation_normalization import (
    normalize_recommendations_output,
    validate_recommendations_output,
)
from core.recommendations import (
    choose_sku,
    orchestrate_recipe,
    recipe_matches_user_pref,
)


def build_catalog():
    """Build a minimal in-memory catalog used by unit tests.

    Input: no database connection; all recipes, nutrients, SKU and rules are
    declared below.
    Output: object with the same attributes as RecipeCatalog.
    Behavior: isolates recommendation logic from PostgreSQL so edge cases can
    be tested deterministically.
    """
    return SimpleNamespace(
        recipes=[
            {
                "recipe_id": "R_TEST",
                "title_pl": "Testowa zupa",
                "category": "kolacja",
                "dish_type": "Soup",
                "time_min": 20,
                "servings": 2,
                "ingredients": [{"concept_id": "C007", "grams": 100}],
                "steps_pl": ["Podgrzej bulion."],
            },
            {
                "recipe_id": "R_MEAT",
                "title_pl": "Testowe mieso",
                "category": "kolacja",
                "dish_type": "Main",
                "time_min": 30,
                "servings": 1,
                "ingredients": [{"concept_id": "C_MEAT", "grams": 100}],
                "steps_pl": ["Usmaz mieso."],
            },
        ],
        diet_policy_by_concept={
            "C007": {
                "is_vegetarian_ok": 1,
                "is_vegan_ok": 1,
                "is_meat": 0,
                "is_fish": 0,
                "is_keto_ok": 1,
            },
            "C_MEAT": {
                "is_vegetarian_ok": 0,
                "is_vegan_ok": 0,
                "is_meat": 1,
                "is_fish": 0,
                "is_keto_ok": 1,
            },
        },
        nutrients_by_concept={
            "C007": {
                "energy_kcal_100g": 10,
                "protein_g_100g": 1,
                "fat_g_100g": 0,
                "carbs_g_100g": 1,
            },
            "C_MEAT": {
                "energy_kcal_100g": 200,
                "protein_g_100g": 25,
                "fat_g_100g": 10,
                "carbs_g_100g": 0,
            },
        },
        skus_by_id={
            "VEG_BROTH": {
                "client_sku_id": "VEG_BROTH",
                "name_pl": "Bulion warzywny",
                "energy_kcal_100": 4,
                "protein_g_100": 0.2,
                "fat_g_100": 0.1,
                "carbs_g_100": 0.6,
                "concept_id": "C007",
            },
            "CHICKEN_BROTH": {
                "client_sku_id": "CHICKEN_BROTH",
                "name_pl": "Bulion drobiowy",
                "energy_kcal_100": 6,
                "protein_g_100": 0.2,
                "fat_g_100": 0.3,
                "carbs_g_100": 0.5,
                "concept_id": "C007",
            },
        },
        sku_name={
            "VEG_BROTH": "Bulion warzywny",
            "CHICKEN_BROTH": "Bulion drobiowy",
        },
        concept_to_skus={"C007": ["VEG_BROTH", "CHICKEN_BROTH"]},
        rules_by_concept={
            "C007": [
                {
                    "client_id": 1,
                    "concept_id": "C007",
                    "rule_order": 1,
                    "condition_type": "user_pref",
                    "condition_value": "vegan",
                    "preferred_sku_id": "VEG_BROTH",
                },
                {
                    "client_id": 1,
                    "concept_id": "C007",
                    "rule_order": 2,
                    "condition_type": "user_pref",
                    "condition_value": "vegetarian",
                    "preferred_sku_id": "VEG_BROTH",
                },
                {
                    "client_id": 1,
                    "concept_id": "C007",
                    "rule_order": 3,
                    "condition_type": "default",
                    "condition_value": "any",
                    "preferred_sku_id": "CHICKEN_BROTH",
                },
            ]
        },
        concept_name={"C007": "bulion", "C_MEAT": "mieso"},
    )


class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = build_catalog()

    def test_vegan_pref_selects_vegetable_broth(self):
        """Input: C007 broth concept with user_pref=vegan.

        Output: vegetable broth SKU id.
        Behavior: confirms that diet-specific SKU rules are evaluated before
        the default chicken broth fallback.
        """
        selected = choose_sku(
            "C007",
            user_pref="vegan",
            nutrition_goal="standard",
            catalog=self.catalog,
        )

        self.assertEqual(selected, "VEG_BROTH")

    def test_default_pref_uses_default_broth(self):
        """Input: C007 broth concept with no diet preference.

        Output: default chicken broth SKU id.
        Behavior: confirms that the default rule is still used when no
        diet-specific rule matches the request.
        """
        selected = choose_sku(
            "C007",
            user_pref="none",
            nutrition_goal="standard",
            catalog=self.catalog,
        )

        self.assertEqual(selected, "CHICKEN_BROTH")

    def test_vegan_filter_rejects_meat_recipe(self):
        """Input: recipe containing a concept marked as meat and user_pref=vegan.

        Output: False.
        Behavior: verifies that recipe filtering rejects recipes that violate
        a vegan dietary preference.
        """
        meat_recipe = self.catalog.recipes[1]

        self.assertFalse(recipe_matches_user_pref(meat_recipe, "vegan", catalog=self.catalog))

    def test_orchestrate_recipe_uses_selected_sku_nutrition(self):
        """Input: test soup with C007 broth and user_pref=vegan.

        Output: brandified recipe using vegetable broth and its nutrition.
        Behavior: verifies the full deterministic path: choose SKU, attach it
        to ingredients, calculate total kcal, then calculate kcal per serving.
        """
        result = orchestrate_recipe(
            "R_TEST",
            user_pref="vegan",
            nutrition_goal="standard",
            catalog=self.catalog,
        )

        self.assertEqual(result["used_skus"], ["VEG_BROTH"])
        self.assertEqual(result["brandified_ingredients"][0]["sku_id"], "VEG_BROTH")
        self.assertAlmostEqual(result["nutrition_total"]["kcal"], 4.0)
        self.assertAlmostEqual(result["nutrition_per_serving"]["kcal"], 2.0)


class RecommendationNormalizationTests(unittest.TestCase):
    def test_normalized_recommendation_output_is_valid(self):
        """Input: raw recommendation payload with unrounded nutrition values.

        Output: normalized recommendation payload with no structural errors.
        Behavior: confirms that the object passed back to the LLM has required
        fields and stable rounded nutrition/ingredient values.
        """
        raw_data = {
            "query": {
                "user_pref": "vegan",
                "nutrition_goal": "standard",
                "category": "kolacja",
                "time_max": None,
                "top_n": 1,
            },
            "recommendations": [
                {
                    "rank": 1,
                    "recipe_id": "R_TEST",
                    "title_pl": "Testowa zupa",
                    "category": "kolacja",
                    "dish_type": "Soup",
                    "time_min": 20,
                    "servings": 2,
                    "nutrition_per_serving": {
                        "kcal": 2.234,
                        "protein": 0.1,
                        "fat": 0.05,
                        "carbs": 0.3,
                    },
                    "nutrition_total": {
                        "kcal": 4.468,
                        "protein": 0.2,
                        "fat": 0.1,
                        "carbs": 0.6,
                    },
                    "used_skus": [{"client_sku_id": "VEG_BROTH", "name_pl": "Bulion warzywny"}],
                    "ingredients": [
                        {
                            "concept_id": "C007",
                            "name_pl": "bulion",
                            "grams_total": 100.0,
                            "grams_per_serving": 50.0,
                        }
                    ],
                    "steps_pl": ["Podgrzej bulion."],
                }
            ],
        }

        normalized = normalize_recommendations_output(raw_data)

        self.assertEqual(validate_recommendations_output(normalized), [])
        self.assertEqual(normalized["recommendations"][0]["nutrition_total"]["kcal"], 4.5)
        self.assertEqual(normalized["recommendations"][0]["ingredients"][0]["grams_total"], 100.0)


if __name__ == "__main__":
    unittest.main()
