import unittest
import argparse

from evals.run_final_answer_eval import DEFAULT_CASES_PATH, load_cases, score_case, sku_is_mentioned
from evals.legacy_final_answer_prompt import build_legacy_final_answer_prompt
from evals.run_final_answer_eval import summarize, positive_int


class FinalAnswerEvalTests(unittest.TestCase):
    def test_summary_distinguishes_persistent_and_intermittent_failures(self):
        trials = [
            {"id": case_id, "attempt": attempt, "passed": passed, "errors": [] if passed else ["failure"], "warnings": []}
            for case_id, outcomes in (("stable", [True, True]), ("mixed", [True, False]), ("failed", [False, False]))
            for attempt, passed in enumerate(outcomes, 1)
        ]
        result = summarize(trials)
        self.assertEqual(result["passed"], 3)
        self.assertEqual(result["stable_cases"], 1)
        self.assertEqual(result["case_results"]["mixed"]["failure_type"], "intermittent")
        self.assertEqual(result["case_results"]["failed"]["failure_type"], "persistent")
        self.assertEqual(result["attempt_results"]["1"]["passed"], 2)

    def test_repeat_count_must_be_positive(self):
        for value in ("0", "-1"):
            with self.assertRaises(argparse.ArgumentTypeError):
                positive_int(value)
        self.assertEqual(positive_int("3"), 3)

    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in load_cases(DEFAULT_CASES_PATH)}

    def test_case_file_contains_unique_controlled_cases(self):
        self.assertEqual(len(self.cases), 16)
        self.assertEqual(set(self.cases), {f"final_{index:03d}" for index in range(1, 17)})

    def test_prompt_omits_sections_missing_from_tool_payload(self):
        prompt = build_legacy_final_answer_prompt("Winiary")

        self.assertIn("całkowicie pomiń nagłówek i treść sekcji składników", prompt.casefold())
        self.assertIn(
            "nie dopisuj produktów, składników, zamienników, wariantów ani sugestii dodatków",
            prompt.casefold(),
        )
        self.assertIn("jeśli 'used_skus' jest puste, nie wspominaj marki ani żadnego produktu", prompt.casefold())
        self.assertIn("krytyczna kontrola przed odpowiedzią", prompt.casefold())

    def test_sku_match_accepts_polish_inflection(self):
        self.assertTrue(sku_is_mentioned("Sos Pomidorowy", "Użyj Sosu Pomidorowego Winiary."))
        self.assertTrue(sku_is_mentioned("Majonez Lekki", "Użyj Majonezu Lekkiego Winiary."))
        self.assertTrue(sku_is_mentioned("Sos Cytrynowy", "Użyj Sosu Cytrynowego Winiary."))
        for adjective in ("Ziołowa", "Śniadaniowa", "Grillowa"):
            with self.subTest(adjective=adjective):
                self.assertTrue(sku_is_mentioned(
                    "Przyprawa " + adjective, "Użyj Przyprawy " + adjective[:-1] + "ej Winiary."))

    def test_sku_match_rejects_scattered_words_and_similar_product(self):
        self.assertFalse(sku_is_mentioned("Sos Pomidorowy", "Sos czosnkowy. Pomidorowy smak."))
        self.assertFalse(sku_is_mentioned("Sos Pomidorowy", "Sos Pomidorowy Pikantny".replace("Pomidorowy", "Pomidorowaty")))

    def test_rejects_extra_ingredient_in_nonempty_payload(self):
        response = """### Omlet warzywny Eval
15 min. 260 kcal | B: 16 g | T: 17 g | W: 10 g.
#### Składniki
- Jajka Eval
- Szpinak Eval
- Bekon
#### Przygotowanie
Usmaż omlet.
Winiary Przyprawa Śniadaniowa."""
        result = score_case(self.cases["final_005"], response, "Winiary")
        self.assertTrue(any("unknown ingredient" in error for error in result["errors"]))

    def test_rejects_foreign_sku_even_when_expected_sku_is_present(self):
        response = """### Ryż z warzywami Eval
35 min. 380 kcal | B: 12 g | T: 11 g | W: 58 g.
Winiary Sos Pomidorowy.
Winiary Majonez Lekki."""
        result = score_case(self.cases["final_003"], response, "Winiary")
        self.assertTrue(any("unknown branded product" in error for error in result["errors"]))

    def test_rejects_additional_wrong_calories(self):
        response = """### Ryż z warzywami Eval
35 min. 380 kcal | B: 12 g | T: 11 g | W: 58 g.
Winiary Sos Pomidorowy. Kalorie: 1380 kcal."""
        result = score_case(self.cases["final_003"], response, "Winiary")
        self.assertIn("unexpected kcal value for Ryż z warzywami Eval", result["errors"])

    def test_rejects_macros_swapped_between_recipes(self):
        response = """### Kurczak z warzywami Eval
25 min. 294 kcal | B: 28 g | T: 10 g | W: 33 g.
Winiary Przyprawa Ziołowa.
### Tofu z kaszą Eval
30 min. 321 kcal | B: 35 g | T: 9 g | W: 24 g."""
        result = score_case(self.cases["final_001"], response, "Winiary")
        self.assertTrue(any("unexpected kcal" in error for error in result["errors"]))

    def test_score_case_rejects_sku_moved_to_another_recipe(self):
        response = """### 1. Łosoś z cukinią Eval
Czas: 28 min. 420 kcal | B: 31 g | T: 30 g | W: 8 g.

### 2. Sałatka jajeczna Eval
Czas: 12 min. 310 kcal | B: 18 g | T: 25 g | W: 5 g.
Użyj Winiary Sos Ziołowy i Winiary Majonez Lekki."""

        result = score_case(self.cases["final_006"], response, "Winiary")

        self.assertFalse(result["passed"])
        self.assertIn("missing promoted SKU: Sos Ziołowy", result["errors"])

    def test_score_case_rejects_changed_servings_when_stated(self):
        response = """### Makaron ryżowy z tuńczykiem Eval
Porcje: 2. Czas: 22 min. 390 kcal | B: 25 g | T: 10 g | W: 50 g.
Użyj Winiary Sosu Cytrynowego."""

        result = score_case(self.cases["final_007"], response, "Winiary")

        self.assertFalse(result["passed"])
        self.assertIn("changed servings for Makaron ryżowy z tuńczykiem Eval: 2", result["errors"])

    def test_score_case_rejects_unknown_recipe_heading(self):
        response = """### Inny deser Eval
Czas: 8 min. 220 kcal | B: 6 g | T: 16 g | W: 14 g."""

        result = score_case(self.cases["final_012"], response, "Winiary")

        self.assertFalse(result["passed"])
        self.assertIn("unknown recipe heading: Inny deser Eval", result["errors"])

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
