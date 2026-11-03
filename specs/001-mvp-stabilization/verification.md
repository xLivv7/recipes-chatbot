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
| ACC-07 — awarie | [Błędy API i argumentów](../../tests/test_tool_call_validation.py), [błędy payloadu](../../tests/test_chat_response_protection.py). | DEC-03 zatwierdzona. Pozostają scenariusze T005 i wdrożenie T006: błąd przygotowania nie może być ukryty jako brak wyników. |
| ACC-08 — katalog | [Walidator bazy](../../validate_db.py), [walidacja flag](../../tests/test_lactose_catalog_validation.py), [curation](../../curation/README.md). | Snapshot i raport zapisano w baseline. Ostrzeżenia wymagają oceny; DEC-02 wymaga szczegółowych scenariuszy i wdrożenia. Pięć SKU pozostaje wstrzymane, DEC-01 utrzymuje nieznane statusy laktozy. |
| ACC-09 — jakość routingu | [Runner raw/application](../../evals/run_routing_eval.py), [przypadki intencji](../../evals/intent_cases.json), [przypadki aplikacji](../../evals/application_routing_cases.json). | Przygotować nowy holdout, sprawdzić etykiety i zamrozić kampanię; pokazać osobno łączny wynik i obsługiwane prośby. Historyczne wyniki nie zaliczają progu. |
| ACC-10 — stabilność | [Runner](../../evals/run_routing_eval.py), [testy powtórzeń i holdoutu](../../tests/test_routing_repeats_holdout.py). | Trzy powtórzenia regresji i nowego holdoutu; próg dotyczy przypadków poprawnych we wszystkich powtórzeniach, nie średniej z przebiegów. |
| ACC-11 — granice obsługi | [Reguły alergii](../../tests/test_request_safety.py), [wykluczenia](../../tests/test_unsupported_exclusions.py), [rozdzielony routing](../../tests/test_separated_routing_eval.py). | Uzgodnić semantyczne etykiety przypadków, także negacji i obsługiwanych próśb błędnie blokowanych przez reguły. W kampanii sprawdzać rzeczywistą decyzję aplikacji; mocki nie zastępują pomiaru LLM. |
| ACC-12 — czytelność | [Przypadki renderera](../../evals/renderer_cases.json) i checklista w kryteriach. | Brak zatwierdzonego zestawu ręcznego oraz formularza z oceną każdej odpowiedzi. Porównanie tekstu w teście nie jest oceną czytelności. |
| ACC-13 — odtwarzalność | [Zależności](../../requirements.txt), [instrukcje](../../evals/README.md), [baseline](../../docs/reports/baseline_2026-10-22.md). | Wersje i kopia danych zapisane, README zaktualizowane. Otwarte: instrukcja przygotowania od zera i próba odtworzenia w odrębnym środowisku (T011). |
| ACC-14 — pełny przepływ | [Integracja z rzeczywistym katalogiem](../../tests/test_recommendations_integration.py), [renderowanie rzeczywistych wyników](../../tests/test_chat_response_protection.py). | Testy częściowe nie stanowią pełnej demonstracji od polskiego zapytania przez rzeczywisty LLM i backend do odpowiedzi. Wybrać scenariusze i rozdzielić żywe próby od kontrolowanych awarii. |

## 3. Weryfikacja wymagań T005 — stan na 2026-11-03

Specyfikacja INT/ERR jest przygotowana. Poniższe scenariusze są planem
weryfikacji T006, nie wykonanymi testami. Ich treść i wyniki oczekiwane
są w [spec.md](spec.md#scenariusze-weryfikacji-do-implementacji-w-t006).
Nie przyznajemy zaliczenia na podstawie samych nazw istniejących testów.

| Wymaganie | Kryterium | Scenariusze / metoda | Punkt zaczepienia i luka |
| --- | --- | --- | --- |
| INT-01 | ACC-01/07/08 | SC-01/03/05/11: kontrola kandydatów i kolejności. | `test_recommendations.py`, `test_lactose_recipe_filter.py`; potrzebne asercje błędu przy braku całej polityki, także bez diety i dla pescetarian/meat/fish. |
| INT-02 | ACC-01 | SC-01/02: zgodność, jawne odrzucenie i kontynuacja. | Istniejące testy diet i ograniczeń; potwierdzić zachowanie bez błędu danych. |
| INT-03 | ACC-01/02/08 | SC-06: NULL z aktywną laktozą i bez niej. | Testy lactose rekomendacji, SKU i walidatora; zachować rozróżnienie NULL i braku rekordu. |
| INT-04 | ACC-01/08 | SC-04/11: bezpośrednie przygotowanie i walidator. | Brak polityki jest obecnie WARNING; potrzebny dowód ERROR i braku obejścia backendu. |
| ERR-01 | ACC-07 | SC-03/05/07/08: błędny kandydat przed i po poprawnym. | Potrzebne testy braku częściowych wyników i rozpoznanych przyczyn danych. |
| ERR-02 | ACC-05/07 | SC-03/07/08/12: test granicy chat z mockiem LLM. | `test_chat_response_protection.py`; nowa ścieżka błędu przygotowania nie jest jeszcze zaimplementowana. |
| ERR-03 | ACC-07 | SC-09: podstawiony RuntimeError w przygotowaniu. | Istniejąca próba błędu programistycznego API w `test_tool_call_validation.py` nie sprawdza maskowania wyjątku w backendzie. |
| ERR-04 | ACC-05 | SC-10: kompletny katalog bez zgodnych wyników i bez kandydatów. | Testy pustych wyników; utrzymać inny komunikat niż ERR-02. |
| ERR-05 | ACC-07 | SC-07/12: przechwycenie logu i porównanie odpowiedzi. | Potrzebny dowód ID/rodzaju błędu w logu i braku sekretów, wypowiedzi oraz szczegółów technicznych w odpowiedzi. |

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
i błędy; ich wdrożenie i wykonanie nowych scenariuszy oczekuje w T006.
Nie zmieniano logiki aplikacji ani danych.
