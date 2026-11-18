"""T024 language-boundary contrasts; no SDK, application or database imports."""
import unittest

from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion


KNOWN_FALSE_BLOCKS = (
    "Nie musi być bez jaj, chcę kolację",
    "Bez laktozy i szybki obiad",
    "Kolacja bez mięsa, ryby mogą być",
    "Kolacja bez mięsa, chcę danie z rybą",
    "Kolacja bez mięsa, nie musi być z rybą",
)


class PreflightGrammarTests(unittest.TestCase):
    def test_five_known_supported_requests_are_released(self):
        for message in KNOWN_FALSE_BLOCKS:
            with self.subTest(message=message):
                self.assertFalse(mentions_unsupported_exclusion(message))

    def test_meal_clauses_cover_case_unicode_whitespace_and_conjunctions(self):
        for message in ("BEZ LAKTOZY I SZYBKI OBIAD", "bez\n\tlaktozy oraz szybka kolacja",
                        "bez glutenu i szybkie śniadanie", "bez laktozy i ekspresowy lunch",
                        "bez laktozy, szybki obiad", "bez mie\u0328sa, ryby moga\u0328 być",
                        "bez mięsa, ryby są dozwolone", "bez mięsa, chcę rybny lunch",
                        "bez mięsa, nie muszą być z rybą"):
            with self.subTest(message=message):
                self.assertFalse(mentions_unsupported_exclusion(message))

    def test_local_optional_exclusion_does_not_impose_a_requirement(self):
        for message in ("Nie musi być bez jaj", "Nie muszą być bez orzechów, chcę przekąski",
                        "bez laktozy, ale nie musi być bez mleka", "nie musi być bez ryb",
                        "nie musi być bez glutenu", "nie musi być bez produktów mięsnych"):
            with self.subTest(message=message):
                self.assertFalse(mentions_unsupported_exclusion(message))

    def test_additional_positive_exclusion_is_never_waived_by_a_released_clause(self):
        for prefix in KNOWN_FALSE_BLOCKS:
            for requirement in ("bez mleka", "bez jaj", "unikam orzechów", "bezmleczna kolacja"):
                message = prefix + ", ale " + requirement
                with self.subTest(message=message):
                    self.assertTrue(mentions_unsupported_exclusion(message))

    def test_elided_lists_and_ambiguous_negation_remain_blocked(self):
        for message in ("bez glutenu i jaj", "bez laktozy oraz mleka", "bez mięsa, ryb, jaj",
                        "bez mięsa, ryby, jaj", "bez glutenu, jaj i laktozy",
                        "nie musi być bez jaj i mleka", "nie musi być bez jaj, mleka",
                        "bez mięsa, nie mleka", "bez laktozy / mleka", "bez glutenu lub jaj",
                        "bez laktozy i na pewno mleka", "bez glutenu oraz do tego jaj"):
            with self.subTest(message=message):
                self.assertTrue(mentions_unsupported_exclusion(message))

    def test_new_clause_does_not_hide_another_exclusion(self):
        for message in ("bez laktozy i szybki obiad bez mleka", "bez mięsa, ryby mogą być bez jaj",
                        "bez mięsa, chcę danie bez mleka", "bez mięsa, nie jem jaj",
                        "bez mięsa, nie musi być z rybą, ale bez soi",
                        "nie musi być bez jaj, chcę kolację bez jaj",
                        "nie musi być bez jaj i bez orzechów"):
            with self.subTest(message=message):
                self.assertTrue(mentions_unsupported_exclusion(message))

    def test_other_negations_quotes_compounds_and_incomplete_exclusions_stay_conservative(self):
        for message in ("nie wymagam dania bez orzechów", "nie unikam mleka",
                        'Powiedziała: "nie musi być bez jaj", chcę kolację',
                        "„Nie musi być bez jaj”, chcę obiad", "nie musi być bezjajeczny",
                        "bez mleka", "bez ryb", "bez", "bez, proszę", "bez laktozy i"):
            with self.subTest(message=message):
                self.assertTrue(mentions_unsupported_exclusion(message))

    def test_supported_lists_keep_their_original_meaning(self):
        for message in ("bez glutenu i laktozy", "bez glutenu oraz bez laktozy",
                        "bez mięsa i ryb", "bez ryb i mięsa", "bez ryb i bez mięsa",
                        "bez produktów mięsnych", "bez ograniczeń", "bez limitu czasu"):
            with self.subTest(message=message):
                self.assertFalse(mentions_unsupported_exclusion(message))

    def test_allergy_mentions_still_block_even_beside_local_optional_exclusion(self):
        for message in ("Alergia na mleko, nie musi być bez jaj, chcę kolację",
                        "Nie mam alergii na jajka, bez laktozy i szybki obiad",
                        "Uczulenie na orzechy, kolacja bez mięsa, ryby mogą być"):
            with self.subTest(message=message):
                self.assertTrue(mentions_unsupported_allergy(message))


if __name__ == "__main__":
    unittest.main()
