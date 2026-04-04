# core/llm_tools.py

RECIPE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Wyszukuje i poleca przepisy kulinarne na podstawie zapytania użytkownika. Użyj tej funkcji zawsze, gdy użytkownik szuka pomysłu na posiłek, prosi o przepis lub chce coś ugotować.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_pref": {
                        "type": "string",
                        "enum": ["none", "vege", "vegetarian", "vegan", "meat", "fish"],
                        "description": "Preferencja dietetyczna użytkownika. Jeśli użytkownik nic nie wspomina o diecie, użyj 'none'."
                    },
                    "nutrition_goal": {
                        "type": "string",
                        "enum": ["standard", "low_kcal", "high_protein"],
                        "description": "Cel sylwetkowy/żywieniowy. Jeśli użytkownik prosi o coś lekkiego/na redukcję użyj 'low_kcal'. Dla dużej ilości białka użyj 'high_protein'. Jeśli brak wytycznych, użyj 'standard'."
                    },
                    "category": {
                        "type": "string",
                        "description": "Rodzaj posiłku, np. 'śniadanie', 'obiad', 'kolacja', 'deser', 'przekąska'. Jeśli użytkownik nie sprecyzuje, domyślnie użyj 'kolacja'."
                    },
                    "time_max": {
                        "type": "integer",
                        "description": "Maksymalny czas przygotowania w minutach, jeśli użytkownik prosi o coś szybkiego (np. 15, 30)."
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Liczba propozycji do wyszukania w bazie. Domyślnie użyj 3, chyba że użytkownik chce więcej/mniej."
                    }
                },
                "required": ["user_pref", "nutrition_goal", "category", "top_n"]
            }
        }
    }
]