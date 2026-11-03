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
