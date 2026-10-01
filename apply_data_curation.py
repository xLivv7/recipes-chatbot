"""Idempotent data curation entrypoint for reproducible database fixes.

Add future data corrections as separate functions and call them from
apply_curation(), so each manual data decision can be replayed after a
database rebuild.
"""

import argparse
import csv
from pathlib import Path

from sqlalchemy import inspect, text

from core.database import Client, ClientSku, DietPolicy, Ingredient, SessionLocal, SkuSelectionRule, engine


CLIENT_NAME = "Winiary"
BROTH_CONCEPT_ID = "C007"
VEGETABLE_BROTH_SKU_ID = "WINIARY_BULION_WARZYWNY_SLOIK_160G"
CURATION_DIR = Path(__file__).resolve().parent / "curation"
GLUTEN_UNSAFE_CONCEPTS_PATH = CURATION_DIR / "gluten_unsafe_concepts.csv"
WINIARY_SKU_GLUTEN_POLICY_PATH = CURATION_DIR / "winiary_sku_gluten_policy.csv"
GLUTEN_POLICY_MAX_CONCEPT_NUMBER = 376
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

        db.commit()
        print("Applied preference rules, gluten-free and lactose-free policy curation.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lactose-only", action="store_true", help="Import only lactose policies.")
    args = parser.parse_args()
    if args.lactose_only:
        apply_lactose_curation()
    else:
        apply_curation()
