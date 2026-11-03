# Mapa weryfikacji MVP

Nawigacja: [specyfikacja](spec.md) · [kryteria](acceptance.md) ·
[plan](plan.md) · [zadania](tasks.md).

Data: 2026-10-22<br>
Wersja: 0.1<br>
Status: wstępne mapowanie; aktualne wyniki istniejących kontroli bazowych
opisuje [raport z 2026-10-22](../../docs/reports/baseline_2026-10-22.md).

## 1. Cel i sposób odczytu

Mapa łączy [kryteria akceptacji](acceptance.md) z istniejącymi narzędziami
weryfikacji. Wskazuje dowody i luki po wykonanej kontroli bazowej.
Nie zastępuje szczegółowych specyfikacji zachowania ani raportu akceptacji.

Tabela wymienia dostępne testy lub narzędzia. Ich bazowy wynik jest zapisany
w raporcie, lecz nie jest dowodem pełnego pokrycia ACC. Żadne ACC nie otrzymuje tu statusu
„spełnione”. Wymienione pliki są punktami zaczepienia, a nie zamkniętym
zestawem wymaganych przypadków. Pokrycie wymaga przeglądu poszczególnych
asercji i jawnego wskazania scenariuszy pozytywnych, negatywnych i brzegowych.

## 2. Powiązania i luki

