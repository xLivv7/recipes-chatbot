from __future__ import annotations

from core.recommendation_catalog import CATALOG, RecipeCatalog
from core.recommendation_preferences import validate_preference_contract


def concept_allows_diet(concept_id: str, diet: str, catalog: RecipeCatalog = CATALOG) -> bool:
    if diet == "none":
        return True

    row = catalog.diet_policy_by_concept.get(concept_id)
    if row is None:
        return True
    if diet == "vegetarian":
        return int(row["is_vegetarian_ok"]) == 1
    if diet == "vegan":
        return int(row["is_vegan_ok"]) == 1

    raise ValueError(f"Unknown diet: {diet}")


def concept_allows_restrictions(
    concept_id: str,
    restrictions: list[str],
    catalog: RecipeCatalog = CATALOG,
) -> bool:
    policy = catalog.diet_policy_by_concept.get(concept_id)

    if "gluten_free" in restrictions:
        if policy is None or int(policy.get("is_gluten_free") or 0) != 1:
            return False

    return True


def sku_allows_restrictions(
    sku_id: str,
    restrictions: list[str],
    catalog: RecipeCatalog = CATALOG,
) -> bool:
    sku = catalog.skus_by_id.get(sku_id)

    if "gluten_free" in restrictions:
        if sku is None or int(sku.get("is_gluten_free") or 0) != 1:
            return False

    return True


def recipe_matches_preferences(
    recipe: dict,
    diet: str = "none",
    protein_preference: str = "none",
    restrictions: list[str] | None = None,
    catalog: RecipeCatalog = CATALOG,
) -> bool:
    normalized_restrictions = validate_preference_contract(diet, protein_preference, restrictions)

    if diet == "pescetarian" and any(
        int(catalog.diet_policy_by_concept.get(item["concept_id"], {}).get("is_meat", 0)) == 1
        for item in recipe.get("ingredients", [])
    ):
        return False

    if diet in {"vegetarian", "vegan"} and not all(
        concept_allows_diet(item["concept_id"], diet, catalog=catalog)
        for item in recipe.get("ingredients", [])
    ):
        return False

    if not all(
        concept_allows_restrictions(
            item["concept_id"],
            normalized_restrictions,
            catalog=catalog,
        )
        for item in recipe.get("ingredients", [])
    ):
        return False

    if protein_preference == "meat":
        return any(
            int(catalog.diet_policy_by_concept.get(item["concept_id"], {}).get("is_meat", 0)) == 1
            for item in recipe.get("ingredients", [])
        )

    if protein_preference == "fish":
        return any(
            int(catalog.diet_policy_by_concept.get(item["concept_id"], {}).get("is_fish", 0)) == 1
            for item in recipe.get("ingredients", [])
        )

    return True


def choose_sku(
    concept_id: str,
    diet: str,
    protein_preference: str,
    restrictions: list[str] | None,
    nutrition_goal: str,
    catalog: RecipeCatalog = CATALOG,
) -> str | None:
    normalized_restrictions = validate_preference_contract(diet, protein_preference, restrictions)

    if concept_id not in catalog.rules_by_concept:
        return None

    for rule in catalog.rules_by_concept[concept_id]:
        condition_type = rule["condition_type"]
        condition_value = str(rule["condition_value"])
        sku_id = rule["preferred_sku_id"]

        rule_matches = (
            (condition_type == "diet" and condition_value == diet)
            or (condition_type == "protein_preference" and condition_value == protein_preference)
            or (condition_type == "restriction" and condition_value in normalized_restrictions)
            or (condition_type == "user_pref" and condition_value in {diet, protein_preference})
            or (condition_type == "nutrition_goal" and condition_value == nutrition_goal)
            or condition_type == "default"
        )
        if rule_matches and sku_allows_restrictions(
            sku_id,
            normalized_restrictions,
            catalog=catalog,
        ):
            return sku_id

    return None


