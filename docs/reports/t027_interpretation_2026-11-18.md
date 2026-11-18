# T027 — diagnostyka V4/IR-1, 2026-11-18

**Wynik: IR-1 nie kwalifikuje się według IR1-D1 (DEC-16).** W raw uzyskał 22/36 poprawnych wyników wobec 26/36 V4. Domyślny tryb pozostaje legacy/V0. T027 jest zakończonym eksperymentem z wynikiem negatywnym; nie uruchamiamy kolejnego wariantu ani wdrożenia.

## Protokół i kompletność

Zatwierdzony plan: `b2fc0dad372996b2f5c2b45d7fe27c61b12db08eb563755e35f8e23486291477`. Źródła T026 w commicie c20a118; nowy wykonawca i testy zamrożone jako niezacommitowane źródła z hashami. Dwanaście istniejących zapytań i expected, dziewięć tool i trzy no_tool, po trzy rundy A/B, B/A, A/B. A to świeże V4, B to IR-1; wspólne gpt-4o-mini, temperatura 0,1, limit odpowiedzi 1024, retry=0 i timeout 30 s. Zmienianym czynnikiem jest cała warstwa interpretacji.

Wykonano 72/72 SDK, uzyskano 72 odpowiedzi i unikatowe request IDs, jeden resolved model gpt-4o-mini-2024-07-18. Zero błędów API/metadanych, bez wznowienia lub ponowień. Każda odpowiedź daje raw ocenę i zależny application_replay; 72 replay nie są kolejnymi wywołaniami LLM ani niezależnym pomiarem. Backend/katalog nie był wykonywany. Jedna prośba bezmleczna jest blokowana w replay; jej raw należało do zatwierdzonego planu.

## Wyniki

| Miara | V4 | IR-1 |
| --- | ---: | ---: |
| Raw: poprawne łącznie | 26/36 | 22/36 |
| Raw: stabilne przypadki 3/3 | 8/12 | 6/12 |
| Replay: poprawne łącznie | 29/36 | 25/36 |
| Replay: stabilne przypadki 3/3 | 9/12 | 7/12 |
| Raw: obsługiwane prośby | 20/27 | 19/27 |
| Raw: poprawne no_tool | 6/9 | 3/9 |
| Raw: błędny zamiar dispatch | 7 | 14 |
| Replay: błędny symulowany dispatch | 4 | 11 |

To ocena interpretacji z atrapą wyszukiwania, nie błędnie wydane rzeczywiste przepisy. V4 też nie jest kandydatem do wdrożenia. Zysk replay nad raw wynika z ochrony przed nieobsługiwanym wykluczeniem; nie zalicza to modelowi interpretacji.

### Wynik każdego przypadku

| ID | V4 raw | IR-1 raw | V4 replay | IR-1 replay |
| --- | ---: | ---: | ---: | ---: |
| intent_003 | 3/3 | 3/3 | 3/3 | 3/3 |
| intent_004 | 3/3 | 0/3 | 3/3 | 0/3 |
| intent_015 | 3/3 | 2/3 | 3/3 | 2/3 |
| intent_025 | 3/3 | 3/3 | 3/3 | 3/3 |
| intent_032 | 2/3 | 3/3 | 2/3 | 3/3 |
| v5_diag_004 | 0/3 | 3/3 | 0/3 | 3/3 |
| v5_diag_008 | 3/3 | 2/3 | 3/3 | 2/3 |
| v5_diag_009 | 3/3 | 0/3 | 3/3 | 0/3 |
| v5_diag_010 | 0/3 | 3/3 | 0/3 | 3/3 |
| routing_005 | 3/3 | 3/3 | 3/3 | 3/3 |
| routing_006 | 3/3 | 0/3 | 3/3 | 0/3 |
| v5_diag_012 | 0/3 | 0/3 | 3/3 | 3/3 |

Regresje raw: intent_004, intent_015, v5_diag_008, v5_diag_009 i routing_006. Poprawy: intent_032, v5_diag_004 i v5_diag_010. Nie łączymy tego pomiaru z dawnymi T016/T023; świeża kontrola V4 ma m.in. intent_004 3/3. Wspólny limit tutaj wynosi 1024; nie przypisujemy przyczynowo różnicy limitowi ani jednemu zdaniu promptu.

### Reguła IR1-D1

| Warunek ustalony przed pomiarem | Spełniony |
| --- | --- |
| valid_complete_measurement | tak |
| no_tool_all | nie |
| tool_accuracy | nie |
| stable_cases | nie |
| targets_all | nie |
| no_case_regression | nie |
| more_correct_tool_trials | nie |
| no_IR_protocol_or_validation_errors | tak |
| no_incorrect_dispatches | nie |

## Co dokładnie zawiodło

Wszystkie 36 odpowiedzi IR-1 ma poprawny call, schemat i dosłowne źródła; request_kind jest poprawny 36/36. Nie było błędu kanału. Dokładny zbiór faktów zgadza się jednak z adnotacją tylko w 19/36 prób. Strict i source potwierdzają format oraz cytat, nie kompletność lub znaczenie.

