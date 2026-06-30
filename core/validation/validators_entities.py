from __future__ import annotations

from collections import Counter

from core.validation.constants import INGREDIENT_ID_PATTERN, RECIPE_ID_PATTERN
from core.validation.context import ValidationContext
from core.validation.helpers import is_blank, is_number, matches_pattern
from core.validation.models import Severity, ValidationIssue, issue


def validate_entities(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(_validate_ingredients(ctx))
    issues.extend(_validate_clients(ctx))
    issues.extend(_validate_client_skus(ctx))
    issues.extend(_validate_recipes_base(ctx))
    return issues


def _validate_ingredients(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = [item.id for item in ctx.ingredients]
    duplicates = {item for item, count in Counter(ids).items() if item and count > 1}

    for ingredient in ctx.ingredients:
        record_id = ingredient.id or "<empty>"
        if is_blank(ingredient.id):
            issues.append(issue(Severity.ERROR, "ingredients", record_id, "id", "Ingredient id is empty."))
        elif not matches_pattern(ingredient.id, INGREDIENT_ID_PATTERN):
            issues.append(
                issue(
                    Severity.ERROR,
                    "ingredients",
                    record_id,
                    "id",
                    "Ingredient id should use a stable concept format like C001.",
                )
            )
        if ingredient.id in duplicates:
            issues.append(issue(Severity.ERROR, "ingredients", record_id, "id", "Ingredient id is duplicated."))
        if is_blank(ingredient.name_pl):
            issues.append(issue(Severity.ERROR, "ingredients", record_id, "name_pl", "Ingredient name is empty."))
    return issues


def _validate_clients(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    names = [client.name for client in ctx.clients if not is_blank(client.name)]
    duplicate_names = {item for item, count in Counter(names).items() if count > 1}

    for client in ctx.clients:
        record_id = client.id or "<empty>"
        if client.id is None:
            issues.append(issue(Severity.ERROR, "clients", record_id, "id", "Client id is empty."))
        if is_blank(client.name):
            issues.append(issue(Severity.ERROR, "clients", record_id, "name", "Client name is empty."))
        elif client.name in duplicate_names:
            issues.append(issue(Severity.ERROR, "clients", record_id, "name", "Client name is duplicated."))
    return issues


def _validate_client_skus(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = [sku.id for sku in ctx.client_skus]
    duplicates = {item for item, count in Counter(ids).items() if item and count > 1}

    for sku in ctx.client_skus:
        record_id = sku.id or "<empty>"
        if is_blank(sku.id):
            issues.append(issue(Severity.ERROR, "client_skus", record_id, "id", "SKU id is empty."))
        elif sku.id in duplicates:
            issues.append(issue(Severity.ERROR, "client_skus", record_id, "id", "SKU id is duplicated."))
        if is_blank(sku.name_pl):
            issues.append(issue(Severity.ERROR, "client_skus", record_id, "name_pl", "SKU name is empty."))
    return issues


def _validate_recipes_base(ctx: ValidationContext) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    ids = [recipe.id for recipe in ctx.recipes]
    duplicates = {item for item, count in Counter(ids).items() if item and count > 1}

    for recipe in ctx.recipes:
        record_id = recipe.id or "<empty>"
        if is_blank(recipe.id):
            issues.append(issue(Severity.ERROR, "recipes", record_id, "id", "Recipe id is empty."))
        elif not matches_pattern(recipe.id, RECIPE_ID_PATTERN):
            issues.append(
                issue(
                    Severity.WARNING,
                    "recipes",
                    record_id,
                    "id",
                    "Recipe id should use a stable format like R001.",
                )
            )
        if recipe.id in duplicates:
            issues.append(issue(Severity.ERROR, "recipes", record_id, "id", "Recipe id is duplicated."))
        if is_blank(recipe.title_pl):
            issues.append(issue(Severity.ERROR, "recipes", record_id, "title_pl", "Recipe title is empty."))
        if not is_number(recipe.time_min) or float(recipe.time_min) <= 0:
            issues.append(issue(Severity.ERROR, "recipes", record_id, "time_min", "Recipe time must be positive."))
        elif float(recipe.time_min) > 240:
            issues.append(issue(Severity.WARNING, "recipes", record_id, "time_min", "Recipe time looks unusually high."))
        if not is_number(recipe.servings) or float(recipe.servings) <= 0:
            issues.append(issue(Severity.ERROR, "recipes", record_id, "servings", "Servings must be positive."))
    return issues