def orchestrate_recipe(
    recipe_id: str,
    diet: str = "none",
    protein_preference: str = "none",
    restrictions: list[str] | None = None,
    nutrition_goal: str = "standard",
    catalog: RecipeCatalog = CATALOG,
) -> dict:
    normalized_restrictions = validate_preference_contract(diet, protein_preference, restrictions)
    recipe = next((item for item in catalog.recipes if item["recipe_id"] == recipe_id), None)
    if recipe is None:
        raise ValueError(f"Recipe not found: {recipe_id}")

    total = {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
    brandified_ingredients = []
    used_skus = []

    for ingredient in recipe["ingredients"]:
        concept_id = ingredient["concept_id"]
        grams = float(ingredient["grams"])
        sku_id = None

        if concept_id in catalog.concept_to_skus:
            sku_id = choose_sku(
                concept_id,
                diet=diet,
                protein_preference=protein_preference,
                restrictions=normalized_restrictions,
                nutrition_goal=nutrition_goal,
                catalog=catalog,
            )

        if sku_id is not None:
            sku_row = catalog.skus_by_id[sku_id]
            kcal_100 = float(sku_row["energy_kcal_100"])
            protein_100 = float(sku_row["protein_g_100"])
            fat_100 = float(sku_row["fat_g_100"])
            carbs_100 = float(sku_row["carbs_g_100"])
            brandified_ingredients.append({"concept_id": concept_id, "sku_id": sku_id, "grams": grams})
            used_skus.append(sku_id)
        else:
            nutrient = catalog.nutrients_by_concept.get(concept_id)
            if nutrient is None:
                raise ValueError(f"Missing nutrients for concept {concept_id}")
            kcal_100 = float(nutrient["energy_kcal_100g"])
            protein_100 = float(nutrient["protein_g_100g"])
            fat_100 = float(nutrient["fat_g_100g"])
            carbs_100 = float(nutrient["carbs_g_100g"])
            brandified_ingredients.append({"concept_id": concept_id, "grams": grams})

        multiplier = grams / 100.0
        total["kcal"] += kcal_100 * multiplier
        total["protein"] += protein_100 * multiplier
        total["fat"] += fat_100 * multiplier
        total["carbs"] += carbs_100 * multiplier

    servings = float(recipe.get("servings", 1))
    per_serving = {key: value / servings for key, value in total.items()}

    return {
        "recipe_id": recipe["recipe_id"],
        "title_pl": recipe["title_pl"],
        "time_min": recipe["time_min"],
        "servings": recipe["servings"],
        "brandified_ingredients": brandified_ingredients,
        "used_skus": sorted(set(used_skus)),
        "nutrition_total": total,
        "nutrition_per_serving": per_serving,
        "steps_pl": recipe["steps_pl"],
    }


def score_recipe(result: dict, nutrition_goal: str = "standard") -> tuple:
    used = len(result["used_skus"])
    kcal = float(result["nutrition_per_serving"]["kcal"])
    protein = float(result["nutrition_per_serving"]["protein"])
    fat = float(result["nutrition_per_serving"]["fat"])
    carbs = float(result["nutrition_per_serving"]["carbs"])

    if nutrition_goal == "low_kcal":
        return (-kcal, protein, used)
    if nutrition_goal == "high_protein":
        return (protein, -kcal, used)
    if nutrition_goal == "keto":
        return (-carbs, fat, used)

    return (used, -kcal, protein)


def orchestrate_top_n(
    diet: str = "none",
    protein_preference: str = "none",
    restrictions: list[str] | None = None,
    nutrition_goal: str = "standard",
    top_n: int = 3,
    category: str = "kolacja",
    time_max: int | float | None = None,
    catalog: RecipeCatalog = CATALOG,
) -> list[dict]:
    normalized_restrictions = validate_preference_contract(diet, protein_preference, restrictions)
    results = []

    for recipe in catalog.recipes:
        if category and recipe.get("category") != category:
            continue
        if time_max is not None and float(recipe.get("time_min", 9999)) > float(time_max):
            continue
        if not recipe_matches_preferences(
            recipe,
            diet=diet,
            protein_preference=protein_preference,
            restrictions=normalized_restrictions,
            catalog=catalog,
        ):
            continue

        try:
            result = orchestrate_recipe(
                recipe["recipe_id"],
                diet=diet,
                protein_preference=protein_preference,
                restrictions=normalized_restrictions,
                nutrition_goal=nutrition_goal,
                catalog=catalog,
            )
            if nutrition_goal == "keto" and float(result["nutrition_per_serving"]["carbs"]) > 15.0:
                continue
            if "dish_type" not in result:
                result["dish_type"] = recipe.get("dish_type", "unknown")
            results.append(result)
        except Exception:
            continue

    results.sort(key=lambda item: score_recipe(item, nutrition_goal=nutrition_goal), reverse=True)

    selected = []
    used_types = set()
    for result in results:
        dish_type = result.get("dish_type", "unknown")
        if dish_type in used_types:
            continue
        selected.append(result)
        used_types.add(dish_type)
        if len(selected) >= top_n:
            return selected

    if len(selected) < top_n:
        selected_ids = {item["recipe_id"] for item in selected}
        for result in results:
            if result["recipe_id"] in selected_ids:
                continue
            selected.append(result)
            if len(selected) >= top_n:
                break

    return selected


def get_recommendations(
    diet: str = "none",
    protein_preference: str = "none",
    restrictions: list[str] | None = None,
    nutrition_goal: str = "standard",
    top_n: int = 3,
    category: str = "kolacja",
    time_max: int | None = None,
    catalog: RecipeCatalog = CATALOG,
) -> dict:
    normalized_restrictions = validate_preference_contract(diet, protein_preference, restrictions)
    top_results = orchestrate_top_n(
        diet=diet,
        protein_preference=protein_preference,
        restrictions=normalized_restrictions,
        nutrition_goal=nutrition_goal,
        top_n=top_n,
        category=category,
        time_max=time_max,
        catalog=catalog,
    )
    recommendations = []

    for rank, result in enumerate(top_results, start=1):
        servings = float(result.get("servings", 1))
        used_skus = [
            {"client_sku_id": sku_id, "name_pl": catalog.sku_name.get(sku_id, sku_id)}
            for sku_id in result.get("used_skus", [])
        ]

        ingredients = []
        for ingredient in result.get("brandified_ingredients", []):
            concept_id = ingredient["concept_id"]
            grams_total = float(ingredient["grams"])
            item = {
                "concept_id": concept_id,
                "name_pl": catalog.concept_name.get(concept_id, concept_id),
                "grams_total": grams_total,
                "grams_per_serving": grams_total / servings,
            }
            if "sku_id" in ingredient:
                item["client_sku_id"] = ingredient["sku_id"]
                item["client_sku_name_pl"] = catalog.sku_name.get(ingredient["sku_id"], ingredient["sku_id"])
            ingredients.append(item)

        recommendations.append(
            {
                "rank": rank,
                "recipe_id": result["recipe_id"],
                "title_pl": result["title_pl"],
                "category": result.get("category", category),
                "dish_type": result.get("dish_type", "unknown"),
                "time_min": result.get("time_min"),
                "servings": result.get("servings"),
                "nutrition_per_serving": result.get("nutrition_per_serving"),
                "nutrition_total": result.get("nutrition_total"),
                "used_skus": used_skus,
                "ingredients": ingredients,
                "steps_pl": result.get("steps_pl", []),
            }
        )

    return {
        "query": {
            "diet": diet,
            "protein_preference": protein_preference,
            "restrictions": normalized_restrictions,
            "nutrition_goal": nutrition_goal,
            "category": category,
            "time_max": time_max,
            "top_n": top_n,
        },
        "recommendations": recommendations,
    }
