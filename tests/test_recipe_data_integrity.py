from copy import deepcopy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_recommendations import build_catalog
from core.recommendation_errors import RecommendationDataError
from core.recommendations import get_recommendations, orchestrate_recipe, recipe_matches_preferences
from core.database import Recipe
from core.validation.context import ValidationContext
from core.validation.models import Severity
from core.validation.validators_diet import validate_diet_policies
from main import chat_with_bot


DATA_MESSAGE = 'Nie udało się przygotować przepisów z powodu niespójnych danych. Spróbuj ponownie później.'


class RecipeDataIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.catalog = build_catalog()
        self.catalog.recipes = self.catalog.recipes[:1]

    def query(self, **kwargs):
        return get_recommendations(catalog=self.catalog, **kwargs)

    def test_sc01_complete_catalog_keeps_facts_and_calculations(self):
        result = self.query()['recommendations'][0]
        self.assertEqual(result['recipe_id'], 'R_TEST')
        self.assertEqual(result['nutrition_total'], {'kcal': 6, 'protein': .2, 'fat': .3, 'carbs': .5})

    def test_sc02_explicit_incompatibility_continues_to_valid_candidate(self):
        rejected = deepcopy(self.catalog.recipes[0])
        rejected.update(recipe_id='BAD', ingredients=[{'concept_id': 'C_MEAT', 'grams': 100}])
        self.catalog.recipes.insert(0, rejected)
        self.assertEqual([r['recipe_id'] for r in self.query(diet='vegan')['recommendations']], ['R_TEST'])

    def test_sc03_missing_policy_fails_all_preference_dimensions(self):
        del self.catalog.diet_policy_by_concept['C007']
        for diet, protein in [('vegan', 'none'), ('vegetarian', 'none'),
                              ('pescetarian', 'none'), ('none', 'meat'),
                              ('none', 'fish'), ('none', 'none')]:
            with self.subTest(diet=diet, protein=protein), self.assertRaises(RecommendationDataError):
                self.query(diet=diet, protein_preference=protein)

    def test_sc04_direct_preparation_and_validator_detect_missing_policy(self):
        del self.catalog.diet_policy_by_concept['C007']
        with self.assertRaises(RecommendationDataError):
            orchestrate_recipe('R_TEST', catalog=self.catalog)
        ctx = ValidationContext(ingredients=[], nutrients=[], diet_policies=[], clients=[],
            client_skus=[], sku_selection_rules=[], recipes=[Recipe(id='R_TEST',
                ingredients_data=[{'concept_id': 'C007', 'grams': 100}])])
        issues = validate_diet_policies(ctx)
        self.assertTrue(any(i.record_id == 'C007' and i.severity == Severity.ERROR for i in issues))
        ctx.recipes.clear()
        self.assertEqual(validate_diet_policies(ctx), [])

    def test_sc05_missing_policy_cannot_hide_behind_rejected_ingredient(self):
        for ids in [('C_MEAT', 'MISSING'), ('MISSING', 'C_MEAT')]:
            self.catalog.recipes[0]['ingredients'] = [{'concept_id': c, 'grams': 10} for c in ids]
            with self.subTest(ids=ids), self.assertRaises(RecommendationDataError):
                self.query(diet='vegan')

    def test_sc06_legal_null_lactose_preserves_filter_and_generic_fallback(self):
        self.catalog.diet_policy_by_concept['C007']['is_lactose_free'] = None
        self.assertEqual(self.query(restrictions=['lactose_free'])['recommendations'], [])
        self.assertEqual(len(self.query()['recommendations']), 1)
        self.catalog.diet_policy_by_concept['C007']['is_lactose_free'] = 1
        for sku in self.catalog.skus_by_id.values():
            sku['is_lactose_free'] = None
        result = self.query(restrictions=['lactose_free'])['recommendations'][0]
        self.assertEqual(result['used_skus'], [])
        self.assertEqual(result['nutrition_total']['kcal'], 10)

    def test_sc07_failure_aborts_whole_query_in_both_candidate_orders(self):
        valid = deepcopy(self.catalog.recipes[0])
        broken = deepcopy(valid)
        broken.update(recipe_id='BROKEN', ingredients=[{'concept_id': 'C_MEAT', 'grams': 100}])
        del self.catalog.nutrients_by_concept['C_MEAT']
        for recipes in ([valid, broken], [broken, valid]):
            self.catalog.recipes = recipes
            with self.subTest(first=recipes[0]['recipe_id']), self.assertRaises(RecommendationDataError):
                self.query(top_n=1)

    def test_sc08_invalid_numbers_are_recognized_data_failures(self):
        for field in ('servings', 'grams'):
            for value in (0, -1, None, 'invalid', float('nan'), float('inf'), True):
                catalog = build_catalog()
                recipe = catalog.recipes[0]
                if field == 'grams':
                    recipe['ingredients'][0]['grams'] = value
                else:
                    recipe['servings'] = value
                with self.subTest(field=field, value=value), self.assertRaises(RecommendationDataError):
                    orchestrate_recipe('R_TEST', catalog=catalog)
        for use_sku in (False, True):
            for field in ('energy_kcal_100', 'protein_g_100', 'fat_g_100', 'carbs_g_100'):
                for value in (-1, None, 'invalid', float('nan'), float('inf'), True):
                    catalog = build_catalog()
                    if use_sku:
                        catalog.skus_by_id['CHICKEN_BROTH'][field] = value
                    else:
                        catalog.rules_by_concept.clear()
                        catalog.nutrients_by_concept['C007'][field + 'g'] = value
                    with self.subTest(sku=use_sku, field=field, value=value), self.assertRaises(RecommendationDataError):
                        orchestrate_recipe('R_TEST', catalog=catalog)

    def test_sc08_missing_macro_and_zero_macro(self):
        self.catalog.rules_by_concept.clear()
        del self.catalog.nutrients_by_concept['C007']['protein_g_100g']
        with self.assertRaises(RecommendationDataError):
            self.query()
        self.catalog.nutrients_by_concept['C007'] = dict.fromkeys(
            ['energy_kcal_100g', 'protein_g_100g', 'fat_g_100g', 'carbs_g_100g'], 0)
        self.assertEqual(self.query()['recommendations'][0]['nutrition_total'],
                         {'kcal': 0, 'protein': 0, 'fat': 0, 'carbs': 0})

    def test_sc08_broken_sku_references_fail_even_with_restrictions(self):
        for change in ('missing', 'concept', 'client', 'null_client', 'no_mapping'):
            catalog = build_catalog()
            rule = catalog.rules_by_concept['C007'][-1]
            if change in ('missing', 'no_mapping'):
                rule['preferred_sku_id'] = 'MISSING'
                if change == 'no_mapping':
                    catalog.concept_to_skus.clear()
            elif change == 'concept':
                catalog.skus_by_id['CHICKEN_BROTH']['concept_id'] = 'WRONG'
            else:
                catalog.skus_by_id['CHICKEN_BROTH']['client_id'] = None if change == 'null_client' else 99
            for restrictions in ([], ['gluten_free']):
                with self.subTest(change=change, restrictions=restrictions), self.assertRaises(RecommendationDataError):
                    orchestrate_recipe('R_TEST', restrictions=restrictions, catalog=catalog)

    def test_sc09_unexpected_preparation_error_propagates(self):
        with patch('core.recommendations.orchestrate_recipe', side_effect=RuntimeError('bug')):
            with self.assertRaisesRegex(RuntimeError, 'bug'):
                self.query()

    def test_sc10_normal_empty_result_is_not_data_error(self):
        self.assertEqual(self.query(category='obiad')['recommendations'], [])
        self.catalog.diet_policy_by_concept['C007']['is_vegan_ok'] = 0
        self.assertEqual(self.query(diet='vegan')['recommendations'], [])

    def test_sc11_out_of_scope_recipe_is_not_prepared(self):
        invalid = deepcopy(self.catalog.recipes[0])
        invalid.update(recipe_id='INVALID', ingredients=[{'concept_id': 'MISSING', 'grams': 1}])
        for changes, query in [({'category': 'obiad'}, {}), ({'time_min': 90}, {'time_max': 30})]:
            bad = dict(invalid, **changes)
            self.catalog.recipes = [bad, self.catalog.recipes[-1]]
            with self.subTest(changes=changes):
                self.assertEqual(len(self.query(**query)['recommendations']), 1)

    def test_sc12_chat_data_error_and_programming_error_have_distinct_boundaries(self):
        args = dict(diet='none', protein_preference='none', restrictions=[],
                    nutrition_goal='standard', category='kolacja', top_n=3)
        call = SimpleNamespace(function=SimpleNamespace(name='get_recommendations', arguments=json.dumps(args)))
        response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
        for error in (RecommendationDataError('missing_nutrients', recipe_id='R_TEST', concept_id='C007'),
                      RuntimeError('bug')):
            with patch('main.client.chat.completions.create', return_value=response) as api, \
                 patch('main.get_recommendations', side_effect=error), patch('main.render_recommendations') as render:
                if isinstance(error, RecommendationDataError):
                    with self.assertLogs('main', level='WARNING') as logs:
                        self.assertEqual(chat_with_bot('PRIVATE_QUERY', 'Winiary'), DATA_MESSAGE)
                    self.assertIn('missing_nutrients', ' '.join(logs.output))
                    self.assertIn('R_TEST', ' '.join(logs.output))
                    self.assertIn('C007', ' '.join(logs.output))
                    self.assertNotIn('PRIVATE_QUERY', ' '.join(logs.output))
                else:
                    with self.assertRaises(RuntimeError):
                        chat_with_bot('PRIVATE_QUERY', 'Winiary')
                api.assert_called_once()
                render.assert_not_called()
