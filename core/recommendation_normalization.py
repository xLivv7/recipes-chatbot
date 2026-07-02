from __future__ import annotations


def safe_round(value, ndigits: int = 1):
    return round(value, ndigits) if isinstance(value, (int, float)) else value


def safe_str(value) -> str:
    return str(value).strip() if value is not None else ""


def normalize_ingredient(ingredient: dict) -> dict:
    return {
        "concept_id": ingredient.get("concept_id"),
        "name_pl": safe_str(ingredient.get("name_pl")),
        "grams_total": safe_round(ingredient.get("grams_total"), 0),
        "grams_per_serving": safe_round(ingredient.get("grams_per_serving"), 0),
    }


def normalize_nutrition(nutrition: dict) -> dict:
    nutrition = nutrition or {}
    return {
        "kcal": safe_round(nutrition.get("kcal"), 1),
        "protein": safe_round(nutrition.get("protein"), 1),
        "fat": safe_round(nutrition.get("fat"), 1),
        "carbs": safe_round(nutrition.get("carbs"), 1),
    }


def normalize_steps(steps) -> list[str]:
    return [safe_str(step) for step in steps if safe_str(step)] if isinstance(steps, list) else []


def normalize_recipe(recipe: dict) -> dict:
    return {
        "rank": recipe.get("rank"),
        "recipe_id": recipe.get("recipe_id"),
        "title_pl": safe_str(recipe.get("title_pl")),
        "category": safe_str(recipe.get("category")),
        "dish_type": safe_str(recipe.get("dish_type")),
        "time_min": recipe.get("time_min"),
        "servings": recipe.get("servings"),
        "nutrition_per_serving": normalize_nutrition(recipe.get("nutrition_per_serving")),
        "nutrition_total": normalize_nutrition(recipe.get("nutrition_total")),
        "used_skus": recipe.get("used_skus", []),
        "ingredients": [normalize_ingredient(ingredient) for ingredient in recipe.get("ingredients", [])],
        "steps_pl": normalize_steps(recipe.get("steps_pl")),
    }


def normalize_recommendations_output(raw_data: dict) -> dict:
    raw_query = raw_data.get("query", {})
    return {
        "query": {
            "user_pref": safe_str(raw_query.get("user_pref")),
            "nutrition_goal": safe_str(raw_query.get("nutrition_goal")),
            "category": safe_str(raw_query.get("category")),
            "time_max": raw_query.get("time_max"),
            "top_n": raw_query.get("top_n"),
        },
        "recommendations": [normalize_recipe(recipe) for recipe in raw_data.get("recommendations", [])],
    }


def validate_recommendations_output(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return ["Input data is not a dict."]
    if "query" not in data:
        errors.append("Missing 'query'.")
    if "recommendations" not in data:
        errors.append("Missing 'recommendations'.")
        return errors
    if not isinstance(data["recommendations"], list):
        errors.append("'recommendations' is not a list.")
        return errors

    for idx, recipe in enumerate(data["recommendations"], start=1):
        if not recipe.get("recipe_id"):
            errors.append(f"Recommendation #{idx}: missing 'recipe_id'.")
        if not recipe.get("title_pl"):
            errors.append(f"Recommendation #{idx}: missing 'title_pl'.")
        if "nutrition_per_serving" not in recipe:
            errors.append(f"Recommendation #{idx}: missing 'nutrition_per_serving'.")
        if "nutrition_total" not in recipe:
            errors.append(f"Recommendation #{idx}: missing 'nutrition_total'.")

    return errors

