# Aktualna architektura prototypu

To opis istniejącego kodu. Oczekiwane zachowanie i zatwierdzone zmiany
opisuje [specyfikacja](../specs/001-mvp-stabilization/spec.md), a stan
implementacji [zadania](../specs/001-mvp-stabilization/tasks.md).

## Przepływ

1. `main.chat_with_bot` sprawdza lokalne reguły alergii i wykluczeń.
2. Model otrzymuje zapytanie, prompt i schemat `get_recommendations`.
3. Aplikacja wymaga pojedynczego znanego wywołania i waliduje argumenty.
4. Backend filtruje przepisy, wybiera SKU, liczy makro i porządkuje wyniki.
5. Normalizacja przygotowuje payload, a lokalny renderer tworzy odpowiedź.

Brak tool calla daje stały komunikat; tekst modelu nie zastępuje wywołania.
Nie ma drugiego wywołania LLM redagującego dane przepisów.

## Moduły

| Miejsce | Rola |
| --- | --- |
| [main.py](../main.py) | Orkiestracja zapytania, prompt i komunikaty. |
| [database.py](../core/database.py) | SQLAlchemy i połączenie PostgreSQL. |
| [recommendation_catalog.py](../core/recommendation_catalog.py) | Katalog w pamięci ładowany przy imporcie. |
| [recommendations.py](../core/recommendations.py) | Filtry, SKU, obliczenia i ranking. |
| [recommendation_preferences.py](../core/recommendation_preferences.py) | Słowniki i sprzeczności preferencji. |
| [llm_tools.py](../core/llm_tools.py) i [tool_call_validation.py](../core/tool_call_validation.py) | Schemat i lokalna walidacja narzędzia. |
| [request_safety.py](../core/request_safety.py) | Ograniczone reguły tekstowe przed modelem. |
| [recommendation_normalization.py](../core/recommendation_normalization.py) i [response_renderer.py](../core/response_renderer.py) | Normalizacja i kontrolowana prezentacja. |
| [validation](../core/validation) | Walidatory katalogu. |

## Dane i ograniczenia

PostgreSQL przechowuje składniki, makro, polityki, klientów, SKU, reguły
i przepisy JSONB. Pliki źródłowe i baza są poza Git; curation jest wersjonowane.
Aktualizacja danych wymaga ponownego wczytania katalogu, zwykle restartu.

Przykład dotyczy Winiary. `brand_name` nie izoluje katalogów klientów.
Brak widgetu, publicznego API i pamięci rozmowy mieści się w granicach MVP.
Reguły tekstowe nie rozpoznają wszystkich parafraz, renderer nie potwierdza
prawdziwości danych. Ograniczenia katalogowe nie są gwarancją alergologiczną.

DEC-02/03 wdrożono w T006: brak polityki kandydata zgłasza błąd danych,
a błąd przygotowania nie jest pomijany. `RecommendationDataError` kończy
zapytanie stałym komunikatem i diagnostyką; nieoczekiwane wyjątki propagują.
Dowody: [raport T006](reports/t006_2026-11-03.md).
Przegląd pięciu SKU jest wstrzymany; luka makro pozostaje otwarta.

Dowody rozdzielają [mapa](../specs/001-mvp-stabilization/verification.md)
i [raporty](reports/baseline_2026-10-22.md).
