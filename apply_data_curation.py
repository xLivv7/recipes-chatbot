"""Idempotent data curation entrypoint for reproducible database fixes.

Add future data corrections as separate functions and call them from
apply_curation(), so each manual data decision can be replayed after a
database rebuild.
"""

import argparse
import csv
from pathlib import Path

from sqlalchemy import inspect, text

from core.database import Client, ClientSku, DietPolicy, Ingredient, Nutrient, Recipe, SessionLocal, SkuSelectionRule, engine


CLIENT_NAME = "Winiary"
# Authored volumes for the two-serving recipes reviewed in T030.
# The original gram amount is retained for the generic or other gram-based variant.
RECIPE_VOLUMES_ML = {
    "C001": {30: ("R024", "R109"), 50: ("R064", "R065", "R081", "R090", "R104", "R118", "R161", "R176"),
             80: ("R113",), 100: ("R013", "R022", "R025", "R029", "R061", "R096", "R119", "R136"),
             150: ("R130",), 200: ("R060",)},
    "C004": {30: ("R069",), 50: ("R018", "R078", "R158", "R169"), 100: ("R062", "R099", "R152", "R173")},
    "C007": {200: ("R047",), 500: ("R036", "R037", "R041", "R045", "R053", "R057", "R069", "R097", "R108", "R110"),
             1000: ("R080",)},
}


def curate_recipe_volumes(db):
    targets = {}
    for concept, portions in RECIPE_VOLUMES_ML.items():
        for ml, recipe_ids in portions.items():
            for recipe_id in recipe_ids:
                targets.setdefault(recipe_id, {})[concept] = ml
    recipes = db.query(Recipe).filter(Recipe.id.in_(targets)).order_by(Recipe.id).with_for_update().all()
    if len(recipes) != len(targets):
        raise ValueError("Missing recipes for volume curation.")
    changes = []
    for recipe in recipes:
        amounts = targets[recipe.id]
        ingredients = [dict(item) for item in recipe.ingredients_data]
        found = set()
        for item in ingredients:
            concept = item["concept_id"]
            if concept not in amounts:
                continue
            ml = amounts[concept]
            if (recipe.servings != 2 or concept in found or item.get("grams") != ml
                    or ("sku_ml" in item and item["sku_ml"] != ml)):
                raise ValueError(f"Review volume variant for {recipe.id}/{concept} before applying curation.")
            item["sku_ml"] = ml
            found.add(concept)
        if found != amounts.keys():
            raise ValueError(f"Missing volume ingredient in {recipe.id}.")
        if ingredients != recipe.ingredients_data:
            changes.append((recipe, ingredients))
    for recipe, ingredients in changes:
        recipe.ingredients_data = ingredients
    return len(changes)


BROTH_CONCEPT_ID = "C007"
VEGETABLE_BROTH_SKU_ID = "WINIARY_BULION_WARZYWNY_SLOIK_160G"
CURATION_DIR = Path(__file__).resolve().parent / "curation"
GLUTEN_UNSAFE_CONCEPTS_PATH = CURATION_DIR / "gluten_unsafe_concepts.csv"
WINIARY_SKU_GLUTEN_POLICY_PATH = CURATION_DIR / "winiary_sku_gluten_policy.csv"
GLUTEN_POLICY_MAX_CONCEPT_NUMBER = 376

# T007: (kcal, protein, fat, carbohydrates) per 100 g, before and after review.
NUTRITION_CORRECTIONS = {
    "C012": ((282, 14.1, 12.9, 54.7), (279, 15.4, 13.8, 23.2)),
    "C338": ((227, 19.6, 13.7, 57.9), (303, 23.5, 10.5, 13)),
    "C357": ((282, 14, 13, 54), (232, 15.3, 10.8, 18.6)),
    "C367": ((247, 4, 1.2, 81), (247, 4, 1.2, 60.6)),
}


def curate_concept_nutrition(db):
    rows = (db.query(Nutrient).filter(Nutrient.ingredient_id.in_(NUTRITION_CORRECTIONS))
            .order_by(Nutrient.ingredient_id).with_for_update().all())
    missing = NUTRITION_CORRECTIONS.keys() - {row.ingredient_id for row in rows}
    if missing:
        raise ValueError(f"Missing T007 nutrient rows: {sorted(missing)}")
    changes = []
    for row in rows:
        original, corrected = NUTRITION_CORRECTIONS[row.ingredient_id]
        current = (row.energy_kcal_100g, row.protein_g_100g, row.fat_g_100g, row.carbs_g_100g)
        if current == original:
            changes.append((row, corrected))
        elif current != corrected:
            raise ValueError(f"Unexpected nutrient values for {row.ingredient_id}; review before applying T007.")
    for row, corrected in changes:
        row.energy_kcal_100g, row.protein_g_100g, row.fat_g_100g, row.carbs_g_100g = corrected
    return len(changes)


