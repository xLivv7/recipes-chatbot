# Aktualna architektura prototypu

To opis istniejącego kodu. Oczekiwane zachowanie i zatwierdzone zmiany
opisuje [specyfikacja](../specs/001-mvp-stabilization/spec.md), a stan
implementacji [zadania](../specs/001-mvp-stabilization/tasks.md).

## Przepływ

Domyślny tryb `legacy` korzysta z V0:

1. `main.chat_with_bot` sprawdza lokalne reguły alergii i wykluczeń.
2. Model otrzymuje zapytanie, prompt i schemat `get_recommendations`.
3. Aplikacja wymaga pojedynczego znanego wywołania i waliduje argumenty.
4. Backend filtruje przepisy, wybiera SKU, liczy makro i porządkuje wyniki.
5. Normalizacja przygotowuje payload, a lokalny renderer tworzy odpowiedź.

Brak tool calla daje stały komunikat; tekst modelu nie zastępuje wywołania.
Nie ma drugiego wywołania LLM redagującego dane przepisów.

Po T026 istnieje wewnętrzny kandydat `facts_v1`, wybierany jawnie przez
argument `interpretation_mode` funkcji `chat_with_bot`. Nie jest domyślnym
trybem interfejsu. Zachowuje ten sam preflight i końcowy przepływ backendu:

1. Model otrzymuje instrukcje IR1 i ścisły schemat faktów, z wymuszonym
   pojedynczym `submit_recipe_interpretation`. Narzędzie nie ma katalogu.
2. Adapter sprawdza metadane odpowiedzi i call, a walidator cały pakiet
   faktów, typy i dosłowne źródła w bieżącym zapytaniu.
3. Czysty kompilator stosuje lokalne reguły, konflikty i defaulty.
   Wynik to `search` z dotychczasowymi argumentami lub `no_search`.
4. Tylko `search` przechodzi przez istniejący parser do backendu i renderera.
   `no_search` daje MSG-01. Błędna interpretacja daje MSG-06, błąd API MSG-05.

W IR brak calla jest błędem protokołu. Biznesowy brak wyszukiwania może
wystąpić po poprawnym callu interpretacyjnym. Liczniki SDK, interpretacji
i backendu są osobne; tekst modelu nie zastępuje żadnego etapu. Klient IR
ma jawny endpoint OpenAI, retry=0, timeout=30 s i limit 1024 tokenów.
W T026 sprawdzono przepływ wyłącznie na atrapach. Jakość rozpoznawania
faktów przez rzeczywisty model pozostaje do pomiaru w T027.

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
| [interpretation_contract.py](../core/interpretation_contract.py) | Wczytanie schematu IR-1, walidacja i budowanie żądania; bez SDK i bazy. |
| [interpretation_compiler.py](../core/interpretation_compiler.py) | Czysta kompilacja zwalidowanych faktów do istniejących argumentów. |
| [interpretation_adapter.py](../core/interpretation_adapter.py) | Granica SDK, metadane, protokół i diagnostyka; bez katalogu. |
| [IR1.txt](../core/prompts/IR1.txt) i [schemat IR-1](../specs/001-mvp-stabilization/contracts/interpretation-v1.schema.json) | Instrukcje kandydata oraz normatywny format faktów. |
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

Walidator IR nie wykrywa każdego pominiętego wymagania ani błędnej etykiety
z poprawnie zacytowanym źródłem. Testy kompilatora potwierdzają reguły dla
dostarczonych faktów, nie jakość interpretacji modelu. Stan i dowody:
[T026](../specs/001-mvp-stabilization/verification.md#t026--implementacja-ir-1-offline-zakończona).

DEC-02/03 wdrożono w T006: brak polityki kandydata zgłasza błąd danych,
a błąd przygotowania nie jest pomijany. `RecommendationDataError` kończy
zapytanie stałym komunikatem i diagnostyką; nieoczekiwane wyjątki propagują.
Dowody: [raport T006](reports/t006_2026-11-03.md).
Przegląd pięciu SKU jest wstrzymany; luka makro pozostaje otwarta.

Dowody rozdzielają [mapa](../specs/001-mvp-stabilization/verification.md)
i [raporty](reports/baseline_2026-10-22.md).
