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
        "condition_type": "user_pref",
        "condition_value": "vegan",
        "preferred_sku_id": VEGETABLE_BROTH_SKU_ID,
    },
    {
        "rule_order": 2,
        "condition_type": "user_pref",
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

        for rule_data in BROTH_RULES:
            upsert_rule(db, client.id, rule_data)
        move_default_broth_rule_after_diet_rules(db, client.id)

        db.commit()
        print("Applied C007 broth SKU curation rules.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    apply_curation()
