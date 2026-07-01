from __future__ import annotations

from core.validation.constants import (
    CONDITION_TYPES,
    MEAL_CATEGORIES,
)
from core.validation.context import ValidationContext
from core.validation.helpers import is_blank
from core.validation.models import Severity, ValidationIssue, issue


def validate_vocabularies(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_validate_recipe_vocabularies(ctx))
    issues.extend(_validate_rule_vocabularies(ctx))
    return issues


def _validate_recipe_vocabularies(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for recipe in ctx.recipes:
        record_id = recipe.id or "<empty>"
        if is_blank(recipe.category) or recipe.category not in MEAL_CATEGORIES:
            issues.append(
                issue(
                    Severity.ERROR,
                    "recipes",
                    record_id,
                    "category",
                    f"Recipe category must be one of: {sorted(MEAL_CATEGORIES)}.",
                )
            )

        if is_blank(recipe.dish_type):
            issues.append(issue(Severity.ERROR, "recipes", record_id, "dish_type", "Recipe dish_type is empty."))

    return issues


def _validate_rule_vocabularies(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for rule in ctx.sku_selection_rules:
        record_id = rule.id or "<empty>"
        condition_type = str(rule.condition_type or "").strip()
        condition_value = str(rule.condition_value or "").strip()

        if condition_type not in CONDITION_TYPES:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "condition_type",
                    f"Condition type '{condition_type}' is not allowed.",
                )
            )
            continue

        if not condition_value:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "condition_value",
                    "Condition value cannot be empty.",
                )
            )
        elif condition_type == "default":
            if condition_value != "any":
                issues.append(
                    issue(
                        Severity.ERROR,
                        "sku_selection_rules",
                        record_id,
                        "condition_value",
                        "Default rule must use condition_value='any'.",
                    )
                )

    return issues
