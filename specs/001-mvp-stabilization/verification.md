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

Stan na 2026-11-03: specyfikacja, instrumentacja i testy wariantów gotowe.
Pełna regresja: 240 testów bez błędów i pominięć; żywego pomiaru nie wykonano.
Manifest zamrożony, ale uruchomienie odrzuciła automatyczna kontrola uprawnień.
Stan i dowody: [raport przygotowania](../../docs/reports/t009_preparation_2026-11-03.md).
Wejścia pierwotnej analizy offline:
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

Testy instrumentacji są w [test_routing_experiment.py](../../tests/test_routing_experiment.py),
kod porównania w [run_routing_experiment.py](../../evals/run_routing_experiment.py).
Sprawdzono izolację wariantów, zgodność przykładów, błędy kanału/protokołu,
dry-run, rotację, kompletność i regułę wyboru oraz checkpoint po błędzie API.
Sformułowania „potrzebny pomiar” w tabeli nadal dotyczą żywego modelu;
planowane kontrole instrumentacji zostały wykonane, wyniki jakości pozostają otwarte.

Trzy warianty i trzy powtórzenia dwóch trybów dają 1368 ocen i planowo
1278 wywołań SDK. W T008 faktycznie wykonano **0 wywołań API**. Nie uznano
żadnego ROU za potwierdzony żywym pomiarem i nie zmieniono ocen ACC.
Końcowy niezależny holdout pozostaje T010/T013, poza wyborem wariantu.

## 4. Metody zbierania dowodów

### Plan dowodów dla ustaleń 2, 3 i 6 — 2026-11-16

Zadania przygotowano na polecenie autorki; ich utworzenie nie oznacza
wykonania projektów, implementacji ani zaliczenia ACC. DEC-09 zapisuje
zaakceptowaną semantykę; DEC-10/11 zlecają opracowanie kontraktów.

| Zadanie | Podstawa | Wymagany rezultat i przyszły dowód |
| --- | --- | --- |
| T017 — kontrakt diet/protein | Punkt 2, DEC-09, INS-02; ROU-12–17, ACC-09/11 | Wykonane 2026-11-16: kontrakt, macierz, DP-01–28, mapa istniejących etykiet, diagnoza, H-T017 i protokół T017-v1. Dowody i granice poniżej; zachowanie modelu nie zostało ponownie zmierzone. |
| T019 — kontrakt no_tool | Punkt 3, DEC-10, INS-03; NTO-01–08; ACC-05/06/07/09/11 | Wykonane 2026-11-17 jako projekt: tabela decyzja → wykonanie → komunikat, odpowiedzialność i źródło wiedzy, MSG-01–08, NTC-01–18 oraz plan testów. Wdrożenie T022 i pomiar zachowania pozostają otwarte. |
| T020 — wiele celów żywieniowych | Punkt 6, DEC-11, INS-07; wpływ na ACC-01/02/03/04/09/14 do oceny | Projekt łączenia wymagań i preferencji, kontraktu danych, filtrów, rankingu, doboru SKU i zgodności pojedynczych celów; scenariusze, ocena zakresu oraz plan migracji. |

Kierunek INS-04/05 ustalono następnie w DEC-12 i T021: format V4 oraz
kontrastowe przykłady w V5. Scenariusze kontraktowe nie są automatycznie
demonstracjami promptu. Na etapie planowania wykonano jedynie
aktualizację planowania i kontrolę spójności dokumentów; nie uruchamiano
testów modelu, aplikacji, API ani bazy i nie zmieniano kodu.

### T017 — diagnoza i kontrakt zakończone

