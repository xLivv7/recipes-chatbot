from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from core.database import ClientSku, DietPolicy, Recipe
from core.recommendation_catalog import load_recipe_catalog
from core.validation.context import ValidationContext
from core.validation.models import Severity
from core.validation.validators_branding import validate_branding
from core.validation.validators_diet import validate_diet_policies


class LactoseCatalogValidationTests(unittest.TestCase):
    def context(self, status):
        return ValidationContext(
            ingredients=[], nutrients=[], clients=[], sku_selection_rules=[],
            diet_policies=[DietPolicy(ingredient_id="C", is_lactose_free=status)],
            client_skus=[ClientSku(id="SKU", concept_id="C", is_lactose_free=status)],
            recipes=[Recipe(id="R", ingredients_data=[{"concept_id": "C", "grams": 100}])],
        )

    def lactose_issues(self, status):
        ctx = self.context(status)
        return [i for i in validate_diet_policies(ctx) + validate_branding(ctx)
                if i.field == "is_lactose_free"]

    def test_null_is_warning_for_used_concept_and_sku_not_error(self):
        issues = self.lactose_issues(None)
        self.assertEqual(len(issues), 2)
        self.assertTrue(all(i.severity == Severity.WARNING for i in issues))

    def test_invalid_flags_are_errors(self):
        issues = self.lactose_issues(2)
        self.assertEqual(len(issues), 2)
        self.assertTrue(all(i.severity == Severity.ERROR for i in issues))

    def test_confirmed_states_have_no_lactose_issues(self):
        for status in (0, 1):
            self.assertEqual(self.lactose_issues(status), [])

    def test_unused_unknown_records_do_not_raise_lactose_warnings(self):
        ctx = self.context(None)
        ctx.recipes.clear()
        issues = validate_diet_policies(ctx) + validate_branding(ctx)
        self.assertFalse(any(i.field == "is_lactose_free" for i in issues))

    def test_loader_preserves_all_three_states(self):
        for status in (None, 0, 1):
            db = MagicMock()
            policy = SimpleNamespace(ingredient_id="C", is_lactose_free=status,
                                     is_vegetarian_ok=1, is_vegan_ok=1, is_meat=0,
                                     is_fish=0, is_keto_ok=1, is_gluten_free=1)
            sku = ClientSku(id="SKU", concept_id="C", is_lactose_free=status)
            db.query.side_effect = lambda model: MagicMock(all=MagicMock(
                return_value=[policy] if model is DietPolicy else [sku] if model is ClientSku else []))
            with patch("core.recommendation_catalog.SessionLocal", return_value=db):
                catalog = load_recipe_catalog()
            self.assertEqual(catalog.diet_policy_by_concept["C"]["is_lactose_free"], status)
            self.assertEqual(catalog.skus_by_id["SKU"]["is_lactose_free"], status)
            db.close.assert_called_once()
