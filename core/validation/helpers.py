from __future__ import annotations

import math
import re
from typing import Any, Iterable


def is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def normalize_token(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def matches_pattern(value: Any, pattern: str) -> bool:
    if is_blank(value):
        return False
    return re.match(pattern, str(value).strip()) is not None


def iter_recipe_ingredient_items(recipes: Iterable[Any]):
    for recipe in recipes:
        ingredients = recipe.ingredients_data
        if not isinstance(ingredients, list):
            continue
        for idx, item in enumerate(ingredients):
            yield recipe, idx, item


def safe_float(value: Any) -> float | None:
    if not is_number(value):
        return None
    return float(value)