Data: 2026-11-16. Ukończono zakres projektowy T017, bez wdrożenia poprawki
routingu. [Kontrakt ROU-12–17 i scenariusze DP](spec.md#t017--kontrakt-interpretacji-diety-i-źródła-białka),
[diagnoza, mapa kontrastów i protokół T017-v1](plan.md#9-t017--diagnoza-relacji-dietprotein-i-specyfikacja-poprawki).

Przejrzano `intent_032` na podstawie niezmienionego raportu T016: jedno
narzędzie i poprawne top_n=4 w 6/6 prób V4, ale niezamówione fish w 2/3 raw
i 3/3 application. To rozbieżność semantyczna, nie nielegalna kombinacja
pól. Brak kontrastowych demonstracji pozostaje hipotezą; nie znaleziono
nakazu wyprowadzania fish z pescetarian. INS-02 i konflikt INS-01 opisano
oddzielnie od tej obserwacji; T018 nie ma jeszcze pomiaru skuteczności.

Kontrole offline, wykonane lokalnie bez importu main, klienta API i bazy:

- 28 scenariuszy DP: 22 pełne obiekty argumentów tool przyjęte przez
  istniejący parser oraz 6 scenariuszy no_tool bez argumentów;
- wszystkie 12 par diet/protein: 7 przyjmowanych i 5 odrzucanych, zgodnie
  z macierzą kontraktu; poprawne pescetarian/fish pozostaje dozwolone;
- 96 wpisów w czterech istniejących zestawach (64 intent, 6 routing,
  6 guard i 20 powtórzeń w pilocie): poprawne strukturalnie expected,
  unikalne ID w pliku i zgodność pilota z przypadkami źródłowymi;
- mapa 25 istniejących ID potwierdzona względem zapisanych diet/protein
  i celów; nie przypisano nowego wyniku modelu żadnemu ID;
- hashe 130 wcześniejszych plików bez zmian, w tym kod, prompty V0–V4,
  expected, holdout i raporty. Zmiana dotyczy czterech dokumentów SDD;
  lokalne materiały kontroli zapisano w ignorowanym katalogu dowodów.

Dowody: [contract_checks.json](../../dokumentacja%20pracy/2026-11-16_t017/contract_checks.json),
[skrypt odtworzenia kontroli](../../dokumentacja%20pracy/2026-11-16_t017/check_contract.py),
[hashe sprzed T017](../../dokumentacja%20pracy/2026-11-16_t017/before_hashes.json).
To walidacja kontraktu i istniejącej granicy narzędzia, nie test rozumienia
języka przez model. Nie uruchamiano ponownie pełnej regresji aplikacji
dla tej zmiany dokumentacji. **0 wywołań API i 0 operacji bazy**.

Kontrola preflight wykazała fałszywe blokady DP-02/03/22 oraz potwierdziła
guard_005/006. DP-02/03/22 blokuje ogon zdania po przecinku, mimo zgodnej
reprezentacji prośby. Expected pozostaje tool; tych przypadków nie naprawi
sam prompt, bo nie docierają do modelu. Zapisano lukę INS-06 i ograniczenie
przyszłego pomiaru; nie zmieniono reguł ochrony. Projekt no_tool w T019
powinien uwzględnić pochodzenie takiej blokady, a jej ewentualna naprawa
wymaga odrębnego zakresu implementacyjnego.

W chwili ukończenia T017 T021 oczekiwało tylko na T019. W planie zapisano wyjątek dla dwóch
bezwarunkowych zdań „bez mięsa” i wprowadzenia do demonstracji; pozostałe
instrukcje V4 mają być zachowane. Zapobiega to sprzeczności nowego V5
z DEC-09/no_tool. Nie utworzono V5 i nie zmieniono aktywnego V0.
ROU-12–17 i ACC nadal wymagają późniejszych dowodów zachowania programu.

### T019 — kontrakt no_tool zakończony

Data: 2026-11-17. Zakończono projekt, bez wdrożenia zmian kodu. Rezultat:
[NTO-01–08, decyzje, MSG-01–08 i NTC-01–18](spec.md#t019--kontrakt-odpowiedzi-no_tool)
oraz [granice implementacji i plan kontroli](plan.md#11-t019--kontrakt-odpowiedzi-no_tool).
Wybrano brak nowego pola/narzędzia przyczyny i stały komunikat aplikacji
przy no_tool modelu. Model nie tworzy odpowiedzi końcowej ani dialogu.
Brak pól z wartościami domyślnymi nie uzasadnia odmowy.

Przejrzano `main.chat_with_bot`, preflight, parser, renderer i runner
raw/application oraz asercje istniejących testów. Kontrola offline na
źródłach `83004ea` objęła 12 obserwacji obecnej funkcji wyodrębnionej
z AST, bez importu main/SDK/bazy. Wstrzyknięto lokalną atrapę klienta
i lookup; odpowiedzi były w pełni kontrolowane.

| Dowód | Ustalenie / ograniczenie |
| --- | --- |
| OBS-01/02 | Brak narzędzia daje stały komunikat. Poprawny JSON w content dla obsługiwanej prośby nie jest wykonywany; to nadal błąd decyzji modelu w przyszłej ocenie. |
| OBS-03 | Poprawny call uruchamia lookup raz; pusta lista daje „Nie znaleziono”, odrębnie od „Nie wyszukano”. |
| OBS-04/05/06 | Symulowany wyjątek API, niepoprawne argumenty i brak choices nie uruchamiają lookup. Kontrola wyjątku używa lokalnej klasy zastępczej, nie sprawdza zachowania SDK. |
| OBS-07 | Nieznana funkcja nie uruchamia backendu; ma inny komunikat niż docelowy wspólny MSG-06. Ujednolicenie w T022. |
| OBS-08/09 | length oraz content_filter/refusal bez call są obecnie traktowane jak zwykłe no_tool. Luka NTO-06, do T022. |
| OBS-10 | Poprawnie wyglądający call z length uruchamia obecnie lookup. Docelowo NTO-06 wymaga 0 wywołań i błędu; poprawka do T022. |
| OBS-11/12 | Preflight pomija klienta i lookup. OBS-12 pozostaje fałszywą blokadą DP-02, bez zmiany expected lub reguły ochrony. Nie wykonano próby modelu. |

Przechwycono **10 wywołań lokalnej atrapy klienta i 2 wywołania atrapy
lookup**, **0 rzeczywistych wywołań API i 0 operacji bazy**. Kontrole
opisują stan zastany, a nie przejście nowych NTC lub poprawę rozumienia
przez model. Nie uruchamiano pełnej regresji aplikacji dla projektu
dokumentacji. Hashe 130 plików poza czterema dokumentami SDD pozostały
niezmienione, w tym kod, prompty, expected i raporty. Nie użyto zapytań
holdoutu do projektowania.

Dowody: [current_behavior_checks.json](../../dokumentacja%20pracy/2026-11-17_t019/current_behavior_checks.json),
[skrypt kontroli](../../dokumentacja%20pracy/2026-11-17_t019/check_current_behavior.py),
[hashe sprzed T019](../../dokumentacja%20pracy/2026-11-17_t019/before_hashes.json).
W chwili ukończenia T019 T021 było gotowe do rozpoczęcia. Wdrożenie
komunikatu i obsługi metadanych jest odrębnym T022. Fałszywe blokady
preflight pozostają osobną luką. Żadne ACC nie zostało tutaj zaliczone.

### T021 — przygotowanie V5 offline zakończone

Data: 2026-11-17. Podstawa: DEC-12 / INS-04/05 oraz kontrakty T017/T019.
Utworzono [V5](../../evals/routing_prompts/V5.txt),
[nowe przypadki](../../evals/routing_v5_cases.json) i niezależny od SDK/bazy
[program przygotowania](../../evals/prepare_routing_v5.py).
Mapa D5-01–18, wybór kohort i dokładny plan są w
[sekcji 13 planu](plan.md#13-t021--przygotowanie-v5-dla-punktów-4-i-5-audytu).

| Kontrola | Dowód i rezultat |
| --- | --- |
| Zakres V4/V5 | Walidator dopuszcza tylko dwie korekty „bez mięsa”, wprowadzenie i nowy blok przykładów. Pozostałe instrukcje oraz końcowy akapit V4 zachowano. Diff zapisany w przygotowaniu. |
| Demonstracje | 18 pozycji: 14 pełnych obiektów przyjętych przez istniejący parser, 4 jawne braki wywołania. Reguły każdego przykładu są w mapie; sprawdzono pary diet/protein i czasu oraz macierz 12 kombinacji. |
| Diagnostyka | 20 niezmienionych przypadków pilota + 12 nowych = 32, w tym 25 tool i 7 no_tool. Kontrola argumentów i identyfikatorów; zapytania różne od demonstracji także po normalizacji. |
| Audyt preflight | Osobne guard_005/006 i DP-02/03/22: expected=tool, pięć fałszywych blokad, bez modelu. Nie są sukcesami no_tool i pozostają luką MVP poza mianownikiem małego porównania. |
| Testy przygotowania | 9 testów bez błędów/pominięć: brak sieci i zależności od klucza/bazy, zamrożenie wejść, zakaz nadpisania, zakres zmian, niezamówione fish, fikcyjne no_tool, przeciek zapytań, niepoprawne etykiety oraz rozdzielenie kohort. |
| Ochrona historii | Hashe 129 wcześniejszych plików poza edytowaną dokumentacją bez zmian, w tym main, wspólny schemat, V0–V4, stare expected, testy i raporty. Zmiany T019 w dokumentacji zachowano. |

Testy są w [test_routing_v5_preparation.py](../../tests/test_routing_v5_preparation.py).
Nie importują main, SDK, bazy ani starego runnera wymagającego PostgreSQL.
Korzystają z istniejącego parsera, schematu i reguł preflight. Sprawdzają
przygotowanie i granice danych, nie rozumienie przez model. Nie uruchamiano
pełnej regresji aplikacji, której kod w T021 nie został zmieniony.

Dowody lokalne:

- [manifest](../../dokumentacja%20pracy/2026-11-17_t021/preparation/manifest.json),
  [checks i mapa przykładów](../../dokumentacja%20pracy/2026-11-17_t021/preparation/checks.json),
  [diff V4/V5](../../dokumentacja%20pracy/2026-11-17_t021/preparation/V4_V5.diff);
- [wynik testów](../../dokumentacja%20pracy/2026-11-17_t021/tests.json),
  [log](../../dokumentacja%20pracy/2026-11-17_t021/tests.log),
  [hashe sprzed T021](../../dokumentacja%20pracy/2026-11-17_t021/before_hashes.json).

Przygotowanie przewiduje 384 oceny / 354 wywołania, szacunkową rezerwę
0,86790195 USD, aktualny schemat po T018 i niewdrożone T022. Ma
execution_enabled=false, actual_api_calls=0, brak zatwierdzonego budżetu
i nie posiada płatnego wykonawcy. **0 rzeczywistych wywołań API i 0 operacji
bazy.** Model gpt-4o-mini zachowano; status deprecated, źródło i data cennika
są zapisane w manifeście. Dostępności konta nie sprawdzano wywołaniem modelu.

Po T021 zaplanowano T022, którego ukończenie opisano poniżej. T023 wymaga nowej instrumentacji i manifestu
na tej samej wersji aplikacji dla V4/V5. Wyników T016 nie przeniesiono
na nowy opis funkcji lub V5. Nie zmieniono aktywnego V0, nie potwierdzono
H-T017 ani ACC i nie wznowiono T009/T012.

### T022 — wdrożenie no_tool zakończone

Data: 2026-11-17. Wdrożono MSG-01, wspólny MSG-06 dla nieznanego narzędzia
i kontrolę NTO-06 przed parserem/dispatch. [Wspólny walidator](../../core/llm_response_validation.py)
jest używany przez [aplikację](../../main.py) i [runner](../../evals/run_routing_eval.py).
Nie odczytuje content jako przyczyny ani argumentów. Refusal jest
rozpoznawane po polu metadanych odpowiedzi, nie po tekście odmowy w content.

Diagnoza ma wersję `response_validation_version=T022-v1`. Brak choices,
length, content_filter i niepuste refusal oznaczają failure_stage=protocol,
effective_action=error, bez model_action, model_decision_correct i ocen pól.
Metadane i ślad narzędzi pozostają w diagnostyce; żaden taki call nie trafia
do backendu. Normalne no_tool nadal jest oceniane względem expected;
fałszywy guard pozostaje błędem preflight, bez próby modelu.

Pełna regresja: **283 testy, 0 niepowodzeń, 0 błędów, 0 pominięć**.
W T022 dodano 9 testów; pozostałe istniejące testy granicy, dawnych profili,
przygotowania V5, renderera i rekomendacji również przeszły.

| NTC | Kontrole i istotne asercje |
| --- | --- |
| 01–04 | `test_controlled_no_tool_decisions_cover_scope_conflicts_and_nonstandalone_queries`: poza zakresem, sprzeczności T017, alergie/wykluczenia i brak samodzielnej prośby w raw/application; brak lookup oraz rozdzielenie guard od modelu. `test_empty_or_context_dependent_query_does_not_reuse_history`: brak pamięci i treści modelu w odpowiedzi. |
| 05 | `test_bare_recipe_request_dispatches_default_arguments_once`: jedna interpretacja i jeden lookup z kompletem domyślnych argumentów, bez wymuszonego doprecyzowania. |
| 06/07 | Istniejące kontrole `test_chat_response_protection.py` i `test_no_tool_diagnostics.py`: null/pusty/tekstowy content, zmyślone produkty/liczby/URL i instrukcje są ignorowane, bez backendu. |
| 08/09 | Istniejące `test_content_is_preserved_verbatim_without_dispatching_json` i `test_no_tool_decision_is_scored_without_inventing_field_errors`: poprawny JSON lub odmowa bez call nadal jest porażką dla expected=tool, bez wymyślonych argumentów i ocen pól. |
| 10 | `test_empty_results_are_rendered_without_llm`: lookup jest wykonany, pusty wynik ma własny komunikat, bez dodatkowego modelu. |
| 11 | `test_api_errors_use_safe_response_without_exception_details` i `test_api_failure_is_not_a_no_tool_success_or_parameter_failure`: wyjątki połączenia, czasu, autoryzacji, limitu i usługi; brak backendu, bez sekretów i sukcesu no_tool. |
| 12/13 | `test_tool_call_validation.py`: puste choices, nieznana funkcja, wiele calls i niepoprawne argumenty; brak backendu. Nieznana funkcja używa teraz tego samego MSG-06. |
| 14 | `test_incomplete_filtered_or_refused_responses_stop_before_arguments_and_backend`: 8 kombinacji, parser i backend niewywołane. `test_response_failures_are_not_business_decisions_in_either_mode`: 24 kombinacje sygnałów, obecności calls, expected i trybu; spójna klasyfikacja, zachowany ślad, brak sukcesu i ocen pól. Puste refusal pozostaje dozwolone. |
| 15 | `test_sc12_chat_data_error_and_programming_error_have_distinct_boundaries` oraz `test_invalid_sku_fails_closed`: rozdzielenie błędu danych/payloadu i błędu programistycznego, bez pozornego pustego wyniku lub redakcji przez model. |
| 16 | `test_all_five_known_false_blocks_remain_preflight_errors_without_model_attempts`: guard_005/006 i DP-02/03/22, niezmienione expected=tool, 0 prób klienta, 0 backendu; wynik pozostaje błędny. |
| 17 | `test_allergy_guard_has_priority`: pierwszeństwo reguły alergii przed wykluczeniem, bez klienta i backendu. |
| 18 | `test_no_tool_does_not_repeat_a_model_claim_that_it_searched_the_catalog`: nie powiela twierdzenia o przeszukaniu, pustym wyniku ani domniemanego powodu. |

To kontrole aplikacji na odpowiedziach podstawionych, nie nowe wyniki
interpretacji przez model. **0 rzeczywistych żądań OpenAI**; harness
blokował metodę żądania SDK, a liczba prób użycia tej ścieżki wynosiła 0.
Import aplikacji i testy integracyjne wykonały 35 SELECT lokalnego
PostgreSQL. Zapisy do katalogu były zablokowane, bez prób zapisu. Istniejące
testy curation korzystały z własnej SQLite w pamięci (8 CREATE, 8 INSERT,
19 SELECT, 2 UPDATE); te operacje nie dotyczą katalogu PostgreSQL.

Zachowano przebiegi nieudane: pierwsza próba w sandboxie nie mogła połączyć
się z localhost; etap red wykazał stare luki; pierwsza pełna regresja miała
2 niepowodzenia wskutek blokady tymczasowej SQLite w harnessie. Po
ograniczeniu blokady zapisów do katalogu i dopuszczeniu SQLite w pamięci
pełna regresja przeszła. Nie usuwano ani nie pomijano testów.

Dowody: [wynik końcowy](../../dokumentacja%20pracy/2026-11-17_t022/final_verified.json),
[log](../../dokumentacja%20pracy/2026-11-17_t022/final_verified.log),
[harness](../../dokumentacja%20pracy/2026-11-17_t022/run_tests.py),
[kontrola zakresu](../../dokumentacja%20pracy/2026-11-17_t022/scope_checks.json),
[hashe sprzed zmian](../../dokumentacja%20pracy/2026-11-17_t022/before_hashes.json).

Hash wspólnej walidacji dodano do źródeł nowych manifestów. Oryginalne
30 plików przygotowania T021 pozostaje niezmienione; ten pakiet identyfikuje
stan przed T022. T023 ma przygotować nowe źródła i manifest. Prompt builder
V0, sposób wywołania modelu, schemat, parser preferencji, preflight,
V0–V5, expected, backend i katalog pozostają bez zmian. Nie przeliczono
historii i nie zaliczono jakości modelu ani końcowej akceptacji MVP.

### T023 — porównanie V4/V5 zakończone

Zakończono 2026-11-17: osobno zatwierdzony pełny przebieg 02, audyt
i przegląd T017-v1. **DEC-13: V5 nie kwalifikuje się, pozostaje V0.**
384 oceny / 354 wywołania, 12 pełnych grup, 354 unikatowe request IDs,
jeden resolved model gpt-4o-mini-2024-07-18 i 0 błędów API/odpowiedzi.
V4 raw 84/96, application 86/96; V5 raw 75/96, application 78/96.
V5 ma 21/21 no_tool i spadek niezamówionych fish 4 → 0 w obu trybach,
lecz sześć regresji w każdym, 13 błędnych dispatch application, obsługiwane
57/75 i stabilne 25/32. Intent_004 oraz diag_004 nadal 0/3 w obu trybach.

[Raport](../../docs/reports/t023_routing_2026-11-17.md),
[surowe wyniki](../../dokumentacja%20pracy/2026-11-17_t023/campaign_02/results.json),
[porównanie](../../dokumentacja%20pracy/2026-11-17_t023/campaign_02/comparison.json),
[diagnostyka](../../dokumentacja%20pracy/2026-11-17_t023/diagnostics_02.json)
i [zgoda 02](../../dokumentacja%20pracy/2026-11-17_t023/approval_02.json).
[Audyt wykonania](../../dokumentacja%20pracy/2026-11-17_t023/execution_audit_02.json)
niezależnie przeliczył 10 flag reguły (cztery true, sześć false), sprawdził
payloady, kolejność, rezerwy, zgodę i kompletność. Przed aktualizacją
specyfikacji potwierdzono niezmienione 25 źródeł i 11 artefaktów;
[hashami utrwalono 53 pliki 02](../../dokumentacja%20pracy/2026-11-17_t023/campaign_02_hashes.json),
zachowano 49 plików 01, 30 plików T021 i 134 chronione istniejące pliki.

Usage 02: 1 215 630 tokenów wejścia, 14 900 wyjścia; koszt referencyjny bez
cache 0,19128450 USD, rezerwa 0,86790195 USD przy progu 1,00 USD.
Obie osobno zatwierdzone próby łącznie: 596 odpowiedzi generacji,
0,32163075 USD kosztu referencyjnego, bez cache/podatków/innego użycia;
to nie rachunek dostawcy. Wykonano też jeden odczyt metadanych modelu.
Obserwacji 01 nie połączono z 02 i nie ponawiano wybiórczo porażek.

Pełna regresja instrumentacji pozostaje 302/302 po poprawce zapisu,
bez pominięć, z generacją SDK zablokowaną. Po pomiarze zmieniono tylko
dokumentację wynikową, bez zmiany kodu aplikacji, promptów, schematu,
expected i danych. [Kontrola końcowa](../../dokumentacja%20pracy/2026-11-17_t023/final_checks.json)
sprawdza integralność dowodów, tabele raportu, status zadań i odnośniki.
Pięć fałszywych blokad nadal jest błędami osobnego audytu bez API;
lookup był atrapą, zbiór rozwojowy nie jest holdoutem. Brak zaliczenia ACC,
wdrożenia V4/V5 i wznowienia T009/T012. T023 zakończone jako eksperyment,
bez uznania routingu za naprawiony.

#### Przygotowanie przed pomiarem

Pierwsze przygotowanie, 2026-11-17, przed generacją. Przygotowano [wykonawcę kampanii](../../evals/run_routing_v5.py)
i początkowe [16 testów](../../tests/test_routing_v5_campaign.py).
Na tym etapie T023.1 było wykonane, a T023.2 i T023.3 pozostawały otwarte
do osobno zatwierdzonego pomiaru oraz przeglądu. Nie było wyników modelu.

Nowy [plan](../../dokumentacja%20pracy/2026-11-17_t023/campaign/plan.json)
zamraża źródła po T022, T017-v1, runtime, hashe wejść i kosztorys.
[Payloady](../../dokumentacja%20pracy/2026-11-17_t023/campaign/payloads.json)
obejmują wyłącznie 32 kontrolowane zapytania, prompty V4/V5 i schemat funkcji;
expected, dane katalogu i rzeczywiste rozmowy nie są wysyłane.
[Harmonogram](../../dokumentacja%20pracy/2026-11-17_t023/campaign/schedule.json)
ma 384 oceny, z czego 354 wymagają generacji, a 30 kończy poprawna ochrona
application. Stan przygotowania: 0 generacji, brak zatwierdzonego hasha
i budżetu. SHA-256 planu:
`f89a18c9702eaa7487af68294c72c26253e37bce3303d014fbb9ad6ccd823783`.
Rezerwa szacunkowa wynosi 0,86790195 USD, proponowany lokalny
próg 1,00 USD; nie jest gwarancją rachunku dostawcy.

Wykonawca sprawdza zgodę na dokładny hash i budżet przed utworzeniem klienta,
zgodność payloadu przed każdym żądaniem oraz zapisuje rezerwę przed wysłaniem.
Obowiązują limit odpowiedzi 512, retry=0, checkpointy i zakaz selektywnego
wznawiania. Pierwszy błąd API lub response_failure_reason przerywa kampanię;
zwykła błędna interpretacja pozostaje wynikiem i nie zatrzymuje pomiaru.
Pięć fałszywych blokad ma osobny audyt z klientem zabraniającym generacji.
Nie stają się sukcesami ani częścią mianownika 32 przypadków.

Pełna regresja: **299 testów, 0 niepowodzeń, 0 błędów, 0 pominięć**.
Dowody: [wynik](../../dokumentacja%20pracy/2026-11-17_t023/full.json),
[log](../../dokumentacja%20pracy/2026-11-17_t023/full.log),
[testy nowej instrumentacji](../../dokumentacja%20pracy/2026-11-17_t023/targeted.json)
i [harness](../../dokumentacja%20pracy/2026-11-17_t023/run_tests.py).
Pełna symulacja wykonała 384 oceny i 354 wywołania atrap; jest oznaczona
execution_kind=mock i is_model_measurement=false. Sprawdzono także brak
klienta przed zgodą, zmienione wejścia/reguły/etykiety, ograniczenia kosztu
i liczby żądań, checkpoint błędu, zakaz wznowienia, remis i regresje,
błędny dispatch, utratę fish oraz niepoprawne/niekompletne obserwacje.

Harness zablokował rzeczywiste żądania SDK; 0 prób tej ścieżki. Importy
i integracja wykonały 35 SELECT lokalnego PostgreSQL, bez zapisu i prób
zapisu do katalogu. Istniejące testy curation wykonały 8 CREATE, 8 INSERT,
19 SELECT i 2 UPDATE wyłącznie we własnej SQLite w pamięci.
Poza testami wykonano **jeden odczyt metadanych modelu**, bez generacji:
[model_access.json](../../dokumentacja%20pracy/2026-11-17_t023/model_access.json).
Widoczność gpt-4o-mini nie dowodzi salda ani powodzenia płatnego żądania.
Łącznie na tym etapie: **0 rzeczywistych żądań generacji**.

[Kontrola zakresu](../../dokumentacja%20pracy/2026-11-17_t023/scope_checks.json)
porównuje stan sprzed T023, zamrożone źródła i historyczny pakiet T021.
[Kontrola dokumentacji](../../dokumentacja%20pracy/2026-11-17_t023/documentation_checks.json)
sprawdza odnośniki i stan zadań. Kod aplikacji, V0–V5, schemat, expected,
parser, preflight i dane pozostają bez zmian. T009/T012 nadal wstrzymane.
Na tym etapie T023 pozostawało w toku; symulacja nie zaliczała H-T017 ani ACC.

#### Przerwany przebieg 01 i poprawka zapisu

Po osobnej zgodzie autorki uruchomiono plan wskazany powyżej. Zachowano
262 oceny i 242 odpowiedzi SDK z unikatowymi request IDs. Zapis kolejnej
rezerwy przerwał PermissionError przy zastępowaniu pliku stanu na Windows,
przed wysłaniem żądania. Licznik rezerwacji wynosi 243; jedna jest niewysłana.
Koszt referencyjny z usage bez cache: 0,13034625 USD. Właściciel blokady
nie został ustalony. Brak kompletnego porównania i kandydata; nie wznowiono
ani nie nadpisano danych. [Raport](../../docs/reports/t023_routing_2026-11-17.md),
[audyt](../../dokumentacja%20pracy/2026-11-17_t023/interrupted_audit.json)
i [hashe pakietu 01](../../dokumentacja%20pracy/2026-11-17_t023/interrupted_campaign_hashes.json).

Poprawka dotyczy wyłącznie lokalnego, atomowego zastąpienia pliku:
po PermissionError do pięciu oczekiwań, łącznie do 1,55 s, potem wyjątek.
Trzy nowe testy potwierdzają chwilową/trwałą blokadę, zachowanie starego
checkpointu i brak SDK przy nieudanym zapisie rezerwy. Po poprawce:
**302 testy, 0 niepowodzeń, 0 błędów, 0 pominięć**.
[Pełny wynik](../../dokumentacja%20pracy/2026-11-17_t023/io_fix_full.json),
[log](../../dokumentacja%20pracy/2026-11-17_t023/io_fix_full.log)
i [19 testów instrumentacji](../../dokumentacja%20pracy/2026-11-17_t023/io_fix_targeted.json).
API generacji w testach zablokowane, 0 prób; 35 SELECT PostgreSQL, bez
zapisów do katalogu, te same operacje tymczasowej SQLite co wcześniej.
Nie zmieniono promptów, expected, schematu, modelu i T017-v1.

Nowy [pakiet 02](../../dokumentacja%20pracy/2026-11-17_t023/campaign_02/plan.json)
zamraża poprawkę. Jest pełnym planem 384 ocen / do 354 wywołań, a nie
wznowieniem 01. Przed uruchomieniem wymagał osobnej zgody, następnie
uzyskanej. Obserwacje 01 pozostają osobno; nie potwierdzają kompletnej
reguły ani akceptacji MVP. Pełny wynik 02 opisano na początku sekcji T023.
SHA-256 planu 02:
`7e625d66712d9a3c2211f50691d3a93c2bc1b04210c4f303a745ff31e7e7f388`.
[Kontrola zakresu 02](../../dokumentacja%20pracy/2026-11-17_t023/scope_checks_02.json)
potwierdza hashe 25 źródeł, 11 artefaktów, 134 istniejących plików,
49 plików przerwanego przebiegu i 30 historycznych wejść T021.
[Kontrola dokumentacji 02](../../dokumentacja%20pracy/2026-11-17_t023/documentation_checks_02.json).

### Audyt instrukcji — część T017, 2026-11-16

[Raport audytu](../../docs/reports/instruction_audit_2026-11-16.md) obejmuje
pełny pakiet routingu: aktywny V0, eksperymentalny V4, kontrolę V1–V3,
wspólny opis narzędzia i siedmiu parametrów, przykłady, konstrukcję wiadomości
i ustawienia. INS-01 wykazał bezpośredni konflikt „użyj zawsze” z wyjątkami
no_tool, następnie usunięty w T018; INS-02 opisuje zbyt ogólną regułę „bez mięsa → vegetarian”.
Pozostałe ustalenia rozdzielają niedopowiedzenia, luki przykładów i różnice
preflight/konfiguracji od faktycznych sprzeczności instrukcji.

Wyodrębnione z AST funkcje aplikacji przechwycono lokalną atrapą klienta,
bez importu main, SDK API i bazy. Potwierdzono zgodność aktywnego buildera
z V0, dwie wiadomości (system i user), jedno narzędzie i siedem parametrów; parser przyjął
pięć unikatowych przykładów powtórzonych w V0–V4. Sprawdzono pięć przypadków
preflight. Dowody i hashe:
[audit_checks.json](../../dokumentacja%20pracy/2026-11-16_instruction_audit/audit_checks.json),
[wire_requests.json](../../dokumentacja%20pracy/2026-11-16_instruction_audit/wire_requests.json).
To kontrole kodu i instrukcji, nie pomiar rozumienia przez model.

Nie znaleziono instrukcji „pescetarian wymaga fish”: opis parametru i prompty
zgodnie wymagają jawnej preferencji. Audyt nie rozstrzyga przyczyny błędu T016.
Nie zmieniono promptu, schematu, kodu, danych, expected ani wcześniejszych
raportów. **0 rzeczywistych wywołań API**. Sam audyt nie kończył T017;
tabelę kontrastów, hipotezę i protokół uzupełniono następnie w sekcji
„T017 — diagnoza i kontrakt zakończone” powyżej.

### T018 — usunięcie INS-01 zakończone

Data: 2026-11-16. Na polecenie autorki wdrożono ROU-11 w opisie
`get_recommendations` w [llm_tools.py](../../core/llm_tools.py).
Wywołanie jest wymagane dokładnie raz dla prośby o posiłek zgodnej
ze wszystkimi obsługiwanymi wymaganiami. Opis wyklucza prośby poza zakresem,
dobór dla alergii, nieobsługiwane wykluczenia i sprzeczne preferencje;
nieobsługiwane wymaganie ma pierwszeństwo i nie może zostać pominięte.

[Porównanie schematu](../../dokumentacja%20pracy/2026-11-16_ins01_fix/schema_check.json)
potwierdziło, że zmieniło się tylko `RECIPE_TOOLS[0].function.description`.
Struktura, nazwa funkcji, parametry, enumy i wymagane pola są identyczne.
Prompt systemowy pozostaje V0; aktualny pakiet instrukcji używa już nowego
opisu funkcji. Warianty V0–V4 i zamrożone dane historycznych pomiarów
nie zostały nadpisane. Audyt INS-01 opisuje stan przed tą poprawką.

Pełna istniejąca regresja offline: **265 testów, 0 niepowodzeń,
0 błędów, 0 pominięć**. Dowody:
[wynik](../../dokumentacja%20pracy/2026-11-03_t006/ins01_full_2026_11_16.json),
[log](../../dokumentacja%20pracy/2026-11-03_t006/ins01_full_2026_11_16.log).
Obejmuje granice alergii/wykluczeń, no_tool, pojedynczy dispatch, parser
i instrumentację porównań. Żądania w testach były podstawione, rzeczywiste
API zablokowane. Nie dodawano testów porównujących literalne brzmienie opisu.

INS-01 jest usunięty na poziomie instrukcji. **0 rzeczywistych wywołań API**;
wpływu poprawki na decyzje modelu jeszcze nie zmierzono. Nie przypisujemy
nowemu opisowi dawnych wyników ani naprawy błędu diet/protein z T016.
T017 uzupełniono następnie o kontrakt i protokół opisane powyżej;
wdrożenie oraz pozostałe ustalenia audytu pozostają otwarte.

### T015 — przygotowanie V4 offline zakończone

Data: 2026-11-03. Najpierw zapisano H-T015 i RSC-09–RSC-12 w `spec.md`
oraz protokół T015-v1 w sekcji 8 `plan.md`; następnie przygotowano kod.
Baza zmian: commit `bf7b971`; nowe pliki i instrumentacja są jeszcze
w drzewie roboczym, z dokładnymi hashami zamrożonymi w manifeście.

[V4](../../evals/routing_prompts/V4.txt) to V3 z jednym akapitem
`OBSŁUGIWANE PREFERENCJE` przed parametrami. Utrzymuje pełny pozostały tekst,
pięć przykładów i pierwszeństwo granic obsługi. Nowy akapit przypomina
niezależność diety od kategorii, obsługę ryby i jawnej liczby propozycji;
nie kopiuje dosłownych zapytań `intent_004/010/032`. Skuteczności hipotezy
nie potwierdzono modelem. Wskazówki dotyczące jasnego opisu parametrów,
warunków wywołania i przypadków problematycznych wspiera
[oficjalna dokumentacja function calling](https://developers.openai.com/api/docs/guides/function-calling);
to podstawa projektowania instrukcji, nie dowód działania V4.

[Runner](../../evals/run_routing_pilot.py) ma nowy profil `t015`: V0/V4,
ta sama konfiguracja i przypadki, prompt wspólny dla obu trybów. Raport
T015-v1 pokaże każdy warunek wyboru, wyniki trzech docelowych przypadków,
wszystkie pogorszenia per-case i wywołania backendu z błędną semantyką.
Nie blokuje ani nie poprawia argumentów w runtime; to kryterium oceny.
T014 zachowuje swoją wcześniejszą regułę.

| Scenariusz / wymaganie | Dowód offline | Granica dowodu |
| --- | --- | --- |
| RSC-09–RSC-11; ROU-01/04/08 | V4 zachowuje przykłady V3, a pełny przebieg na atrapach przesyła dokładny prompt w raw/application. Reguła odrzuca każdy z trzech przypadków poniżej 3/3 w dowolnym trybie. | Mocki nie dowodzą, że model rzeczywiście wybierze vegetarian, fish lub top_n=4. Potrzebny pomiar T016. |
| RSC-12; ROU-05/09/10 | Wykrywane 3/3 → 2/3 oraz 2/3 → 1/3; osobny warunek odrzuca błędne argumenty przekazane do backendu mimo poprawy wyniku ogólnego. | Ocena na podstawie niezmienionych expected; bez pomiaru jakości wyszukanych przepisów. |
| Granice i progi | Pełne no_tool w obu trybach, dokładne ułamki 90%/90%/85%, błędy API, ucięcia, zmiany modelu i niekompletne/zduplikowane oceny. | Progi małej iteracji nie zaliczają ACC na pełnej regresji i holdoucie. |
| Integralność przygotowania | Dry-run bez klienta, hashe V0/V4 i źródłowego V3, konfiguracja, etykiety, treści zapytań i identyfikator reguły. Zmieniona reguła jest odrzucana przed utworzeniem klienta. | Nie jest zgodą na koszt przyszłego wykonania. |

Testy: [test_routing_t015.py](../../tests/test_routing_t015.py), **11/11**.
Pełna regresja: **265 testów, 0 niepowodzeń, 0 błędów, 0 pominięć**.
Rzeczywiste żądania API były zablokowane. Dowody:
[wynik nowych testów](../../dokumentacja%20pracy/2026-11-03_t006/t015_targeted.json),
[pełny wynik](../../dokumentacja%20pracy/2026-11-03_t006/t015_full.json),
[pełny log](../../dokumentacja%20pracy/2026-11-03_t006/t015_full.log).
Osobna [kontrola historii](../../dokumentacja%20pracy/2026-11-03_t015/history_check.json)
potwierdziła integralność 26 plików T014 i identyczny agregat jego 240 zapisanych
ocen po wydzieleniu wspólnego czytnika par wariantów. Starych wyników nie zmieniono.

Dry-run przygotował
[pierwotny manifest T016](../../dokumentacja%20pracy/2026-11-03_t016_campaign_01/prepared_manifest.json)
i kopie promptów. W chwili przygotowania: status `prepared`, `actual_calls=0`,
bez wyników kampanii. Późniejszy pomiar opisuje sekcja T016 poniżej:

- 20 ujawnionych zapytań × V0/V4 × 3 rundy × raw/application = **240 ocen**;
- **216 planowanych wywołań**, 120 raw + 96 application; retry 0;
- model gpt-4o-mini, temperatura 0,1, auto, parallel_tool_calls=false,
  limit 512 tokenów odpowiedzi, timeout 30 s;
- konserwatywna rezerwa **0,4310442 USD**, lokalny próg **0,50 USD**.

Kosztorys stosuje sprawdzone 2026-11-03
[stawki modelu](https://developers.openai.com/api/docs/models/gpt-4o-mini):
0,15 USD/milion tokenów wejściowych i 0,60 USD/milion wyjściowych.
Proxy wejścia: bajty UTF-8 zserializowanego żądania + 2000 tokenów narzutu;
wyjście przy limicie 512, bez cache. To szacunek rezerwy, nie gwarancja
rachunku; podatki i inne użycie konta są poza nim.

T016 będzie przesyłać do `https://api.openai.com/v1` treści tych 20
kontrolowanych zapytań, systemowy V0 lub V4 i schemat `get_recommendations`.
Nie przesyła katalogu bazy ani rzeczywistych rozmów użytkowników w treści
zapytań. W samym T015 wykonano **0 rzeczywistych wywołań API**; nie uzyskano
wówczas wyników jakości ani kandydata, aktywny V0 pozostał. Nie zmieniono
schematu, preflight, parsera, etykiet, danych ani progów końcowej akceptacji.
T016 następnie wykonano po poleceniu autorki; T009 i T012 pozostają wstrzymane.

### T016 — pomiar i przegląd zakończone

Data: 2026-11-03. Autorka poleciła „Wykonaj T016” po przedstawieniu
216 wywołań i rezerwy około 0,43 USD. Pełny
[raport](../../docs/reports/t016_routing_2026-11-03.md) zawiera warunki,
tabelę 20 przypadków, wszystkie warunki T015-v1, przegląd i decyzję.
240 ocen / 216 wywołań, 0 błędów API i ucięć, jeden resolved model.

| Wynik | V0 raw | V4 raw | V0 application | V4 application |
| --- | --- | --- | --- | --- |
| Poprawne oceny | 41/60 | 58/60 | 40/60 | 57/60 |
| Obsługiwane prośby | 23/42 | 40/42 | 22/42 | 39/42 |
| No_tool | 18/18 | 18/18 | 18/18 | 18/18 |
| Przypadki stabilne 3/3 | 13/20 | 19/20 | 13/20 | 19/20 |

**DEC-08: V4 nie kwalifikuje się według T015-v1; pozostawić V0.**
`intent_004/010` poprawne 3/3 w obu trybach. `intent_032` dostał poprawne
top_n=4, lecz niezamówione protein_preference=fish: raw 1/3, application 0/3
wobec 3/3 V0. Wszystkie pięć błędów V4 to ta sama semantyka; trzy application
trafiły do atrapy backendu. Nie badano, jakie przepisy zwróciłaby baza.

Siedem flag T015-v1 jest spełnionych, trzy nie: `targets_all`,
`no_case_regression`, `no_semantic_dispatch`. 95% application, 92,86%
obsługiwanych i 95% stabilności nie zastępuje tych warunków i nie zalicza ACC
na pełnej regresji lub nowym holdoucie. Reguła i expected pozostają bez zmian.
Przegląd w raporcie uzasadnia pozostawienie V0; jego znane wady nie są zamknięte.

[Audyt offline](../../dokumentacja%20pracy/2026-11-03_t016_campaign_01/audit.json)
niezależnie potwierdził źródła i ich kopie, oryginalny manifest, kompletność,
etykiety, semantykę pól, wszystkie flagi reguły i regresje. Usage: 556 830
tokenów wejściowych i 8894 wyjściowe; koszt obliczony bez cache 0,0888609 USD,
bez podatków i odczytu rachunku. Rezerwa 0,4310442 USD.
Dokładne źródła niezacommitowanego T015 zachowano w `frozen_inputs/`,
a bazowy commit `bf7b971` i stan drzewa w kontekście wykonania.
Nie zmieniano kodu, wejść ani reguły w trakcie pomiaru. Dokumentację wyniku
zaktualizowano po audycie. Nie wykonano wdrożenia, nowych testów aplikacji
ani drugiej kampanii; przed pomiarem obowiązywał wynik offline 265/265.

T016 zakończono pomiarem, audytem i decyzją. T017 to osobna, zaplanowana
diagnoza kontrastów diet/protein i specyfikacja następnej poprawki offline,
bez automatycznej kolejnej zmiany promptu lub płatnego pomiaru.

### Plan dowodów dla T014

| Wymaganie | Kryterium | Dowód do uzyskania |
| --- | --- | --- |
| ROU-07 | ACC-09/11 | T014.3: V3 no_tool 18/18 osobno w raw i application, routing_004 poprawny 3/3. Dowód dla celowanego zbioru, nie pełne zaliczenie ACC. Historyczny V2 15/18 pozostaje bez zmian. |
| ROU-08 | ACC-06/09 | Diff V2/V3, kompletność i zgodność przykładów, niezmieniony parser/schemat/preflight, test izolacji wariantu. W T014.2 przed API. |
| ROU-09 | ACC-09/11 | T014.3: oddzielne wyniki raw/application, 120/96 wywołań, po 12 poprawnych blokad application dla V0/V3, bez fałszywych blokad. Brak błędu raw dla blokowanego przypadku w tej kampanii; mechanizm rozdzielenia sprawdzony offline. |
| ROU-10 | Reguła iteracji; ACC bez zmian | T014.3: manifest, kompletny raport i audyt reguły wskazały kandydata V3. T014.4: przegląd zakończony, DEC-07 pozostawia V0; bez wdrożenia i bez zmiany reguły kandydata. |

Stan: T014.1–T014.4 zakończone. V3 zachowuje kwalifikację kandydata
na podstawie pomiaru; przegląd DEC-07 pozostawia aktywny V0.
Nie przenosimy wyników V2 na V3; potrzebna dalsza praca nad routingiem w T015.

### T014.2 — przygotowanie offline zakończone

Data: 2026-11-03. Specyfikacja T014.1 w commicie `0b313ab`;
instrumentacja T014.2 zamrożona hashami w manifeście, następnie zapisana
w commicie `261a04f` przed T014.3. Nie tworzono kolejnego dokumentu zadań.

[V3](../../evals/routing_prompts/V3.txt) różni się od V2 jednym akapitem
`PRIORYTET ZAKRESU` przed parametrami. Pięć pełnych przykładów i cały
pozostały tekst zachowano. Hipoteza: jawne pierwszeństwo granic obsługi
ograniczy pomijanie nieobsługiwanego wymagania przy zachowaniu poprawnego
kanału wywołania. Nie jest to potwierdzona skuteczność V3.

[Runner](../../evals/run_routing_pilot.py) otrzymał profil `t014`.
Raw i application otrzymują ten sam zamrożony prompt danego wariantu;
application zachowuje preflight, parser i dispatch, podmieniając wyszukiwanie
na atrapę. Aktywny `main.build_system_prompt` nadal odpowiada V0.
Schemat, reguły aplikacji, expected przypadków, dane i pięć SKU bez zmian.

[Dziesięć nowych testów](../../tests/test_routing_t014.py) sprawdza:

- ograniczony diff V2/V3 i zgodność aktywnego promptu z V0;
- przygotowanie bez API, liczebności, kosztorys i zakaz nadpisania kampanii;
- pełny przebieg na atrapach: 240 ocen / 216 wywołań klienta, wspólne
  prompty w obu trybach, blokady, limit odpowiedzi i odtworzenie stanu aplikacji;
- odrzucenie zmienionej konfiguracji lub promptu przed utworzeniem klienta;
- limit 216 wywołań oraz regułę wyboru: remis, granice no_tool, stabilność,
  wynik application i nową stałą regresję;
- kompletność i etykiety, zmianę modelu, błąd API i ucięcie odpowiedzi;
- zachowanie błędu raw także przy poprawnej blokadzie application.

Wyniki: **10/10 nowych testów; pełna regresja 254 testy, 0 niepowodzeń,
0 błędów, 0 pominięć**. Rzeczywiste żądania API były zablokowane.
To testy mechanizmu pomiaru, nie jakości odpowiedzi modelu.
Dowody: [wynik pełny](../../dokumentacja%20pracy/2026-11-03_t006/t014_full.json),
[log pełny](../../dokumentacja%20pracy/2026-11-03_t006/t014_full.log),
[wynik nowych testów](../../dokumentacja%20pracy/2026-11-03_t006/t014_targeted.json).
Katalog T006 zawiera współdzielony runner kontroli; prefiks wskazuje T014.

Dry-run utworzył
[pierwotny manifest](../../dokumentacja%20pracy/2026-11-03_t014_campaign_01/prepared_manifest.json)
oraz kopie V0/V3: w chwili przygotowania status `prepared`, faktyczne
wywołania **0**, bez wyników kampanii. Późniejszy pomiar opisuje sekcja T014.3.
Zamrożono hashe kodu, specyfikacji, zbiorów i promptów (także
źródłowego V2), przypadki, kolejność oraz konfigurację. Plan:

- 20 kontrolowanych zapytań × V0/V3 × 3 rundy × raw/application = **240 ocen**;
- 120 wywołań raw i 96 application = **216 wywołań API**, retry 0;
- `gpt-4o-mini`, temperatura 0,1, maksymalnie 512 tokenów odpowiedzi,
  timeout 30 s, `tool_choice=auto`, `parallel_tool_calls=False`;
- szacowana rezerwa **0,415881 USD**, lokalny próg zatrzymania **0,50 USD**.

Kosztorys wykorzystuje stawki 0,15 USD / milion tokenów wejściowych
i 0,60 USD / milion wyjściowych z
[karty modelu](https://developers.openai.com/api/docs/models/gpt-4o-mini),
sprawdzonej 2026-11-03. Wejście szacowane konserwatywnie przez bajty UTF-8
zserializowanych żądań plus 2000 tokenów narzutu na każde wywołanie;
wyjście przy maksymalnych 512 tokenach. Nie zakłada cache. To rezerwa
szacunku, nie gwarancja rachunku; podatki i inne użycie konta są poza nią.

Ewentualny T014.3 wysyła do `https://api.openai.com/v1` treść 20 kontrolowanych
zapytań, prompt systemowy V0 lub V3 i schemat `get_recommendations`.
Nie wysyła katalogu bazy ani rzeczywistych rozmów użytkowników w treści
zapytań. Ten opis i dry-run nie są zgodą na wysłanie lub koszt.
Zmiana zamrożonego wejścia przed T014.3 wymaga przygotowania nowego manifestu;
nie poprawiać hashów w starym. T009 i T012 pozostają wstrzymane.

### T014.3 — pomiar zakończony

Wykonano 2026-11-03 po poleceniu autorki „zrób commit i wykonaj T014.3”.
[Raport](../../docs/reports/t014_3_routing_2026-11-03.md) zawiera konfigurację,
pełną tabelę per-case, błędy, wynik reguły i odsyłacze do surowych dowodów.
240 ocen / 216 wywołań, jedna wersja modelu, 0 błędów API i ucięć.

| Wynik | V0 raw | V3 raw | V0 application | V3 application |
| --- | --- | --- | --- | --- |
| Poprawne oceny | 43/60 | 55/60 | 42/60 | 53/60 |
| Obsługiwane prośby | 25/42 | 37/42 | 24/42 | 35/42 |
| No_tool | 18/18 | 18/18 | 18/18 | 18/18 |
| Przypadki stabilne 3/3 | 14/20 | 18/20 | 14/20 | 17/20 |

**Kandydat V3 spełnia wcześniej ustaloną regułę T014.** Nie ma nowej
stałej regresji 3/3 → 0/3, ale `intent_032` application pogorszył się
z 3/3 do 2/3. Pozostają błędna dieta w `intent_004` i błędne odmowy
lub kanał w `intent_010`. Te problemy są jawnie opisane w raporcie.
88,33% wszystkich ocen application i 83,33% obsługiwanych próśb nie zalicza
progów 90%; celowany zbiór nie jest też holdoutem. ACC pozostają otwarte.

Usage: 527 994 tokeny wejściowe i 8918 wyjściowych; obliczenie bez cache
0,0845499 USD, bez podatków i bez odczytu rachunku. Rezerwa 0,415881 USD.
Audyt offline potwierdził kompletność, etykiety, hashe źródeł, agregaty,
unikalne identyfikatory 216 żądań i regułę wyboru. Zachowano dokładny
pierwotny manifest, kopie wejść oraz hashe 26 plików dowodowych.
Zmiany specyfikacji opisujące wyniki wprowadzono dopiero po zakończeniu
pomiaru i audycie; protokół użyty w pomiarze zachowano w `frozen_inputs/`.
Nie zmieniono kodu aplikacji, promptu V0, schematu, etykiet, progów ani danych.
Późniejszy przegląd i decyzję opisuje sekcja T014.4 poniżej.

### T014.4 — przegląd i decyzja zakończone

Data: 2026-11-03. Na polecenie wykonania T014.4 przejrzano raport T014.3,
surowe wyniki, dispatch i aktualny kontrakt argumentów. **DEC-07:
pozostawić V0; V3 wymaga dalszego dopracowania przed wdrożeniem.**
To wynik przeglądu zleconego agentowi, nie deklaracja osobnego zatwierdzenia
przez autorkę ani akceptacji MVP.

| Obszar | Dowód z T014.3 / kontrola offline | Znaczenie dla decyzji |
| --- | --- | --- |
| Kwalifikacja V3 | Reguła wskazała V3; no_tool 18/18 w obu trybach, wynik i stabilność raw lepsze, brak nowej stałej regresji 3/3 → 0/3. | Zachować wynik wyboru kandydata. Przegląd nie zmienia reguły po pomiarze. |
| Pominięta dieta | `intent_004` application: V0 0 wywołań backendu, V3 3 wywołania z `diet=none`, expected `vegetarian`. Parser akceptuje te strukturalnie poprawne argumenty. | Błąd kanału V0 zmienił się w przekazanie niepełnego wymagania V3. To ryzyko niezgodnej rekomendacji; nie dowód, że rzeczywisty katalog zwrócił niezgodny przepis, bo wyszukiwanie było atrapą. |
| Błędna odmowa ryby | `intent_010` application: V3 0/3, brak blokady preflight, brak dispatch. Surowe treści pokazują odmowę albo opis narzędzia w content. | Problem decyzji/kanału modelu; nie należy go „naprawiać” dopuszczeniem JSON-a z tekstu lub usunięciem expected. |
| Niestabilna regresja liczby wyników | `intent_032` application: V0 3/3, V3 2/3; parser przyjmuje oczekiwane `top_n=4`. | Model wymyślił ograniczenie liczby propozycji. Brak stałej regresji nie oznacza braku regresji w ogóle. |
| Jakość application | 53/60 = 88,33%, obsługiwane 35/42 = 83,33%, stabilne 17/20 = 85%. | Poprawa wobec V0, lecz dwa pierwsze wyniki poniżej liczbowych progów ACC. Stabilność osiąga liczbowo 85% tylko na tym ujawnionym podzbiorze; brak pełnej regresji i nowego holdoutu. Żadne ACC nie zostaje zaliczone. |
| Granice obsługi | `routing_004` raw poprawny 3/3; application blokuje go bez modelu. | Zachować tę poprawę w następnej iteracji. Nie uogólniać wyniku na dowolną parafrazę ani utożsamiać preflight z sukcesem modelu. |

Decyzja wdrożeniowa wynika przede wszystkim z pomijanej diety i otwartych
błędów semantyki; wyniki ACC stanowią kontekst, nie nowy próg dopisany
do reguły kandydata. Pozostawienie V0 nie oznacza uznania go za poprawny:
jego znane błędy kanału pozostają otwarte. T014 kończy się udokumentowaną
decyzją, a nie ogłoszeniem naprawy całego routingu.

[Kontrola przeglądu offline](../../dokumentacja%20pracy/2026-11-03_t014_4/review.json)
potwierdziła integralność 26 plików dowodowych, niezmieniony kod i zbiory,
liczniki dispatch trzech problematycznych przypadków oraz akceptację
`top_n=4` przez istniejący parser. Nie uruchamiała aplikacji, API ani bazy.
Nie dodawano testów udających dowód jakości LLM; nie ponawiano kampanii.
Kod aplikacji i aktywny prompt pozostały bez zmian, więc testy wdrożenia V3
nie mają zastosowania. Ostatni pełny wynik kodu pozostaje 254/254 z T014.2,
bez przypisywania go do nowego przebiegu. W T014.4: **0 wywołań API**.

T014 oznaczono jako wykonane, a następną pracę zapisano jako T015:
hipoteza dla `intent_004/010/032`, protokół, wariant eksperymentalny i kontrole
offline, bez wdrożenia i bez uruchomienia nowego płatnego pomiaru.
Zachowano pierwotny raport, surowe wyniki, hashe, etykiety i progi.
Nie tworzono kolejnego pliku raportu; decyzja jest w DEC-07 i tej sekcji.

### Mały pilotaż T009P

Osobny podzbiór 20 istniejących przypadków i expected, bez holdoutu.
Kod [run_routing_pilot.py](../../evals/run_routing_pilot.py), przypadki
[routing_pilot_cases.json](../../evals/routing_pilot_cases.json).
Testy [test_routing_pilot.py](../../tests/test_routing_pilot.py) sprawdzają:
zgodność podzbioru z oryginałem, brak API w dry-run, rezerwację budżetu
przed wysłaniem, limit odpowiedzi, 120 kontrolowanych wywołań i kolejność,
niezmieniony prompt aplikacji, decyzję przy remisie, zakaz selektywnego
wznawiania, odrzucenie zmienionego manifestu oraz klasyfikację ucięcia jako błędu.
Po zatwierdzeniu payloadu/kosztu wykonano osobny pilotaż: 120 wywołań,
0 API errors i ucięć. V0 42/60, V2 57/60; V2 miał 3 błędne tool calle
dla `routing_004`, dlatego reguła zachowała V0.
[Raport i dowody](../../docs/reports/routing_pilot_2026-11-03.md).
To wynik raw na celowanym podzbiorze, nie zaliczenie ACC na regresji
i holdoucie. Pełna kampania T009 pozostaje wstrzymana.

Pełna regresja po dodaniu pilotażu: **244 testy, 0 niepowodzeń, 0 błędów,
0 pominięć**. [Wynik](../../dokumentacja%20pracy/2026-11-03_t006/pilot_full.json)
i [log](../../dokumentacja%20pracy/2026-11-03_t006/pilot_full.log).
Wszystkie wywołania w testach były podstawione, rzeczywiste API zablokowane.

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

T008 zakończyło wymagania i protokół. W T009 wykonano część offline;
płatny etap jest wstrzymany na decyzję autorki: pozostawić tylko offline.
Nie powstały wyniki kampanii; progi routingu pozostają nieocenione.
Aktywny prompt, dane i progi pozostają bez zmian.
