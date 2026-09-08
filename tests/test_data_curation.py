import unittest

from apply_data_curation import (
    load_gluten_free_sku_statuses,
    load_gluten_unsafe_concept_ids,
)
from core.database import ClientSku, SkuSelectionRule
from core.validation.context import ValidationContext
from core.validation.validators_branding import validate_branding


class GlutenFreeCurationTests(unittest.TestCase):
    def test_reviewed_sku_policy_contains_safe_and_blocked_products(self):
        statuses = load_gluten_free_sku_statuses()

        self.assertEqual(statuses["WINIARY_MAJONEZ_DEKORACYJNY_400ML"], 1)
        self.assertEqual(statuses["WINIARY_BULION_DROBIOWY_160G"], 0)

    def test_known_wheat_concept_is_in_unsafe_curation_set(self):
        self.assertIn("C030", load_gluten_unsafe_concept_ids())

    def test_gluten_free_rule_rejects_unsafe_sku(self):
        sku = ClientSku(id="SKU_TEST", client_id=1, concept_id="C001", is_gluten_free=0)
        rule = SkuSelectionRule(
            id=1,
            client_id=1,
            concept_id="C001",
            rule_order=1,
            condition_type="restriction",
            condition_value="gluten_free",
            preferred_sku_id="SKU_TEST",
        )
        context = ValidationContext(
            ingredients=[],
            nutrients=[],
            diet_policies=[],
            clients=[],
            client_skus=[sku],
            sku_selection_rules=[rule],
            recipes=[],
        )

        issues = validate_branding(context)

        self.assertTrue(any("Gluten-free rule" in item.message for item in issues), issues)


if __name__ == "__main__":
    unittest.main()
