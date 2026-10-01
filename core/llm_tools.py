from core.recommendation_preferences import DIETS, PROTEIN_PREFERENCES

# Expose lactose_free only after the separate LLM integration/evaluation stage.
LLM_SUPPORTED_RESTRICTIONS = ("gluten_free",)

RECIPE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Wyszukuje i poleca przepisy kulinarne na podstawie zapytania użytkownika. Użyj tej funkcji zawsze, gdy użytkownik szuka pomysłu na posiłek, prosi o przepis lub chce coś ugotować.",
            "parameters": {
                "type": "object",
                "properties": {
                    "diet": {
                        "type": "string",
                        "enum": list(DIETS),
                        "description": "Dieta użytkownika. Użyj 'vegetarian' dla diety bez mięsa i ryb, 'vegan' dla diety wegańskiej, 'pescetarian' gdy mięso jest wykluczone, ale ryby są dozwolone. Sama prośba o danie z rybą nie oznacza diety pescetariańskiej. Jeśli użytkownik nie określa diety, użyj 'none'."
                    },
                    "protein_preference": {
                        "type": "string",
                        "enum": list(PROTEIN_PREFERENCES),
                        "description": "Jawnie oczekiwane źródło białka. Użyj 'meat' tylko gdy użytkownik wprost chce mięso, a 'fish' tylko gdy wprost chce rybę. Dieta pescetariańska jedynie dopuszcza ryby, więc bez jawnej prośby o rybę ustaw 'none'. Cel wysokobiałkowy również nie oznacza mięsa ani ryby. Nie wyprowadzaj źródła białka z diety lub celu żywieniowego."
                    },
                    "restrictions": {
                        "type": "array",
                        "items": {"type": "string", "enum": list(LLM_SUPPORTED_RESTRICTIONS)},
                        "maxItems": len(LLM_SUPPORTED_RESTRICTIONS),
                        "uniqueItems": True,
                        "description": "Lista dodatkowych ograniczeń żywieniowych. Dodaj 'gluten_free' tylko gdy użytkownik jawnie prosi o danie bez glutenu lub bezglutenowe. Nie dodawaj go dla próśb o danie bez mięsa, bez laktozy, lekkie ani keto. W pozostałych przypadkach użyj pustej listy []."
                    },
                    "nutrition_goal": {
                        "type": "string",
                        "enum": ["standard", "low_kcal", "high_protein", "keto"],
                        "description": "Cel sylwetkowy/żywieniowy. Słowa 'lekki', 'fit', 'niskokaloryczny', 'mało kalorii' i 'na redukcję' oznaczają 'low_kcal'. Dla dużej ilości białka użyj 'high_protein'. Dla diety ketogenicznej użyj 'keto'. Jeśli brak wytycznych, użyj 'standard'."
                    },
                    "category": {
                        "type": "string",
                        "enum": ["śniadanie", "lunch", "obiad", "kolacja", "deser", "przekąska"],
                        "description": "Rodzaj posiłku z kontrolowanego słownika. Jeśli użytkownik mówi dosłownie 'lunch', zawsze użyj 'lunch' i nie tłumacz tego na 'obiad'. Jeśli użytkownik mówi 'obiad', użyj 'obiad'. Jeśli użytkownik nie sprecyzuje rodzaju posiłku, domyślnie użyj 'kolacja'."
                    },
                    "time_max": {
                        "type": "integer",
                        "description": "Maksymalny czas przygotowania w minutach. Ustawiaj tylko wtedy, gdy użytkownik jawnie podaje limit czasu (np. 'do 15 minut', 'do 30 minut') albo używa słów 'szybki', 'na szybko' lub 'ekspresowy'; przy takiej prośbie bez liczby użyj 30. Nie wymyślaj limitu 30 minut dla słów 'lekki', 'fit', 'niskokaloryczny', 'na redukcję', 'keto' ani 'wysokobiałkowy'. Jeśli nie ma jawnego ograniczenia czasu lub szybkości, pomiń to pole."
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Liczba propozycji do wyszukania w bazie. Domyślnie użyj 3, chyba że użytkownik chce więcej/mniej."
                    }
                },
                "required": ["diet", "protein_preference", "restrictions", "nutrition_goal", "category", "top_n"]
            }
        }
    }
]