| Kryterium | Istniejące testy lub narzędzia | Co trzeba doprecyzować lub uzupełnić |
| --- | --- | --- |
| ACC-01 — zgodność przepisów | [Diety](../../tests/test_recommendations_diet_integration.py), [kategorie](../../tests/test_recommendations_categories_integration.py), [ograniczenia](../../tests/test_recommendations_restrictions_integration.py), [integracja](../../tests/test_recommendations_integration.py), [laktoza](../../tests/test_lactose_recipe_filter.py). | Jawna lista kombinacji i granic czasu, przypadki nieznanych polityk, sprzeczności i braku zgodnych przepisów. Potwierdzić, które testy wymagają rzeczywistej bazy. |
| ACC-02 — SKU | [Branding](../../tests/test_recommendations_branding_integration.py), [logika rekomendacji](../../tests/test_recommendations.py), [polityki laktozy SKU](../../tests/test_lactose_sku_policy.py). | Macierz: zgodny SKU, niezgodny, niezweryfikowany, kolejny zgodny według reguł, zgodny koncept bez SKU i niezgodny koncept. |
| ACC-03 — obliczenia | [Obliczenia z wybranym SKU](../../tests/test_recommendations.py), [cele żywieniowe](../../tests/test_recommendations_nutrition_integration.py). | Oddzielić test rankingu od niezależnej kontroli arytmetyki; spisać oczekiwane sumy i wartości na porcję, tolerancje oraz dane wejściowe. |
| ACC-04 — renderer | [Testy renderera](../../tests/test_response_renderer.py), [ochrona odpowiedzi](../../tests/test_chat_response_protection.py), [runner offline](../../evals/run_renderer_eval.py). | Uzgodnić wymagane przypadki payloadu i przypisać je do konkretnych testów; wynik offline nie potwierdza prawdziwości katalogu. |
| ACC-05 — brak wyników i brak wyszukiwania | [Ochrona odpowiedzi](../../tests/test_chat_response_protection.py), [renderer](../../tests/test_response_renderer.py). | Sprawdzić jawnie odrębne komunikaty, zachowanie aktywnych ograniczeń i brak zastępczych wyników. |
| ACC-06 — granica narzędzia | [Walidacja wywołań](../../tests/test_tool_call_validation.py), [pojedyncze wywołanie](../../tests/test_single_recommendation_call.py), [brak tool calla](../../tests/test_chat_response_protection.py). | Powiązać wszystkie wymienione niepoprawne wejścia z asercją braku wywołania backendu; zwykły JSON pozostaje niepoprawnym kanałem. |
| ACC-07 — awarie | [Błędy API i argumentów](../../tests/test_tool_call_validation.py), [błędy payloadu](../../tests/test_chat_response_protection.py). | DEC-03 wdrożona i zweryfikowana w T006; dowody w sekcji 3. Inne awarie pozostają w ogólnym zakresie ACC-07. |
| ACC-08 — katalog | [Walidator bazy](../../validate_db.py), [walidacja flag](../../tests/test_lactose_catalog_validation.py), [curation](../../curation/README.md). | Snapshot i raport zapisano w baseline. Ostrzeżenia wymagają oceny; DEC-02 wdrożona i zweryfikowana w T006. Pięć SKU pozostaje wstrzymane, DEC-01 utrzymuje nieznane statusy laktozy. |
| ACC-09 — jakość routingu | [Runner raw/application](../../evals/run_routing_eval.py), [przypadki intencji](../../evals/intent_cases.json), [przypadki aplikacji](../../evals/application_routing_cases.json). | Przygotować nowy holdout, sprawdzić etykiety i zamrozić kampanię; pokazać osobno łączny wynik i obsługiwane prośby. Historyczne wyniki nie zaliczają progu. |
| ACC-10 — stabilność | [Runner](../../evals/run_routing_eval.py), [testy powtórzeń i holdoutu](../../tests/test_routing_repeats_holdout.py). | Trzy powtórzenia regresji i nowego holdoutu; próg dotyczy przypadków poprawnych we wszystkich powtórzeniach, nie średniej z przebiegów. |
| ACC-11 — granice obsługi | [Reguły alergii](../../tests/test_request_safety.py), [wykluczenia](../../tests/test_unsupported_exclusions.py), [rozdzielony routing](../../tests/test_separated_routing_eval.py). | Uzgodnić semantyczne etykiety przypadków, także negacji i obsługiwanych próśb błędnie blokowanych przez reguły. W kampanii sprawdzać rzeczywistą decyzję aplikacji; mocki nie zastępują pomiaru LLM. |
| ACC-12 — czytelność | [Przypadki renderera](../../evals/renderer_cases.json) i checklista w kryteriach. | Brak zatwierdzonego zestawu ręcznego oraz formularza z oceną każdej odpowiedzi. Porównanie tekstu w teście nie jest oceną czytelności. |
| ACC-13 — odtwarzalność | [Zależności](../../requirements.txt), [instrukcje](../../evals/README.md), [baseline](../../docs/reports/baseline_2026-10-22.md). | Wersje i kopia danych zapisane, README zaktualizowane. Otwarte: instrukcja przygotowania od zera i próba odtworzenia w odrębnym środowisku (T011). |
| ACC-14 — pełny przepływ | [Integracja z rzeczywistym katalogiem](../../tests/test_recommendations_integration.py), [renderowanie rzeczywistych wyników](../../tests/test_chat_response_protection.py). | Testy częściowe nie stanowią pełnej demonstracji od polskiego zapytania przez rzeczywisty LLM i backend do odpowiedzi. Wybrać scenariusze i rozdzielić żywe próby od kontrolowanych awarii. |

## 3. Weryfikacja wymagań T005 — wykonana w T006 (2026-11-03)