R120_STEP_CORRECTIONS = {
    1: (
        "Po upieczeniu buraków, gdy slightly ostygną, obierz je i pokrój w cienkie plastry.",
        "Po upieczeniu buraków, gdy lekko ostygną, obierz je i pokrój w cienkie plastry.",
    ),
    4: (
        "Podawaj od razu, dekorując świeżymi ziołami, jeśli masz pod ręką.",
        "Podawaj od razu.",
    ),
}


def curate_r120_steps(db):
    recipe = db.get(Recipe, "R120")
    if recipe is None:
        raise ValueError("Recipe R120 is missing; cannot apply instruction corrections.")
    steps = recipe.steps_pl
    if not isinstance(steps, list) or len(steps) != 5:
        raise ValueError("Recipe R120 instructions changed; manual review required.")
    for index, (original, corrected) in R120_STEP_CORRECTIONS.items():
        if steps[index] not in (original, corrected):
            raise ValueError(f"Recipe R120 step {index + 1} changed; manual review required.")
    updated = list(steps)
    for index, (_, corrected) in R120_STEP_CORRECTIONS.items():
        updated[index] = corrected
    if updated != steps:
        recipe.steps_pl = updated


def apply_recipe_curation():
    db = SessionLocal()
    try:
        curate_r120_steps(db)
        db.commit()
        print("Applied R120 instruction corrections; ingredients and nutrition unchanged.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
LACTOSE_CONCEPT_POLICY_PATH = CURATION_DIR / "lactose_concept_policy.csv"
WINIARY_SKU_LACTOSE_POLICY_PATH = CURATION_DIR / "winiary_sku_lactose_policy.csv"


def ensure_lactose_free_columns():
    with engine.begin() as connection:
        for table_name in ("diet_policies", "client_skus"):
            connection.execute(text(
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS is_lactose_free INTEGER"
            ))


def load_lactose_statuses(path, id_field):
    statuses = {}
    required = {id_field, "is_lactose_free"}
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing lactose policy columns in {path.name}")
        for row in reader:
            record_id = (row[id_field] or "").strip()
            value = (row["is_lactose_free"] or "").strip()
            if not record_id or record_id in statuses:
                raise ValueError(f"Empty or duplicate lactose policy ID: {record_id!r}")
            if value not in ("", "0", "1"):
                raise ValueError(f"Invalid lactose policy value for {record_id}: {value!r}")
            statuses[record_id] = None if value == "" else int(value)
    if not statuses:
        raise ValueError(f"Empty lactose policy: {path.name}")
    return statuses


def validate_lactose_policy_ids(statuses, database_ids, label):
    missing = sorted(database_ids - statuses.keys())
    unknown = sorted(statuses.keys() - database_ids)
    if missing or unknown:
        raise ValueError(f"Lactose {label} policy ID mismatch: missing={missing}, unknown={unknown}")


def curate_lactose_free_policies(db, client_id):
    concept_statuses = load_lactose_statuses(LACTOSE_CONCEPT_POLICY_PATH, "concept_id")
    sku_statuses = load_lactose_statuses(WINIARY_SKU_LACTOSE_POLICY_PATH, "client_sku_id")
    ingredient_ids = {row.id for row in db.query(Ingredient).all()}
    policies = db.query(DietPolicy).all()
    skus = db.query(ClientSku).filter(ClientSku.client_id == client_id).all()
    validate_lactose_policy_ids(concept_statuses, ingredient_ids, "concept")
    validate_lactose_policy_ids(concept_statuses, {row.ingredient_id for row in policies}, "diet")
    validate_lactose_policy_ids(sku_statuses, {row.id for row in skus}, "SKU")

    # Validate both files and their entire scope before assigning any values.
    for policy in policies:
        policy.is_lactose_free = concept_statuses[policy.ingredient_id]
    for sku in skus:
        sku.is_lactose_free = sku_statuses[sku.id]


def apply_lactose_curation():
    ensure_lactose_free_columns()
    db = SessionLocal()
    try:
        client = get_required_client(db)
        curate_lactose_free_policies(db, client.id)
        db.commit()
        print("Applied lactose-free concept and SKU policies (unknown values remain NULL).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

BROTH_RULES = [
    {
        "rule_order": 1,
        "condition_type": "diet",
        "condition_value": "vegan",
        "preferred_sku_id": VEGETABLE_BROTH_SKU_ID,
    },
    {
        "rule_order": 2,
        "condition_type": "diet",
        "condition_value": "vegetarian",
        "preferred_sku_id": VEGETABLE_BROTH_SKU_ID,
    },
]


def ensure_gluten_free_columns():
    table_columns = {
        table_name: {column["name"] for column in inspect(engine).get_columns(table_name)}
        for table_name in ("diet_policies", "client_skus")
    }

    with engine.begin() as connection:
        if "is_gluten_free" not in table_columns["diet_policies"]:
            connection.execute(text("ALTER TABLE diet_policies ADD COLUMN is_gluten_free INTEGER"))
        if "is_gluten_free" not in table_columns["client_skus"]:
            connection.execute(text("ALTER TABLE client_skus ADD COLUMN is_gluten_free INTEGER"))


def load_gluten_unsafe_concept_ids() -> set[str]:
    with GLUTEN_UNSAFE_CONCEPTS_PATH.open("r", encoding="utf-8", newline="") as file:
        return {str(row["concept_id"]).strip() for row in csv.DictReader(file)}


def curate_gluten_free_concepts(db):
    unsafe_concept_ids = load_gluten_unsafe_concept_ids()
    policies = db.query(DietPolicy).all()

    unexpected_ids = []
    for policy in policies:
        concept_id = str(policy.ingredient_id or "").strip()
        try:
            concept_number = int(concept_id.removeprefix("C"))
        except ValueError:
            unexpected_ids.append(concept_id)
            continue
        if not concept_id.startswith("C") or concept_number > GLUTEN_POLICY_MAX_CONCEPT_NUMBER:
            unexpected_ids.append(concept_id)

    if unexpected_ids:
        raise ValueError(
            "Gluten policy requires manual classification for concepts: "
            f"{sorted(unexpected_ids)}"
        )

    for policy in policies:
        policy.is_gluten_free = 0 if policy.ingredient_id in unsafe_concept_ids else 1


def load_gluten_free_sku_statuses() -> dict[str, int]:
    with WINIARY_SKU_GLUTEN_POLICY_PATH.open("r", encoding="utf-8", newline="") as file:
        statuses = {
            str(row["client_sku_id"]).strip(): int(row["is_gluten_free"])
            for row in csv.DictReader(file)
        }

    invalid = sorted(sku_id for sku_id, value in statuses.items() if value not in (0, 1))
    if invalid:
        raise ValueError(f"Invalid SKU gluten policy values: {invalid}")
    return statuses


def curate_gluten_free_skus(db, client_id: int):
    statuses = load_gluten_free_sku_statuses()

    client_skus = db.query(ClientSku).filter(ClientSku.client_id == client_id).all()
    missing_source_ids = sorted(sku.id for sku in client_skus if sku.id not in statuses)
    if missing_source_ids:
        raise ValueError(f"SKU gluten policy is missing source rows: {missing_source_ids}")

    for sku in client_skus:
        sku.is_gluten_free = statuses[sku.id]


def get_required_client(db):
    client = db.query(Client).filter(Client.name == CLIENT_NAME).first()
    if client is None:
        raise ValueError(f"Client not found: {CLIENT_NAME}")
    return client


def validate_required_sku(db, client_id):
    sku = db.query(ClientSku).filter(ClientSku.id == VEGETABLE_BROTH_SKU_ID).first()
    if sku is None:
        raise ValueError(f"SKU not found: {VEGETABLE_BROTH_SKU_ID}")
    if sku.client_id != client_id:
        raise ValueError(f"SKU {VEGETABLE_BROTH_SKU_ID} does not belong to client {client_id}")
    if sku.concept_id != BROTH_CONCEPT_ID:
        raise ValueError(f"SKU {VEGETABLE_BROTH_SKU_ID} is not mapped to concept {BROTH_CONCEPT_ID}")


def upsert_rule(db, client_id, rule_data):
    rule = (
        db.query(SkuSelectionRule)
        .filter(
            SkuSelectionRule.client_id == client_id,
            SkuSelectionRule.concept_id == BROTH_CONCEPT_ID,
            SkuSelectionRule.condition_type == rule_data["condition_type"],
            SkuSelectionRule.condition_value == rule_data["condition_value"],
        )
        .first()
    )

    if rule is None:
        rule = (
            db.query(SkuSelectionRule)
            .filter(
                SkuSelectionRule.client_id == client_id,
                SkuSelectionRule.concept_id == BROTH_CONCEPT_ID,
                SkuSelectionRule.rule_order == rule_data["rule_order"],
                SkuSelectionRule.condition_type.is_(None),
                SkuSelectionRule.condition_value.is_(None),
            )
            .first()
        )

    if rule is None:
        rule = SkuSelectionRule(client_id=client_id, concept_id=BROTH_CONCEPT_ID)
        db.add(rule)

    rule.rule_order = rule_data["rule_order"]
    rule.condition_type = rule_data["condition_type"]
    rule.condition_value = rule_data["condition_value"]
    rule.preferred_sku_id = rule_data["preferred_sku_id"]
    return rule


def migrate_supported_preference_rule_types(db):
    diet_values = {"vegetarian", "vegan", "pescetarian"}
    protein_values = {"meat", "fish"}

    legacy_rules = db.query(SkuSelectionRule).filter(SkuSelectionRule.condition_type == "user_pref").all()
    for rule in legacy_rules:
        condition_value = str(rule.condition_value or "").strip()
        if condition_value in diet_values:
            rule.condition_type = "diet"
        elif condition_value in protein_values:
            rule.condition_type = "protein_preference"


def deduplicate_supported_preference_rules(db):
    supported_types = {"diet", "protein_preference"}
    rules = (
        db.query(SkuSelectionRule)
        .filter(SkuSelectionRule.condition_type.in_(supported_types))
        .order_by(SkuSelectionRule.id)
        .all()
    )

    seen = set()
    for rule in rules:
        key = (rule.client_id, rule.concept_id, rule.condition_type, rule.condition_value)
        if key in seen:
            db.delete(rule)
        else:
            seen.add(key)


def move_default_broth_rule_after_diet_rules(db, client_id):
    default_rules = (
        db.query(SkuSelectionRule)
        .filter(
            SkuSelectionRule.client_id == client_id,
            SkuSelectionRule.concept_id == BROTH_CONCEPT_ID,
            SkuSelectionRule.condition_type == "default",
            SkuSelectionRule.condition_value == "any",
        )
        .all()
    )

    for rule in default_rules:
        if rule.rule_order is None or rule.rule_order < 3:
            rule.rule_order = 3


def apply_curation():
    ensure_gluten_free_columns()
    ensure_lactose_free_columns()
    db = SessionLocal()
    try:
        client = get_required_client(db)
        validate_required_sku(db, client.id)
        curate_gluten_free_concepts(db)
        curate_gluten_free_skus(db, client.id)
        curate_lactose_free_policies(db, client.id)
        migrate_supported_preference_rule_types(db)
        db.flush()

        for rule_data in BROTH_RULES:
            upsert_rule(db, client.id, rule_data)
        move_default_broth_rule_after_diet_rules(db, client.id)
        db.flush()
        deduplicate_supported_preference_rules(db)
        curate_r120_steps(db)
        curate_concept_nutrition(db)
        curate_recipe_volumes(db)

        db.commit()
        print("Applied preference rules, diet policies, recipe and nutrient corrections.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--lactose-only", action="store_true", help="Import only lactose policies.")
    mode.add_argument("--recipes-only", action="store_true", help="Apply only recipe instruction corrections.")
    mode.add_argument("--nutrition-only", action="store_true", help="Replay the four T007 nutrient corrections.")
    mode.add_argument("--volumes-only", action="store_true", help="Apply T030 recipe volume variants.")
    args = parser.parse_args()
    if args.volumes_only:
        with SessionLocal.begin() as db:
            changed = curate_recipe_volumes(db)
        print(f"T030: updated volume variants in {changed} recipes.")
    elif args.lactose_only:
        apply_lactose_curation()
    elif args.recipes_only:
        apply_recipe_curation()
    elif args.nutrition_only:
        with SessionLocal.begin() as db:
            changed = curate_concept_nutrition(db)
        print(f"T007: updated {changed} nutrient rows.")
    else:
        apply_curation()
