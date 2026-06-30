from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.database import (
    Client,
    ClientSku,
    DietPolicy,
    Ingredient,
    Nutrient,
    Recipe,
    SkuSelectionRule,
)


@dataclass(frozen=True)
class ValidationContext:
    ingredients: list[Ingredient]
    nutrients: list[Nutrient]
    diet_policies: list[DietPolicy]
    clients: list[Client]
    client_skus: list[ClientSku]
    sku_selection_rules: list[SkuSelectionRule]
    recipes: list[Recipe]

    @property
    def ingredient_ids(self) -> set[str]:
        return {item.id for item in self.ingredients if item.id is not None}

    @property
    def nutrient_by_ingredient(self) -> dict[str, Nutrient]:
        return {item.ingredient_id: item for item in self.nutrients}

    @property
    def diet_by_ingredient(self) -> dict[str, DietPolicy]:
        return {item.ingredient_id: item for item in self.diet_policies}

    @property
    def client_ids(self) -> set[int]:
        return {item.id for item in self.clients if item.id is not None}

    @property
    def sku_by_id(self) -> dict[str, ClientSku]:
        return {item.id: item for item in self.client_skus if item.id is not None}

    @property
    def rules_by_client_concept(self) -> dict[tuple[int, str], list[SkuSelectionRule]]:
        grouped: dict[tuple[int, str], list[SkuSelectionRule]] = {}
        for rule in self.sku_selection_rules:
            key = (rule.client_id, rule.concept_id)
            grouped.setdefault(key, []).append(rule)
        return grouped

    @property
    def used_recipe_concepts(self) -> set[str]:
        concepts: set[str] = set()
        for recipe in self.recipes:
            if not isinstance(recipe.ingredients_data, list):
                continue
            for item in recipe.ingredients_data:
                if isinstance(item, dict) and item.get("concept_id"):
                    concepts.add(str(item["concept_id"]))
        return concepts

    @property
    def table_counts(self) -> dict[str, int]:
        return {
            "ingredients": len(self.ingredients),
            "nutrients": len(self.nutrients),
            "diet_policies": len(self.diet_policies),
            "clients": len(self.clients),
            "client_skus": len(self.client_skus),
            "sku_selection_rules": len(self.sku_selection_rules),
            "recipes": len(self.recipes),
        }


def load_context(db: Any) -> ValidationContext:
    return ValidationContext(
        ingredients=db.query(Ingredient).all(),
        nutrients=db.query(Nutrient).all(),
        diet_policies=db.query(DietPolicy).all(),
        clients=db.query(Client).all(),
        client_skus=db.query(ClientSku).all(),
        sku_selection_rules=db.query(SkuSelectionRule).all(),
        recipes=db.query(Recipe).all(),
    )

