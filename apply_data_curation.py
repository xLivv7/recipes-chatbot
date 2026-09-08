"""Idempotent data curation entrypoint for reproducible database fixes.

Add future data corrections as separate functions and call them from
apply_curation(), so each manual data decision can be replayed after a
database rebuild.
"""

from core.database import Client, ClientSku, SessionLocal, SkuSelectionRule


CLIENT_NAME = "Winiary"
BROTH_CONCEPT_ID = "C007"
VEGETABLE_BROTH_SKU_ID = "WINIARY_BULION_WARZYWNY_SLOIK_160G"

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
    db = SessionLocal()
    try:
        client = get_required_client(db)
        validate_required_sku(db, client.id)
        migrate_supported_preference_rule_types(db)
        db.flush()

        for rule_data in BROTH_RULES:
            upsert_rule(db, client.id, rule_data)
        move_default_broth_rule_after_diet_rules(db, client.id)
        db.flush()
        deduplicate_supported_preference_rules(db)

        db.commit()
        print("Applied C007 broth SKU curation rules.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    apply_curation()
