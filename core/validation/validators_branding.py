from __future__ import annotations

from collections import defaultdict

from core.validation.context import ValidationContext
from core.validation.helpers import is_number
from core.validation.models import Severity, ValidationIssue, issue


def validate_branding(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sku_by_id = ctx.sku_by_id
    rules_by_client_concept = ctx.rules_by_client_concept

    used_rule_skus: set[str] = set()
    brandable_concepts_by_client: dict[int, set[str]] = defaultdict(set)
    for sku in ctx.client_skus:
        if sku.is_lactose_free not in (None, 0, 1):
            issues.append(issue(Severity.ERROR, "client_skus", sku.id or "<empty>",
                                "is_lactose_free", "SKU lactose-free flag must be 0, 1 or NULL."))
        elif sku.is_lactose_free is None and sku.concept_id in ctx.used_recipe_concepts:
            issues.append(issue(Severity.WARNING, "client_skus", sku.id or "<empty>",
                                "is_lactose_free", "SKU for a recipe concept has unverified lactose-free status."))
        if sku.client_id is not None and sku.concept_id:
            brandable_concepts_by_client[sku.client_id].add(sku.concept_id)
        if sku.is_gluten_free not in (0, 1):
            issues.append(
                issue(
                    Severity.ERROR,
                    "client_skus",
                    sku.id or "<empty>",
                    "is_gluten_free",
                    "SKU gluten-free flag must be 0 or 1.",
                )
            )

    for rule in ctx.sku_selection_rules:
        record_id = rule.id or "<empty>"
        if not is_number(rule.rule_order) or int(rule.rule_order) <= 0:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "rule_order",
                    "Rule order must be a positive number.",
                )
            )

        sku = sku_by_id.get(rule.preferred_sku_id)
        if sku is None:
            continue

        used_rule_skus.add(sku.id)

        if sku.client_id != rule.client_id:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "preferred_sku_id",
                    "Preferred SKU belongs to a different client than the rule.",
                )
            )
        if not sku.concept_id:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "preferred_sku_id",
                    "Preferred SKU has no concept_id and cannot be used for branding.",
                )
            )
        elif sku.concept_id != rule.concept_id:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "preferred_sku_id",
                    "Preferred SKU concept_id does not match rule concept_id.",
                )
            )
        if (
            rule.condition_type == "restriction"
            and str(rule.condition_value).strip() == "gluten_free"
            and sku.is_gluten_free != 1
        ):
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    record_id,
                    "preferred_sku_id",
                    "Gluten-free rule must select an explicitly gluten-free SKU.",
                )
            )

    issues.extend(_validate_default_fallbacks(brandable_concepts_by_client, rules_by_client_concept))
    issues.extend(_validate_rule_uniqueness(ctx))
    issues.extend(_validate_rule_coverage(ctx, brandable_concepts_by_client, rules_by_client_concept))
    issues.extend(_report_unused_skus(ctx, used_rule_skus))

    return issues


def _validate_rule_uniqueness(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    condition_keys = {}
    order_keys = {}

    for rule in ctx.sku_selection_rules:
        condition_key = (
            rule.client_id,
            rule.concept_id,
            str(rule.condition_type or "").strip(),
            str(rule.condition_value or "").strip(),
        )
        if condition_key in condition_keys:
            issues.append(
                issue(
                    Severity.ERROR,
                    "sku_selection_rules",
                    rule.id or "<empty>",
                    "condition_value",
                    f"Duplicate rule condition; first rule id is {condition_keys[condition_key]}.",
                )
            )
        else:
            condition_keys[condition_key] = rule.id

        if is_number(rule.rule_order):
            order_key = (rule.client_id, rule.concept_id, int(rule.rule_order))
            if order_key in order_keys:
                issues.append(
                    issue(
                        Severity.ERROR,
                        "sku_selection_rules",
                        rule.id or "<empty>",
                        "rule_order",
                        f"Duplicate rule order; first rule id is {order_keys[order_key]}.",
                    )
                )
            else:
                order_keys[order_key] = rule.id

    return issues


def _validate_default_fallbacks(
    brandable_concepts_by_client: dict[int, set[str]],
    rules_by_client_concept,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for client_id, concepts in brandable_concepts_by_client.items():
        for concept_id in sorted(concepts):
            rules = rules_by_client_concept.get((client_id, concept_id), [])
            has_default = any(
                rule.condition_type == "default" and str(rule.condition_value).strip() == "any"
                for rule in rules
            )
            if not has_default:
                issues.append(
                    issue(
                        Severity.WARNING,
                        "sku_selection_rules",
                        f"client={client_id},concept={concept_id}",
                        "default",
                        "Brandable concept has no default fallback rule.",
                    )
                )

    return issues


def _validate_rule_coverage(
    ctx: ValidationContext,
    brandable_concepts_by_client: dict[int, set[str]],
    rules_by_client_concept,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    used_concepts = ctx.used_recipe_concepts

    for client_id, concepts in brandable_concepts_by_client.items():
        for concept_id in sorted(concepts & used_concepts):
            if (client_id, concept_id) not in rules_by_client_concept:
                issues.append(
                    issue(
                        Severity.WARNING,
                        "sku_selection_rules",
                        f"client={client_id},concept={concept_id}",
                        "concept_id",
                        "Recipe concept has client SKUs but no selection rules.",
                    )
                )

    return issues


def _report_unused_skus(ctx: ValidationContext, used_rule_skus: set[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for sku in ctx.client_skus:
        if sku.id and sku.concept_id and sku.id not in used_rule_skus:
            issues.append(
                issue(
                    Severity.INFO,
                    "client_skus",
                    sku.id,
                    "id",
                    "SKU is mapped to a concept but is not used by any selection rule.",
                )
            )

    return issues

