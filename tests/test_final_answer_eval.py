import unittest

from evals.run_final_answer_eval import DEFAULT_CASES_PATH, load_cases, score_case


class FinalAnswerEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in load_cases(DEFAULT_CASES_PATH)}

    def test_case_file_contains_unique_controlled_cases(self):
        self.assertEqual(len(self.cases), 4)
        self.assertEqual(set(self.cases), {"final_001", "final_002", "final_003", "final_004"})

    def test_score_case_accepts_grounded_answer(self):
        response = """## Kurczak z warzywami Eval
Czas: 25 min. Na porcję: 321 kcal | B: 35 g | T: 9 g | W: 24 g.
Dodaj Winiary Przyprawa Ziołowa.

## Tofu z kaszą Eval
Czas: 30 min. Na porcję: 294 kcal | B: 28 g | T: 10 g | W: 33 g."""

        result = score_case(self.cases["final_001"], response, "Winiary")

        self.assertTrue(result["passed"], result["errors"])

    def test_score_case_rejects_changed_nutrition_and_missing_sku(self):
        response = """## Kurczak z warzywami Eval
Czas: 25 min. Na porcję: 400 kcal | B: 35 g | T: 9 g | W: 24 g.

## Tofu z kaszą Eval
Czas: 30 min. Na porcję: 294 kcal | B: 28 g | T: 10 g | W: 33 g."""

        result = score_case(self.cases["final_001"], response, "Winiary")

        self.assertFalse(result["passed"])
        self.assertIn("missing or changed kcal per serving for Kurczak z warzywami Eval: 321", result["errors"])
        self.assertIn("missing promoted SKU: Przyprawa Ziołowa", result["errors"])

    def test_score_case_rejects_unsupported_gluten_claim(self):
        response = """## Ryż z warzywami Eval
Czas: 35 min. Na porcję: 380 kcal | B: 12 g | T: 11 g | W: 58 g.
To certyfikowany wybór dla celiakii. Dodaj Winiary Sos Pomidorowy Eval."""

        result = score_case(self.cases["final_003"], response, "Winiary")

        self.assertFalse(result["passed"])
        self.assertIn("forbidden claim or product: certyfikowany", result["errors"])
        self.assertIn("forbidden claim or product: dla celiakii", result["errors"])

    def test_score_case_accepts_markdown_wrapped_macro_labels(self):
        response = """## Ryż z warzywami Eval
**Czas przygotowania:** 35 min. **Kalorie:** 380 kcal.
**Białko:** 12 g | **Tłuszcz:** 11 g | **Węglowodany:** 58 g.
Dodaj Winiary Sos Pomidorowy."""

        result = score_case(self.cases["final_003"], response, "Winiary")

        self.assertTrue(result["passed"], result["errors"])

    def test_score_case_accepts_explicit_no_results_message(self):
        result = score_case(
            self.cases["final_004"],
            "Nie znalazłem w bazie propozycji spełniających te kryteria.",
            "Winiary",
        )

        self.assertTrue(result["passed"], result["errors"])


if __name__ == "__main__":
    unittest.main()
