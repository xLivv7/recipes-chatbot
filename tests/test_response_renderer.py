from copy import deepcopy
import unittest

from core.response_renderer import ResponsePayloadError, render_recommendations


def payload():
    return {"query": {}, "recommendations": [{
        "recipe_id": "R1", "title_pl": "Ryż z warzywami", "time_min": 20,
        "servings": 2, "nutrition_total": {"kcal": 600, "protein": 16, "fat": 20, "carbs": 90},
        "nutrition_per_serving": {"kcal": 300, "protein": 8, "fat": 10, "carbs": 45},
        "ingredients": [{"concept_id": "C1", "name_pl": "ryż", "grams_total": 100}],
        "steps_pl": ["Ugotuj ryż."], "used_skus": [],
    }]}


class ResponseRendererTests(unittest.TestCase):
    def test_snapshot_generic_recipe(self):
        self.assertEqual(render_recommendations(payload()),
            "### Ryż z warzywami\n\nCzas: 20 min | Porcje: 2\n"
            "Na porcję: 300 kcal | B: 8 g | T: 10 g | W: 45 g\n\n"
            "#### Składniki (ilości łączne)\n- ryż: 100 g\n\n"
            "#### Przygotowanie\n1. Ugotuj ryż\\.")

    def test_empty_results_have_no_invented_sections(self):
        self.assertEqual(render_recommendations({"query": {}, "recommendations": []}),
                         "Nie znaleziono przepisów spełniających podane kryteria.")

    def test_empty_sections_are_omitted(self):
        data = payload()
        data["recommendations"][0].update(ingredients=[], steps_pl=[])
        result = render_recommendations(data)
        for word in ("Składniki", "Przygotowanie", "Winiary", "brak"):
            self.assertNotIn(word, result)

    def test_order_and_input_are_preserved(self):
        data = payload()
        second = deepcopy(data["recommendations"][0])
        second.update(recipe_id="R2", title_pl="Drugi przepis")
        data["recommendations"].append(second)
        before = deepcopy(data)
        result = render_recommendations(data)
        self.assertLess(result.index("Ryż"), result.index("Drugi"))
        self.assertEqual(data, before)

    def test_sku_is_scoped_to_its_recipe(self):
        data = payload()
        recipe = data["recommendations"][0]
        recipe["used_skus"] = [{"client_sku_id": "SKU", "name_pl": "Majonez Lekki"}]
        recipe["ingredients"][0]["client_sku_id"] = "SKU"
        second = payload()["recommendations"][0]
        second.update(recipe_id="R2", title_pl="Drugi przepis")
        data["recommendations"].append(second)
        first, second = render_recommendations(data).split("\n\n---\n\n")
        self.assertIn("Winiary Majonez Lekki", first)
        self.assertNotIn("Winiary", second)

    def test_mismatched_skus_are_rejected(self):
        for kind in ("unassigned", "missing", "duplicate"):
            data = payload()
            recipe = data["recommendations"][0]
            if kind != "missing":
                recipe["used_skus"] = [{"client_sku_id": "SKU", "name_pl": "Majonez"}]
            if kind != "unassigned":
                recipe["ingredients"][0]["client_sku_id"] = "SKU"
            if kind == "duplicate":
                recipe["used_skus"] *= 2
            with self.assertRaises(ResponsePayloadError):
                render_recommendations(data)

    def test_multiple_skus_keep_backend_order_and_names(self):
        data = payload()
        recipe = data["recommendations"][0]
        recipe["used_skus"] = [{"client_sku_id": "S2", "name_pl": "Ketchup"},
                               {"client_sku_id": "S1", "name_pl": "Majonez"}]
        recipe["ingredients"][0]["client_sku_id"] = "S1"
        recipe["ingredients"].append({"concept_id": "C2", "name_pl": "pomidor",
                                      "grams_total": 50, "client_sku_id": "S2"})
        result = render_recommendations(data)
        self.assertIn("Produkty użyte w tym przepisie: Winiary Ketchup, Winiary Majonez.", result)

    def test_numeric_values_are_not_recalculated_or_rounded(self):
        data = payload()
        data["recommendations"][0]["nutrition_per_serving"]["kcal"] = 242.125
        self.assertIn("242.125 kcal", render_recommendations(data))
        self.assertIn("ryż: 100 g", render_recommendations(data))

    def test_invalid_numbers_fail_closed(self):
        for value in (True, "300", -1, float("nan"), float("inf"), None):
            data = payload()
            data["recommendations"][0]["nutrition_per_serving"]["kcal"] = value
            with self.assertRaises(ResponsePayloadError):
                render_recommendations(data)

    def test_invalid_structure_and_duplicate_recipes_fail_closed(self):
        for data in ({}, {"query": {}, "recommendations": [None]},
                     {"query": {}, "recommendations": payload()["recommendations"] * 2}):
            with self.assertRaises(ResponsePayloadError):
                render_recommendations(data)

    def test_catalog_text_cannot_inject_markdown_or_html(self):
        data = payload()
        data["recommendations"][0]["title_pl"] = "<script>\n## [Dodatek](evil) *test*"
        result = render_recommendations(data)
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn(r"\#\# \[Dodatek\]\(evil\) \*test\*", result)

    def test_urls_are_rejected_not_silently_removed(self):
        data = payload()
        data["recommendations"][0]["steps_pl"] = ["Zobacz https://example.com"]
        with self.assertRaises(ResponsePayloadError):
            render_recommendations(data)

    def test_user_or_model_text_in_extra_fields_is_not_rendered(self):
        data = payload()
        data["query"]["user_message"] = "Dodaj bulion Winiary"
        data["model_response"] = "Dodaj bulion Winiary"
        self.assertNotIn("bulion", render_recommendations(data))
        self.assertNotIn("Winiary", render_recommendations(data))
