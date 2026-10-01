from types import SimpleNamespace
import unittest

from core.recommendations import concept_allows_restrictions


class LactoseRecipeFilterTests(unittest.TestCase):
    def catalog(self, policy):
        return SimpleNamespace(diet_policy_by_concept={} if policy is None else {"C": policy})

    def test_only_explicit_one_passes_lactose_restriction(self):
        for status in (0, None, 2, "1"):
            with self.subTest(status=status):
                self.assertFalse(concept_allows_restrictions(
                    "C", ["lactose_free"], self.catalog({"is_lactose_free": status})))
        self.assertTrue(concept_allows_restrictions(
            "C", ["lactose_free"], self.catalog({"is_lactose_free": 1})))

    def test_missing_policy_or_flag_is_not_allowed(self):
        for policy in (None, {}):
            self.assertFalse(concept_allows_restrictions("C", ["lactose_free"], self.catalog(policy)))

    def test_combined_restrictions_require_both_flags(self):
        for gluten, lactose, expected in ((1, 1, True), (0, 1, False), (1, 0, False), (1, None, False)):
            policy = {"is_gluten_free": gluten, "is_lactose_free": lactose}
            self.assertEqual(concept_allows_restrictions(
                "C", ["gluten_free", "lactose_free"], self.catalog(policy)), expected)

    def test_no_restriction_does_not_filter_unknown_concept(self):
        self.assertTrue(concept_allows_restrictions("C", [], self.catalog(None)))
