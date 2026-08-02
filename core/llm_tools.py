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
                        "enum": ["none", "vege", "vegetarian", "vegan", "meat", "fish", "pescetarian"],
                        "description": "Preferencja dietetyczna użytkownika. Jeśli użytkownik nic nie wspomina o diecie, użyj 'none'."
                    },
                    "nutrition_goal": {
                        "type": "string",
                        "enum": ["standard", "low_kcal", "high_protein", "keto"],
                        "description": "Cel sylwetkowy/żywieniowy. Jeśli użytkownik prosi o coś lekkiego/na redukcję użyj 'low_kcal'. Dla dużej ilości białka użyj 'high_protein'. Dla diety ketogenicznej użyj 'keto'. Jeśli brak wytycznych, użyj 'standard'."
                    },
                    "category": {
                        "type": "string",
                        "enum": ["śniadanie", "lunch", "obiad", "kolacja", "deser", "przekąska"],
                        "description": "Rodzaj posiłku z kontrolowanego słownika. Jeśli użytkownik mówi dosłownie 'lunch', zawsze użyj 'lunch' i nie tłumacz tego na 'obiad'. Jeśli użytkownik mówi 'obiad', użyj 'obiad'. Jeśli użytkownik nie sprecyzuje rodzaju posiłku, domyślnie użyj 'kolacja'."
                    },
                    "time_max": {
                        "type": "integer",
                        "description": "Maksymalny czas przygotowania w minutach. Ustawiaj tylko wtedy, gdy użytkownik jawnie podaje limit czasu (np. 'do 15 minut', 'do 30 minut') albo prosi o coś szybkiego/na szybko/ekspresowego; wtedy użyj rozsądnego domyślnego limitu 30 minut, jeśli nie podał liczby. Nie ustawiaj time_max tylko dlatego, że użytkownik prosi o coś lekkiego, fit, niskokalorycznego, na redukcję, keto lub wysokobiałkowego. Jeśli brak jawnego ograniczenia czasu lub szybkości, pomiń to pole."
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