- intent_004: we wszystkich trzech próbach model przekazał wykluczenie mięsa, lecz pominął kategorię deser. Kompilator poprawnie ustalił vegetarian i zastosował domyślną kolację. Błąd dotyczy brakującego faktu kategorii, nie reguły bez mięsa → vegetarian.
- v5_diag_009: w 3/3 pominięto lunch; w v5_diag_008 stało się to w 1/3. Gluten, low_kcal i jawny czas pozostawały, lecz brak kategorii dawał kolację. W intent_015 raz pominięto low_kcal.
- routing_006: w 3/3 żądanie mięsa przy vegan zastąpiono exclusion/meat/waived; zabrakło wymaganego protein/meat oraz kategorii obiad. Poprawnie działający kompilator nie dostał faktów konfliktu, więc dopuścił wyszukanie vegan.
- v5_diag_012: w 3/3 bezmleczny błędnie stał się exclusion/lactose zamiast unsupported/exclusion. Raw dopuścił wyszukiwanie, a preflight zatrzymał je dopiero w replay. Zachowujemy oba wyniki oddzielnie.
- v5_diag_004: wynik końcowy poprawny 3/3 mimo pominiętej kategorii kolacja w 3/3. Domyślna kategoria przypadkiem pokryła się z gold; dlatego wynik końcowy nie zastępuje oceny faktów.

IR-1 ma 8 porażek semantyki i 6 decyzji; V4 odpowiednio 4 i 6. Wniosek z zachowanych śladów: ta wersja ekstrakcji gubi lub błędnie oznacza wymagania. Nie jest to dowód awarii kompilatora ani odrzucenie każdej możliwej architektury IR.

### Warunkowa poprawność pól IR-1

| Pole | Poprawne / oceniane |
| --- | ---: |
| diet | 27/27 |
| protein_preference | 27/27 |
| restrictions | 27/27 |
| nutrition_goal | 26/27 |
| category | 20/27 |
| time_max | 27/27 |
| top_n | 27/27 |

Te 27 prób dotyczy wyłącznie expected=tool i poprawnego strukturalnie search. Nie obejmują sześciu błędnych decyzji w no_tool. Wyniku 27/27 dla diety lub restrykcji nie wolno przedstawiać jako poprawnej obsługi konfliktu vegan+mięso lub bezmleczności.

## Koszt i kontrola wykonania

Użycie: 160416 tokenów wejścia, 4056 wyjścia, 164472 łącznie. Referencyjny koszt bez cache: **0.026496 USD** przy 0,15/0,60 USD za milion tokenów. To wyliczenie z usage, nie odczyt faktury dostawcy. Rezerwa przed żądaniami wyniosła 0,1637217 USD przy zatwierdzonym lokalnym progu 0,50 USD.

Poza 72 generacjami wykonano wcześniej jeden GET metadanych, bez generacji. Weryfikacja kodu: 366/366 testów, 0 pominięć, rzeczywisty SDK i zapisy katalogu zablokowane; 35 odczytów PostgreSQL i operacje wyłącznie w izolowanej SQLite. Testy sprawdzają instrumentację, nie dowodzą jakości LLM.

## Decyzja i dalsza praca

DEC-16: IR-1 nie kwalifikuje się według zamrożonej IR1-D1. Pozostaje domyślny legacy/V0. T027 zamykamy z wynikiem negatywnym; brak automatycznej zmiany modelu, promptu, schematu, domyślnego trybu lub kolejnego płatnego pomiaru. Żadne ACC nie jest zaliczone.

Przed kolejną implementacją potrzebny jest osobny projekt kompletności ekstrakcji: rozróżnienie braku wymagania od pominiętego rozpoznania, kategoria/cel, wymagane białko kontra negacja i nieobsługiwane wykluczenie. Rozważyć jawne grupy pól i ograniczone reguły domenowe, ocenić ich granice na zachowanych kontrastach oraz ustalić kryteria przed kodem. Samo dalsze poprawianie kanału nie odpowiada zaobserwowanym błędom.

To jawny zestaw diagnostyczny, nie nowy holdout ani pomiar rekomendacji od A do Z. Pełna kwalifikacja pozostaje w T010/T013 ze świeżym aktywnym V0; T009/T012 nadal są wstrzymane.

## Dowody

- [Plan](../../dokumentacja%20pracy/2026-11-18_t027/campaign/plan.json), [pełne żądania](../../dokumentacja%20pracy/2026-11-18_t027/campaign/payloads.json), [przypadki i adnotacje](../../dokumentacja%20pracy/2026-11-18_t027/campaign/cases.json).
- [72 obserwacje z odpowiedziami dostawcy](../../dokumentacja%20pracy/2026-11-18_t027/campaign/results.json), [porównanie](../../dokumentacja%20pracy/2026-11-18_t027/campaign/comparison.json), [stan i rezerwacje](../../dokumentacja%20pracy/2026-11-18_t027/campaign/state.json).
- [Powtórne przeliczenie offline](../../dokumentacja%20pracy/2026-11-18_t027/measurement_audit.json), [hashe zakończonego pakietu](../../dokumentacja%20pracy/2026-11-18_t027/completed_campaign_hashes.json), [regresja](../../dokumentacja%20pracy/2026-11-18_t027/full.json).
- [Projekt IR-1](../../specs/001-mvp-stabilization/interpretation-contract.md), [stan i mapa dowodów](../../specs/001-mvp-stabilization/verification.md#t027--diagnostyka-zakończona).
