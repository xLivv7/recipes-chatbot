from core.recommendation_preferences import DIETS, PROTEIN_PREFERENCES, SUPPORTED_RESTRICTIONS

RECIPE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Wyszukuje i poleca przepisy kulinarne na podstawie zapytania użytkownika. Użyj tej funkcji zawsze, gdy użytkownik szuka pomysłu na posiłek, prosi o przepis lub chce coś ugotować.",
            "parameters": {
                "type": "object",
                "additionalProperties": False,
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
                        "items": {"type": "string", "enum": list(SUPPORTED_RESTRICTIONS)},
                        "maxItems": len(SUPPORTED_RESTRICTIONS),
                        "uniqueItems": True,
                        "description": "Lista dodatkowych ograniczeń żywieniowych. Dodaj 'gluten_free' dla jawnej prośby bez glutenu lub nietolerancji glutenu. Dodaj 'lactose_free' dla bez laktozy, bezlaktozowe lub jawnej nietolerancji laktozy. Oba ograniczenia mogą wystąpić razem i są niezależne od diety, źródła białka oraz celu. Nie dodawaj ograniczenia zanegowanego, np. 'nie musi być bez laktozy'. Vegan nie dodaje automatycznie lactose_free. Bez mleka, bez nabiału i alergia na mleko nie oznaczają lactose_free ani vegan; wymagają doprecyzowania poza narzędziem. W pozostałych przypadkach użyj []."
                    },
                    "nutrition_goal": {
                        "type": "string",
                        "enum": ["standard", "low_kcal", "high_protein", "keto"],
                        "description": "Cel żywieniowy niezależny od czasu. 'Lekki', 'lekka', 'lekkie', 'lekką', 'fit', 'niskokaloryczny', 'mało kalorii' i 'na redukcję' oznaczają 'low_kcal', także z dietą i limitem czasu. Zanegowana prośba o lekkie danie nie dodaje low_kcal. Dla dużej ilości białka użyj 'high_protein', dla keto 'keto', bez celu 'standard'. Sama szybkość nie oznacza low_kcal, a low_kcal nie oznacza limitu czasu."
                    },
                    "category": {
                        "type": "string",
                        "enum": ["śniadanie", "lunch", "obiad", "kolacja", "deser", "przekąska"],
                        "description": "Rodzaj posiłku z kontrolowanego słownika. Jeśli użytkownik mówi dosłownie 'lunch', zawsze użyj 'lunch' i nie tłumacz tego na 'obiad'. Jeśli użytkownik mówi 'obiad', użyj 'obiad'. Jeśli użytkownik nie sprecyzuje rodzaju posiłku, domyślnie użyj 'kolacja'."
                    },
                    "time_max": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Maksymalny czas w minutach, niezależny od celu i diety. Jawny dodatni limit ma pierwszeństwo: do 15 minut -> 15, do pół godziny -> 30, szybkie do 45 minut -> 45. Bez liczby 'szybki', 'szybka', 'szybkie', 'szybką', 'na szybko' i formy 'ekspresowy/ekspresowa/ekspresowe' oznaczają 30. Zanegowana szybkość sama nie ustawia limitu. Same 'lekki/lekka/lekkie', fit, niskokaloryczny, na redukcję, keto i wysokobiałkowy nie ustawiają czasu. Bez prośby o szybkość lub jawnego limitu pomiń pole (nie podawaj null)."
                    },
                    "top_n": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Liczba propozycji w jednym wyszukiwaniu. Dwa przepisy, dwie przekąski lub dwa desery oznaczają top_n=2 w jednym wywołaniu, nie dwa wywołania. Domyślnie użyj 3, chyba że użytkownik chce więcej/mniej."
                    }
                },
                "required": ["diet", "protein_preference", "restrictions", "nutrition_goal", "category", "top_n"]
            }
        }
    }
]
