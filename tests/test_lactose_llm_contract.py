import unittest

from core.llm_tools import RECIPE_TOOLS
from evals.run_llm_eval import DEFAULT_CASES_PATH, build_eval_system_prompt, load_cases
from evals.run_final_answer_eval import DEFAULT_CASES_PATH as FINAL_PATH, load_cases as load_final, score_case, sku_is_mentioned
from main import build_system_prompt, run_recommendation_tool


class LactoseLlmContractTests(unittest.TestCase):
    def test_eval_uses_application_prompt(self):
        self.assertEqual(build_eval_system_prompt("Winiary"), build_system_prompt("Winiary"))

    def test_tool_exposes_both_restrictions(self):
        field = RECIPE_TOOLS[0]["function"]["parameters"]["properties"]["restrictions"]
        self.assertEqual(field["items"]["enum"], ["gluten_free", "lactose_free"])
        self.assertEqual(field["maxItems"], 2)
        self.assertTrue(field["uniqueItems"])

    def test_lactose_intent_cases_cover_positive_negative_and_combined_requests(self):
        cases = {c["id"]: c for c in load_cases(DEFAULT_CASES_PATH)}
        self.assertEqual(len(cases), 64)
        self.assertEqual(cases["intent_051"]["expected"]["restrictions"], ["lactose_free"])
        self.assertEqual(cases["intent_054"]["expected"]["restrictions"], ["gluten_free", "lactose_free"])
        self.assertEqual(cases["intent_061"]["expected"]["restrictions"], [])
        self.assertEqual(cases["intent_062"]["expected"]["restrictions"], [])

    def test_final_grader_rejects_selected_medical_guarantees(self):
        cases = {c["id"]: c for c in load_final(FINAL_PATH)}
        result = score_case(cases["final_014"], "To danie jest w 100% bezpieczna propozycja dla alergików.", "Winiary")
        self.assertTrue(any("forbidden claim" in e for e in result["errors"]))

    def test_tool_wrapper_passes_lactose_restrictions_to_backend(self):
        result = run_recommendation_tool({"restrictions": ["lactose_free"], "category": "kolacja", "top_n": 1})
        self.assertEqual(result["query"]["restrictions"], ["lactose_free"])
        self.assertTrue(result["recommendations"])

    def test_grader_accepts_expected_polish_noun_inflections(self):
        self.assertTrue(sku_is_mentioned("warzywa", "100 g warzyw"))
        self.assertTrue(sku_is_mentioned("mleko bez laktozy", "100 g mleka bez laktozy"))
        self.assertFalse(sku_is_mentioned("mleko bez laktozy", "100 g mleka kokosowego"))

    def test_grader_accepts_protein_genitive_without_changing_numbers(self):
        cases = {c["id"]: c for c in load_final(FINAL_PATH)}
        response = "### Ryż z warzywami Eval\n20 min | 300 kcal | 8 g białka | 10 g tłuszczu | 45 g węglowodanów"
        self.assertTrue(score_case(cases["final_013"], response, "Winiary")["passed"])
        self.assertFalse(score_case(cases["final_013"], response.replace("8 g białka", "9 g białka"), "Winiary")["passed"])
