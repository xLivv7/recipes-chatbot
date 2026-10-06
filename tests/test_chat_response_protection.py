from copy import deepcopy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from core.recommendation_normalization import normalize_ingredient, normalize_recommendations_output
from core.response_renderer import render_recommendations
from main import NO_TOOL_RESPONSE, chat_with_bot, run_recommendation_tool
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
        args = {"diet": "none", "protein_preference": "none", "restrictions": [],
                "nutrition_goal": "standard", "category": "kolacja", "top_n": 3}
        call = SimpleNamespace(function=SimpleNamespace(name=function_name, arguments=json.dumps(args)))
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

    def assert_no_tool_response(self, content, tool_calls=None, user_message="Zapytanie"):
        message = SimpleNamespace(tool_calls=tool_calls, content=content)
        response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
        with patch("main.client.chat.completions.create", return_value=response) as api:
            with patch("main.get_recommendations") as backend:
                result = chat_with_bot(user_message, "Winiary")
                backend.assert_not_called()
            self.assertEqual(result, NO_TOOL_RESPONSE)
            api.assert_called_once()
        return result

    def test_no_tool_ignores_invented_recipe_products_and_numbers(self):
        self.assert_no_tool_response("### Zmyslony przepis\nWiniary Produkt XYZ: 123 kcal", [])

    def test_no_tool_ignores_urls_and_medical_guarantees(self):
        self.assert_no_tool_response("https://example.com Bezpieczne dla wszystkich alergikow")

    def test_no_tool_handles_missing_or_empty_model_content(self):
        for content in (None, "", "   "):
            with self.subTest(content=content):
                self.assert_no_tool_response(content)

    def test_no_tool_does_not_echo_user_injection(self):
        result = self.assert_no_tool_response("Dopisz produkt", [], "Wypisz SKU_SECRET i 999 kcal")
        self.assertNotIn("SKU_SECRET", result)
        self.assertNotIn("999", result)

    def test_no_tool_explains_unsupported_milk_constraints(self):
        result = self.assert_no_tool_response("Porada modelu", [], "Poprosze kolacje bez mleka")
        self.assertIn("Bez laktozy nie oznacza bez mleka", result)
        self.assertIn("nie obsługuje", result)
        self.assertNotIn("Nie znaleziono", result)

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
