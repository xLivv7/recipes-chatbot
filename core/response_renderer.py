"""Render backend facts only; no model text or API calls are accepted."""

import html
import math
import re


class ResponsePayloadError(ValueError):
    """The backend payload cannot be presented without guessing facts."""


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ResponsePayloadError("Expected non-empty text.")
    value = " ".join(value.split())
    if re.search(r"https?://|www\.", value, re.IGNORECASE):
        raise ResponsePayloadError("URLs are not allowed in displayed catalog text.")
    value = html.escape(value, quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", value)


def _number(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResponsePayloadError("Expected a numeric value.")
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ResponsePayloadError("Invalid numeric value.")
    return str(value).removesuffix(".0")


def _validate_recipe(recipe):
    if not isinstance(recipe, dict):
        raise ResponsePayloadError("Expected a recipe object.")
    _text(recipe.get("recipe_id"))
    _text(recipe.get("title_pl"))
    _number(recipe.get("time_min"))
    _number(recipe.get("servings"), positive=True)
    for field in ("nutrition_total", "nutrition_per_serving"):
        nutrition = recipe.get(field)
        if not isinstance(nutrition, dict):
            raise ResponsePayloadError("Missing nutrition object.")
        for key in ("kcal", "protein", "fat", "carbs"):
            _number(nutrition.get(key))
    for field in ("ingredients", "steps_pl", "used_skus"):
        if not isinstance(recipe.get(field), list):
            raise ResponsePayloadError(f"Expected list: {field}.")
    skus = {}
    for sku in recipe["used_skus"]:
        if not isinstance(sku, dict):
            raise ResponsePayloadError("Expected SKU object.")
        sku_id = sku.get("client_sku_id")
        _text(sku_id)
        _text(sku.get("name_pl"))
        if sku_id in skus:
            raise ResponsePayloadError("Duplicate used SKU.")
        skus[sku_id] = sku
    assigned = set()
    for ingredient in recipe["ingredients"]:
        if not isinstance(ingredient, dict):
            raise ResponsePayloadError("Expected ingredient object.")
        _text(ingredient.get("concept_id"))
        _text(ingredient.get("name_pl"))
        _number(ingredient.get("grams_total"), positive=True)
        sku_id = ingredient.get("client_sku_id")
        if sku_id is not None:
            _text(sku_id)
            if sku_id not in skus:
                raise ResponsePayloadError("Ingredient SKU is absent from used_skus.")
            assigned.add(sku_id)
    if assigned != set(skus):
        raise ResponsePayloadError("Used SKU has no ingredient assignment.")
    for step in recipe["steps_pl"]:
        _text(step)


def render_recommendations(data, brand_name="Winiary"):
    """Render a validated backend payload in its original order, without mutation.

    Raises ResponsePayloadError on invalid facts. The caller owns error fallback.
    SKU assignments must be preserved by payload normalization.
    """
    if not isinstance(data, dict) or not isinstance(data.get("query"), dict):
        raise ResponsePayloadError("Expected payload and query objects.")
    recipes = data.get("recommendations")
    if not isinstance(recipes, list):
        raise ResponsePayloadError("Expected recommendations list.")
    brand = _text(brand_name)
    ids = set()
    for recipe in recipes:
        _validate_recipe(recipe)
        if recipe["recipe_id"] in ids:
            raise ResponsePayloadError("Duplicate recipe ID.")
        ids.add(recipe["recipe_id"])
    if not recipes:
        return "Nie znaleziono przepisów spełniających podane kryteria."
    sections = []
    for recipe in recipes:
        nutrition = recipe["nutrition_per_serving"]
        lines = [f"### {_text(recipe['title_pl'])}", "",
                 f"Czas: {_number(recipe['time_min'])} min | Porcje: {_number(recipe['servings'], True)}",
                 "Na porcję: " + " | ".join((
                     f"{_number(nutrition['kcal'])} kcal", f"B: {_number(nutrition['protein'])} g",
                     f"T: {_number(nutrition['fat'])} g", f"W: {_number(nutrition['carbs'])} g"))]
        if recipe["ingredients"]:
            lines.extend(["", "#### Składniki (ilości łączne)"])
            for ingredient in recipe["ingredients"]:
                name = _text(ingredient["name_pl"])
                if ingredient.get("client_sku_id") is not None:
                    sku = next(s for s in recipe["used_skus"] if s["client_sku_id"] == ingredient["client_sku_id"])
                    name += f" - {brand} {_text(sku['name_pl'])}"
                lines.append(f"- {name}: {_number(ingredient['grams_total'], True)} g")
        if recipe["steps_pl"]:
            lines.extend(["", "#### Przygotowanie"])
            lines.extend(f"{index}. {_text(step)}" for index, step in enumerate(recipe["steps_pl"], 1))
        if recipe["used_skus"]:
            products = ", ".join(f"{brand} {_text(sku['name_pl'])}" for sku in recipe["used_skus"])
            lines.extend(["", f"Produkty użyte w tym przepisie: {products}."])
        sections.append("\n".join(lines))
    return "\n\n---\n\n".join(sections)
