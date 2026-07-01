from __future__ import annotations

from core.validation.context import ValidationContext
from core.validation.helpers import iter_recipe_ingredient_items
from core.validation.models import Severity, ValidationIssue, issue


def validate_relationships(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ingredient_ids = ctx.ingredient_ids
    client_ids = ctx.client_ids
    sku_ids = set(ctx.sku_by_id)

    for nutrient in ctx.nutrients:
        if nutrient.ingredient_id not in ingredient_ids:
            issues.append(
                issue(
                    Severity.ERROR,
                    "nutrients",
                    nutrient.ingredient_id,
                    "ingredient_id",
                    "Nutrient row points to a missing ingredient.",
                )
            )

    for policy in ctx.diet_policies:
        if policy.ingredient_id not in ingredient_ids:
            issues.append(
                issue(
                    Severity.ERROR,
                    "diet_policies",
                    policy.ingredient_id,
                    "ingredient_id",
                    "Diet policy points to a missing ingredient.",
                )
            )

    for sku in ctx.client_skus:
        record_id = sku.id or "<empty>"
        if sku.client_id not in client_ids:
            issues.append(issue(Severity.ERROR, "client_skus", record_id, "client_id", "SKU points to a missing client."))
        if sku.concept_id and sku.concept_id not in ingredient_ids:
            issues.append(
                issue(Severity.ERROR, "client_skus", record_id, "concept_id", "SKU points to a missing ingredient.")
            )

    for rule in ctx.sku_selection_rules:
        record_id = rule.id or "<empty>"
        if rule.client_id not in client_ids:
            issues.append(
                issue(Severity.ERROR, "sku_selection_rules", record_id, "client_id", "Rule points to a missing client.")
            )
        if rule.concept_id not in ingredient_ids:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "concept_id",
                    "Rule points to a missing ingredient.",
                )
            )
        if rule.preferred_sku_id not in sku_ids:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "preferred_sku_id",
                    "Rule points to a missing SKU.",
                )
            )

    for recipe, idx, item in iter_recipe_ingredient_items(ctx.recipes):
        if not isinstance(item, dict) or "concept_id" not in item:
            continue
        concept_id = item.get("concept_id")
        if concept_id not in ingredient_ids:
            issues.append(
                issue(
                    Severity.ERROR,
                    "recipes",
                    recipe.id or "<empty>",
                    f"ingredients_data[{idx}].concept_id",
                    f"Concept {concept_id} does not exist in ingredients.",
                )
            )

    return issues