Źródło scenariuszy: [spec.md](spec.md#scenariusze-weryfikacji-do-implementacji-w-t006).
Testy: [test_recipe_data_integrity.py](../../tests/test_recipe_data_integrity.py).
Każdy wiersz poniżej ma status **zweryfikowane w zakresie T006**.
Wynik: 14 nowych metod testowych, warianty subTest oraz pełna regresja
230 testów bez błędów i pominięć. Dowody:
[raport T006](../../docs/reports/t006_2026-11-03.md).
Nie oznacza to zaliczenia całego kryterium ACC ani pełnego MVP.

| Wymaganie | Kryterium | Scenariusze | Konkretne metody testowe (prefiks `test_`) |
| --- | --- | --- | --- |
| INT-01 | ACC-01/07/08 | SC-01/03/05/11 | `sc01_complete_catalog_keeps_facts_and_calculations`, `sc03_missing_policy_fails_all_preference_dimensions`, `sc05_missing_policy_cannot_hide_behind_rejected_ingredient`, `sc11_out_of_scope_recipe_is_not_prepared` |
| INT-02 | ACC-01 | SC-01/02 | `sc02_explicit_incompatibility_continues_to_valid_candidate` i SC-01; istniejąca regresja diet i ograniczeń. |
| INT-03 | ACC-01/02/08 | SC-06 | `sc06_legal_null_lactose_preserves_filter_and_generic_fallback` oraz istniejące testy laktozy. |
| INT-04 | ACC-01/08 | SC-04/11 | `sc04_direct_preparation_and_validator_detect_missing_policy`, SC-11. |
| ERR-01 | ACC-07 | SC-03/05/07/08 | `sc07_failure_aborts_whole_query_in_both_candidate_orders`, SC-03/05 oraz trzy metody SC-08. |
| ERR-02 | ACC-05/07 | SC-12 | `sc12_chat_data_error_and_programming_error_have_distinct_boundaries`; pozostałe scenariusze sprawdzają błąd domenowy backendu. |
| ERR-03 | ACC-07 | SC-09/12 | `sc09_unexpected_preparation_error_propagates`, SC-12. |
| ERR-04 | ACC-05 | SC-10 | `sc10_normal_empty_result_is_not_data_error` i istniejące testy pustego renderowania. |
| ERR-05 | ACC-07 | SC-12 | SC-12 sprawdza rodzaj problemu, ID przepisu/konceptu w logu, brak wypowiedzi użytkownika oraz stałą odpowiedź bez renderowania i drugiego API. Logowanie korzysta tylko z pól błędu domenowego, bez wartości wejściowych i konfiguracji. |

SC-08 obejmuje `sc08_invalid_numbers_are_recognized_data_failures`,
`sc08_missing_macro_and_zero_macro` i `sc08_broken_sku_references_fail_even_with_restrictions`.
Warianty obejmują przypisanie do innego klienta, innego konceptu, brak SKU
i brak mapowania konceptu. `client_id` SKU jest odczytywany z istniejącej bazy;
nie zmieniono schematu ani danych.

### Routing T008 — plan weryfikacji T009

Stan na 2026-11-03: specyfikacja i protokół gotowe; kod instrumentacji,
testy wariantów i żywe pomiary nie są jeszcze wykonane. Wejścia offline:
[plan_inputs.json](../../dokumentacja%20pracy/2026-11-03_t008/plan_inputs.json).
Odczytano pliki przypadków i lokalne reguły; nie importowano aplikacji
ani nie łączono się z bazą lub API. To nie jest dry-run nowej instrumentacji.

| Wymaganie | Kryterium / scenariusze | Istniejący punkt zaczepienia i brakujący dowód |
| --- | --- | --- |
| ROU-01 | ACC-06/09; RSC-01 | `test_single_recommendation_call.py`, `test_current_evaluation.py`; potrzebne pomiary V0/V1/V2 i agregaty poprawności wszystkich argumentów. |
| ROU-02 | ACC-06/09; RSC-02 | `test_no_tool_diagnostics.py`, `test_chat_response_protection.py`; potwierdzić zachowanie w instrumentacji każdego wariantu. Nie zaliczać tekstowego JSON-a. |
| ROU-03 | ACC-09/11; RSC-03/04/05 | Istniejące przypadki guard/routing i testy preflight. W kampanii oddzielić 27 ocen ACC-11 i 6 znanych fałszywych blokad, bez zmiany etykiet. |
| ROU-04 | ACC-06/09; RSC-06/07 | `test_tool_call_validation.py`, `test_complete_prompt_examples.py`; kontrola V0 nadal używa ramek, V2 potrzebuje osobnego odczytu tych samych pełnych argumentów. |
| ROU-05 | ACC-09/10; RSC-08 | `test_routing_repeats_holdout.py` i obecne metryki per-case; potrzebne agregaty podzbiorów, łączenie rund bez duplikatów, dowód kompletności kampanii. |
| ROU-06 | Porównywalność; RSC-07/08 | Test izolacji wariantu w raw/application, zgodność V0 z bazą, zapis i hashe pełnych promptów, manifest oraz kontrola braku API w dry-run — do wykonania w T009. |

Trzy warianty i trzy powtórzenia dwóch trybów dają 1368 ocen i planowo
1278 wywołań SDK. W T008 faktycznie wykonano **0 wywołań API**. Nie uznano
żadnego ROU za potwierdzony żywym pomiarem i nie zmieniono ocen ACC.
Końcowy niezależny holdout pozostaje T010/T013, poza wyborem wariantu.

## 4. Metody zbierania dowodów

Ta sekcja opisuje sposób weryfikacji. Kolejność i stan prac są utrzymywane
w `plan.md` i `tasks.md`, bez osobnej konkurencyjnej listy zadań.

### A. Procedura kontroli bazowej — wykonana

Przebieg i wyniki zapisano w [raporcie](../../docs/reports/baseline_2026-10-22.md).
Poniższe punkty opisują procedurę, nie kolejne zadania do rozpoczęcia.

1. Zapisać commit i niezacommitowane różnice, wersję Pythona i bibliotek.
2. Utrwalić wersję katalogu oraz sposób jego odtworzenia, bez ujawniania sekretów.
3. Uruchomić istniejące testy, walidator i ocenę renderera offline.
4. Zapisać surowe wyniki, liczbę testów wykonanych, pominiętych i błędów.

Część testów integracyjnych używa
[pomocnika rzeczywistej bazy](../../tests/recommendation_integration_helpers.py),
który może zgłosić `SkipTest` przy błędzie importu lub pustym katalogu.
Samo „OK” z test runnera nie wystarcza: pominięta integracja oznacza brak
dowodu. Należy sprawdzić przyczynę pominięcia, a nie automatycznie uznać ją
za potwierdzoną niedostępność PostgreSQL.

Pomiar bazowy ocenia stan przed poprawkami. Może wykazać błędy i luki;
nie jest kampanią końcowej akceptacji. Nie należy zmieniać testów ani danych
w trakcie jednego przebiegu w celu uzyskania pozytywnego wyniku.

### B. Specyfikacje i uzupełnienie pokrycia

1. Z istniejących kontraktów wyprowadzić konkretne wymagania i przykłady.
2. Dla każdego wskazać ACC i dokładny test lub scenariusz pomiarowy.
3. Dla DEC-02/03 korzystać z opracowanych INT/ERR i SC w T005;
   w T006 uzupełnić testy i wdrożyć zachowanie.
4. Uzupełnić tylko te testy, które sprawdzają istotną lukę zachowania.
5. Przygotować zestaw ręcznej oceny oraz nowy holdout z przeglądem etykiet.

### C. Poprawki i ocena

Prace stabilizacyjne wynikają z niezgodności z wymaganiami, a nie z pomysłu
na kolejną funkcję. Dla każdego zadania zapisać: wymaganie, objaw, plan zmiany
i sposób weryfikacji. Routing ST-01 badać w kontrolowanym eksperymencie,
z zachowaniem starego wariantu i raportów. Nie wykorzystywać holdoutu do
wybierania kolejnych wersji promptu.

Kampania końcowa obejmuje tę samą wersję kandydującą we wszystkich dowodach,
z oceną ACC-01–ACC-14. Płatne pomiary API stanowią osobny, jawnie opisany etap;
samo sporządzenie mapy ich nie uruchamia.

## 5. Wynik tego kroku

Zatwierdzone progi zapisano w kryteriach. Istnieje wstępna mapa wszystkich
14 ACC i lista luk. Początkowo opracowano ją bez wykonania kontroli;
następnie zapisano osobny raport bazowy z kopią danych, inwentaryzacją
środowiska i wynikami testów. Szczegółowe przypadki wymagane oraz nowy
holdout pozostają do przygotowania. T005 opisuje szczegółowo integralność
i błędy; wdrożenie T006 i wykonane scenariusze są opisane w sekcji 3.
Kod zaktualizowano zgodnie z wymaganiami; dane i progi pozostały bez zmian.

T008 zakończyło przygotowanie wymagań ROU i protokołu, bez zmiany promptu
lub kodu pomiarowego. Następna praca T009 zaczyna się od instrumentacji
offline, a nie od wywołania płatnej kampanii.
