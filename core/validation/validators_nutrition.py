from __future__ import annotations

from typing import Any

from core.validation.constants import NUTRIENT_FIELDS, SKU_NUTRIENT_FIELDS
from core.validation.context import ValidationContext
from core.validation.helpers import safe_float
from core.validation.models import Severity, ValidationIssue, issue


def validate_nutrition(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_validate_generic_nutrients(ctx))
    issues.extend(_validate_sku_nutrients(ctx))
    issues.extend(_validate_recipe_nutrition_coverage(ctx))
    return issues


def _validate_generic_nutrients(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for row in ctx.nutrients:
        values = {label: getattr(row, field) for field, label in NUTRIENT_FIELDS.items()}
        issues.extend(_validate_nutrient_values("nutrients", row.ingredient_id, values))
    return issues


def _validate_sku_nutrients(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for sku in ctx.client_skus:
        values = {label: getattr(sku, field) for field, label in SKU_NUTRIENT_FIELDS.items()}
        issues.extend(_validate_nutrient_values("client_skus", sku.id or "<empty>", values))
    return issues


def _validate_recipe_nutrition_coverage(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    nutrient_ids = set(ctx.nutrient_by_ingredient)

    for concept_id in sorted(ctx.used_recipe_concepts):
        if concept_id not in nutrient_ids:
            issues.append(
                issue(
                    Severity.ERROR,
                    "nutrients",
                    concept_id,
                    "ingredient_id",
                    "Ingredient is used in recipes but has no generic nutrient row.",
                )
            )
    return issues


def _validate_nutrient_values(table: str, record_id: str, values: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for label, value in values.items():
        number = safe_float(value)
        if number is None:
            issues.append(issue(Severity.ERROR, table, record_id, label, "Nutrient value must be a finite number."))
        elif number < 0:
            issues.append(issue(Severity.ERROR, table, record_id, label, "Nutrient value cannot be negative."))

    kcal = safe_float(values.get("kcal"))
    protein = safe_float(values.get("protein"))
    fat = safe_float(values.get("fat"))
    carbs = safe_float(values.get("carbs"))

    if kcal is not None and (kcal < 0 or kcal > 950):
        issues.append(issue(Severity.WARNING, table, record_id, "kcal", "Energy value is outside the expected range."))

    macros = [protein, fat, carbs]
    if all(value is not None for value in macros):
        macro_sum = sum(value for value in macros if value is not None)
        if macro_sum > 105:
            issues.append(
                issue(
                    Severity.WARNING,
                    table,
                    record_id,
                    "macros",
                    "Macro sum is above a plausible per-100g range.",
                )
            )

    if None not in (kcal, protein, fat, carbs):
        macro_kcal = 4 * protein + 9 * fat + 4 * carbs
        tolerance = max(50.0, kcal * 0.35)
        if abs(kcal - macro_kcal) > tolerance:
            issues.append(
                issue(
                    Severity.WARNING,
                    table,
                    record_id,
                    "kcal",
                    "Energy value differs from macro-derived kcal; review source data, fiber, or polyols.",
                )
            )

    return issues
