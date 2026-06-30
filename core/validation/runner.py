from __future__ import annotations

from typing import Any, Callable

from core.validation.context import ValidationContext, load_context
from core.validation.models import ValidationIssue, ValidationReport
from core.validation.validators_branding import validate_branding
from core.validation.validators_diet import validate_diet_policies
from core.validation.validators_entities import validate_entities
from core.validation.validators_nutrition import validate_nutrition
from core.validation.validators_recipes import validate_recipe_jsonb
from core.validation.validators_relationships import validate_relationships
from core.validation.validators_vocabularies import validate_vocabularies

Validator = Callable[[ValidationContext], list[ValidationIssue]]

VALIDATORS: tuple[Validator, ...] = (
    validate_entities,
    validate_recipe_jsonb,
    validate_relationships,
    validate_vocabularies,
    validate_diet_policies,
    validate_nutrition,
    validate_branding,
)


def run_database_validation(db: Any) -> ValidationReport:
    ctx = load_context(db)
    report = ValidationReport(table_counts=ctx.table_counts)

    for validator in VALIDATORS:
        report.extend(validator(ctx))

    return report

