from __future__ import annotations

from core.validation.context import ValidationContext
from core.validation.helpers import is_blank, is_number
from core.validation.models import Severity, ValidationIssue, issue


def validate_recipe_jsonb(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for recipe in ctx.recipes:
        record_id = recipe.id or "<empty>"
        issues.extend(_validate_ingredients_data(recipe.ingredients_data, record_id))
        issues.extend(_validate_steps(recipe.steps_pl, record_id))

    return issues


def _validate_ingredients_data(ingredients_data, record_id: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(ingredients_data, list):
        return [
            issue(
                Severity.ERROR,
                "recipes",
                record_id,
                "ingredients_data",
                "ingredients_data must be a list.",
            )
        ]

    if len(ingredients_data) == 0:
        issues.append(
            issue(
                Severity.ERROR,
                "recipes",
                record_id,
                "ingredients_data",
                "ingredients_data cannot be empty.",
            )
        )

    for idx, item in enumerate(ingredients_data):
        prefix = f"ingredients_data[{idx}]"
        if not isinstance(item, dict):
            issues.append(
                issue(
                    Severity.ERROR,
                    "recipes",
                    record_id,
                    prefix,
                    f"Ingredient item must be an object, got {type(item).__name__}.",
                )
            )
            continue

        concept_id = item.get("concept_id")
        grams = item.get("grams")

        if is_blank(concept_id):
            issues.append(issue(Severity.ERROR, "recipes", record_id, f"{prefix}.concept_id", "Missing concept_id."))
        if "grams" not in item:
            issues.append(issue(Severity.ERROR, "recipes", record_id, f"{prefix}.grams", "Missing grams."))
        elif not is_number(grams):
            issues.append(issue(Severity.ERROR, "recipes", record_id, f"{prefix}.grams", "grams must be a number."))
        elif float(grams) <= 0:
            issues.append(issue(Severity.ERROR, "recipes", record_id, f"{prefix}.grams", "grams must be positive."))

    return issues


def _validate_steps(steps_pl, record_id: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(steps_pl, list):
        return [issue(Severity.ERROR, "recipes", record_id, "steps_pl", "steps_pl must be a list.")]

    if len(steps_pl) == 0:
        issues.append(issue(Severity.ERROR, "recipes", record_id, "steps_pl", "steps_pl cannot be empty."))

    for idx, step in enumerate(steps_pl):
        if not isinstance(step, str) or is_blank(step):
            issues.append(
                issue(
                    Severity.ERROR,
                    "recipes",
                    record_id,
                    f"steps_pl[{idx}]",
                    "Recipe step must be a non-empty string.",
                )
            )

    return issues

