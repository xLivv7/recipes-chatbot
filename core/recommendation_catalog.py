from __future__ import annotations

from dataclasses import dataclass

from core.database import ClientSku, DietPolicy, Ingredient, Nutrient, Recipe, SessionLocal, SkuSelectionRule


@dataclass(frozen=True)
class RecipeCatalog:
    recipes: list[dict]
    diet_policy_by_concept: dict[str, dict]
    nutrients_by_concept: dict[str, dict]
    skus_by_id: dict[str, dict]
    sku_name: dict[str, str]
    concept_to_skus: dict[str, list[str]]
    rules_by_concept: dict[str, list[dict]]
    concept_name: dict[str, str]


def load_recipe_catalog() -> RecipeCatalog:
    db = SessionLocal()
    try:
        recipes = [
            {
                "recipe_id": recipe.id,
                "title_pl": recipe.title_pl,
                "category": recipe.category,
                "dish_type": recipe.dish_type,
                "time_min": recipe.time_min,
                "servings": recipe.servings,
                "ingredients": recipe.ingredients_data,
                "steps_pl": recipe.steps_pl,
            }
            for recipe in db.query(Recipe).all()
        ]

        diet_policy_by_concept = {
            policy.ingredient_id: {
                "is_vegetarian_ok": policy.is_vegetarian_ok,
                "is_vegan_ok": policy.is_vegan_ok,
                "is_meat": policy.is_meat,
                "is_fish": policy.is_fish,
                "is_keto_ok": policy.is_keto_ok,
            }
            for policy in db.query(DietPolicy).all()
        }

        nutrients_by_concept = {
            nutrient.ingredient_id: {
                "energy_kcal_100g": nutrient.energy_kcal_100g,
                "protein_g_100g": nutrient.protein_g_100g,
                "fat_g_100g": nutrient.fat_g_100g,
                "carbs_g_100g": nutrient.carbs_g_100g,
            }
            for nutrient in db.query(Nutrient).all()
        }

        skus_by_id: dict[str, dict] = {}
        sku_name: dict[str, str] = {}
        concept_to_skus: dict[str, list[str]] = {}

        for sku in db.query(ClientSku).all():
            skus_by_id[sku.id] = {
                "client_sku_id": sku.id,
                "name_pl": sku.name_pl,
                "energy_kcal_100": sku.energy_kcal_100,
                "protein_g_100": sku.protein_g_100,
                "fat_g_100": sku.fat_g_100,
                "carbs_g_100": sku.carbs_g_100,
                "concept_id": sku.concept_id,
            }
            sku_name[sku.id] = sku.name_pl
            if sku.concept_id:
                concept_to_skus.setdefault(sku.concept_id, []).append(sku.id)

        rules_by_concept: dict[str, list[dict]] = {}
        for rule in db.query(SkuSelectionRule).order_by(SkuSelectionRule.rule_order).all():
            rules_by_concept.setdefault(rule.concept_id, []).append(
                {
                    "client_id": rule.client_id,
                    "concept_id": rule.concept_id,
                    "rule_order": rule.rule_order,
                    "condition_type": rule.condition_type,
                    "condition_value": rule.condition_value,
                    "preferred_sku_id": rule.preferred_sku_id,
                }
            )

        concept_name = {ingredient.id: ingredient.name_pl for ingredient in db.query(Ingredient).all()}

        return RecipeCatalog(
            recipes=recipes,
            diet_policy_by_concept=diet_policy_by_concept,
            nutrients_by_concept=nutrients_by_concept,
            skus_by_id=skus_by_id,
            sku_name=sku_name,
            concept_to_skus=concept_to_skus,
            rules_by_concept=rules_by_concept,
            concept_name=concept_name,
        )
    finally:
        db.close()


CATALOG = load_recipe_catalog()

