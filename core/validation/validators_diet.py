from __future__ import annotations

from core.validation.context import ValidationContext
from core.validation.models import Severity, ValidationIssue, issue


DIET_FLAG_FIELDS = (
    "is_vegetarian_ok",
    "is_vegan_ok",
    "is_meat",
    "is_fish",
    "is_keto_ok",
)


def validate_diet_policies(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    policy_by_ingredient = ctx.diet_by_ingredient

    for policy in ctx.diet_policies:
        record_id = policy.ingredient_id or "<empty>"
        for field in DIET_FLAG_FIELDS:
            value = getattr(policy, field)
            if value not in (0, 1):
                issues.append(
                    issue(
                        Severity.ERROR,
                        "diet_policies",
                        record_id,
                        field,
                        "Diet policy flag must be 0 or 1.",
                    )
                )

        if policy.is_vegan_ok == 1 and policy.is_vegetarian_ok != 1:
            issues.append(
                issue(
                    Severity.ERROR,
                    "diet_policies",
                    record_id,
                    "is_vegan_ok",
                    "Vegan ingredient must also be vegetarian.",
                )
            )
        if policy.is_meat == 1 and (policy.is_vegetarian_ok == 1 or policy.is_vegan_ok == 1):
            issues.append(
                issue(
                    Severity.ERROR,
                    "diet_policies",
                    record_id,
                    "is_meat",
                    "Meat cannot be marked vegetarian or vegan.",
                )
            )
        if policy.is_fish == 1 and (policy.is_vegetarian_ok == 1 or policy.is_vegan_ok == 1):
            issues.append(
                issue(
                    Severity.ERROR,
                    "diet_policies",
                    record_id,
                    "is_fish",
                    "Fish cannot be marked vegetarian or vegan.",
                )
            )

    for concept_id in sorted(ctx.used_recipe_concepts):
        if concept_id not in policy_by_ingredient:
            issues.append(
                issue(
                    Severity.WARNING,
                    "diet_policies",
                    concept_id,
                    "ingredient_id",
                    "Ingredient is used in recipes but has no diet policy.",
                )
            )

    return issues

