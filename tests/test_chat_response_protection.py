from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.recommendation_normalization import normalize_ingredient, normalize_recommendations_output
from core.response_renderer import render_recommendations
from main import chat_with_bot, run_recommendation_tool
from test_response_renderer import payload


class ChatResponseProtectionTests(unittest.TestCase):
    def test_normalization_preserves_sku_assignment_without_mutation(self):
        ingredient = {"concept_id": "C1", "name_pl": "ryz", "grams_total": 100,
                      "client_sku_id": "S1", "client_sku_name_pl": "Produkt"}
        before = deepcopy(ingredient)
        normalized = normalize_ingredient(ingredient)
        self.assertEqual(normalized["client_sku_id"], "S1")
        self.assertEqual(normalized["client_sku_name_pl"], "Produkt")
        self.assertEqual(ingredient, before)

    def test_generic_ingredient_does_not_gain_sku(self):
        self.assertNotIn("client_sku_id", normalize_ingredient({"name_pl": "ryz"}))

    def call_chat(self, data, function_name="get_recommendations"):
        call = SimpleNamespace(function=SimpleNamespace(name=function_name, arguments="{}"))
        message = SimpleNamespace(tool_calls=[call], content="Invented product")
        response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
        with patch("main.client.chat.completions.create", return_value=response) as api:
            with patch("main.get_recommendations", return_value=data) as backend:
                result = chat_with_bot("Dodaj wymyslony produkt", "Winiary")
            api.assert_called_once()
        return result, backend.call_count

    def test_chat_renders_backend_without_second_llm_call(self):
        data = payload()
        recipe = data["recommendations"][0]
        recipe["ingredients"][0]["client_sku_id"] = "S1"
        recipe["used_skus"] = [{"client_sku_id": "S1", "name_pl": "Produkt"}]
        result, count = self.call_chat(data)
        self.assertEqual(count, 1)
        self.assertEqual(result, render_recommendations(normalize_recommendations_output(data)))
        self.assertNotIn("Invented", result)

    def test_empty_results_are_rendered_without_llm(self):
        result, _ = self.call_chat({"query": {}, "recommendations": []})
        self.assertIn("Nie znaleziono", result)

    def test_invalid_sku_fails_closed(self):
        data = payload()
        data["recommendations"][0]["used_skus"] = [{"client_sku_id": "S1", "name_pl": "Produkt"}]
        with self.assertLogs("main", level="ERROR"):
            result, _ = self.call_chat(data)
        self.assertIn("niespójnych danych", result)
        self.assertNotIn("Produkt", result)

    def test_unknown_tool_does_not_call_backend(self):
        result, count = self.call_chat(payload(), "unknown")
        self.assertEqual(count, 0)
        self.assertIn("Nie udało", result)

    def test_no_tool_path_is_unchanged(self):
        message = SimpleNamespace(tool_calls=[], content="Doprecyzuj zapytanie")
        response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
        with patch("main.client.chat.completions.create", return_value=response) as api:
            self.assertEqual(chat_with_bot("Zapytanie", "Winiary"), message.content)
            api.assert_called_once()

    def test_real_database_normalized_results_can_be_rendered(self):
        for restrictions in ([], ["gluten_free"], ["lactose_free"], ["gluten_free", "lactose_free"]):
            with self.subTest(restrictions=restrictions):
                data = run_recommendation_tool({"category": "kolacja", "restrictions": restrictions})
                self.assertTrue(data["recommendations"])
                result = render_recommendations(data)
                self.assertIn("Na porcję:", result)
                for recipe in data["recommendations"]:
                    assigned = {i["client_sku_id"] for i in recipe["ingredients"] if i.get("client_sku_id")}
                    self.assertEqual(assigned, {s["client_sku_id"] for s in recipe["used_skus"]})
