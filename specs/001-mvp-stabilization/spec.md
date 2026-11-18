# Specyfikacja — stabilizacja istniejącego MVP

Data: 2026-10-22<br>
Wersja dokumentu: 0.29; projekt T020 zakończony: 2026-11-18<br>
Status: zakres, progi i DEC-01–03 zatwierdzone; wymagania integralności
i błędów wdrożone w T006; protokół T008 opracowany. Pięć SKU pozostaje wstrzymanych.

Nawigacja: [kryteria](acceptance.md) · [plan](plan.md) ·
[zadania](tasks.md) · [weryfikacja](verification.md) · [projekt IR-1](interpretation-contract.md).

## 1. Cel dokumentu

Dokument określa rezultat, do którego dążymy przed dodawaniem kolejnych
funkcji. Stanowi punkt wyjścia do specyfikacji wymagań w podejściu
spec-driven development (SDD). Opisuje oczekiwany zakres pierwszej wersji,
a nie potwierdzenie, że wszystkie wymienione funkcje są już ukończone.

Dokument jest nadrzędnym opisem granic MVP. Szczegółowe kontrakty
rozwijają te ustalenia. W razie rozbieżności należy uzgodnić i zaktualizować
dokumenty przed implementacją; rozbieżność nie upoważnia do cichej zmiany
zachowania aplikacji. Historyczne raporty pozostają zapisem dawnych wersji.

## 2. Cel pierwszej wersji

Pierwsza wersja ma być ustabilizowanym, lokalnym demonstratorem obecnego
asystenta kulinarnego dla jednej marki spożywczej. Celem tego etapu jest
poprawa niezawodności, jakości odpowiedzi i możliwości oceny istniejącego
przepływu, bez dodawania nowych funkcji użytkowych. Użytkownik opisuje po polsku,
jakiego posiłku szuka. System interpretuje prośbę, wybiera zgodne przepisy
z przygotowanego katalogu, dobiera produkty marki według jawnych reguł
i prezentuje wynik wraz z wartościami odżywczymi.

MVP ma umożliwić demonstrację i ocenę trzech elementów projektu:

1. Interpretacji preferencji zapisanych językiem naturalnym przez LLM.
2. Deterministycznej selekcji przepisów i doboru produktów marki.
3. Kontrolowanej prezentacji danych pochodzących z backendu.

Docelowa wizja obejmuje SaaS i widget na stronach marek. Ich pełna realizacja
nie jest warunkiem ukończenia tego MVP.

## 3. Granice etapu stabilizacji

Punktem odniesienia jest zestaw funkcji istniejących w repozytorium
2026-10-22. Commit i wersję danych utrwalono w
[raporcie bazowym](../../docs/reports/baseline_2026-10-22.md).
Obecność funkcji w kodzie nie oznacza, że jej jakość została zaakceptowana.

| ID | Granica zakresu | Konsekwencja |
| --- | --- | --- |
| Z-01 | Jedna marka demonstracyjna: Winiary | Jeden przygotowany katalog SKU; izolacja wielu klientów wymaga późniejszej specyfikacji. |
| Z-02 | Lokalny sposób uruchomienia obecnego prototypu | Wystarcza istniejący punkt wejścia i instrukcja przekazania zapytania; interaktywna konsola, frontend i publiczne API nie są wymagane. |
| Z-03 | Każde zapytanie jest samodzielne | Nie zakładamy pamięci wcześniejszych wypowiedzi ani obsługi odwołań typu „a teraz bez ryby”. |
| Z-04 | Bez nowych funkcji użytkowych | Poprawiamy i weryfikujemy obecne zachowanie, bez nowych diet, ograniczeń, parametrów i sposobów interakcji. |

Zmiana tych założeń wymaga aktualizacji zakresu i oceny dodatkowej pracy.

### Obowiązujące decyzje

Ta tabela jest bieżącym rejestrem decyzji. Dawne raporty zachowują kontekst,
ale nie zastępują jej ani stanów w `tasks.md`.

| ID | Stan | Ustalenie |
| --- | --- | --- |
| DEC-01 | Zatwierdzona | Nieznane statusy laktozy pozostają. Takie SKU są pomijane przy `lactose_free`. Dodawanie produktów i dopuszczanie kolejnych SKU do tej polityki pozostaje poza MVP. |
| DEC-02 | Zatwierdzona; wdrożona w T006 | Brak wymaganej polityki składnika nie oznacza zgodności. Szczegóły opisują INT-01–INT-04. |
| DEC-03 | Zatwierdzona; wdrożona w T006 | Błąd przygotowania przepisu przerywa zapytanie; nie zwracamy częściowego sukcesu ani pozornego braku wyników. Błędy programistyczne nie są maskowane jako poprawna odpowiedź. |
| DEC-04 | Wstrzymana przez autorkę | Nie prowadzimy obecnie przeglądu źródeł pięciu SKU ani zależnych korekt czy wyłączeń. Luka podstawy makro pozostaje otwarta. |
| DEC-05 | Zatwierdzona 2026-11-03 | T009 pozostaje wyłącznie przygotowaniem offline. Płatna kampania API jest wstrzymana; wznowienie wymaga jawnej decyzji autorki. Nie oceniono progów jakości modelu. |
| DEC-06 | Pilotaż zatwierdzony i wykonany 2026-11-03 | Po jednoznacznej zgodzie wykonano 120 wywołań V0/V2 na 20 przypadkach. Wybór pozostawia V0: V2 poprawił kanał, ale nie spełnił warunku wszystkich no_tool. Duża kampania pozostaje wstrzymana; wynik nie zalicza MVP ani nie podmienia promptu. |
| DEC-07 | Decyzja przeglądu T014.4, 2026-11-03 | Pozostawić aktywny V0; V3 zachowuje kwalifikację kandydata T014.3, ale wymaga dalszego dopracowania. W application pomija dietę w intent_004, błędnie odmawia obsługi intent_010 i ma niestabilną regresję intent_032. Nie wdrażać V3 na podstawie tego pomiaru. Uzasadnienie i dowody w sekcji T014.4 mapy weryfikacji; ACC i reguła wyboru pozostają bez zmian. |
| DEC-08 | Decyzja przeglądu T016, 2026-11-03 | V4 nie kwalifikuje się według T015-v1 mimo 57/60 application. W intent_032 dodaje fish bez jawnej prośby: regresja application 3/3 → 0/3 i trzy wywołania backendu z błędną semantyką. Pozostawić V0; dalsza diagnoza relacji diety i preferencji białka w T017 offline. Zachować progi, expected i regułę oraz raport T016. |
| DEC-09 | Zatwierdzona przez autorkę 2026-11-16 | Samo „bez mięsa” oznacza domyślnie vegetarian. Jawne dopuszczenie ryb lub wskazanie diety doprecyzowuje tę regułę; sama zgoda na ryby nie wymaga fish. Obowiązuje tabela prośba → interpretacja poniżej, rozwinięta w kontrakcie T017. |
| DEC-10 | Kontrakt T019; komunikat i kontrola odpowiedzi wdrożone w T022, 2026-11-17 | No_tool oznacza brak wywołania, bez nowego narzędzia ani pola powodu. Model wybiera decyzję, aplikacja tworzy komunikat. Powód biznesowy pozostaje nieznany; znany jest etap wykonania. NTO-01–08 określają kontrakt; T022 wdrożyło MSG-01/06 oraz zatrzymanie length/content_filter/refusal przed dispatch, ze wspólną diagnostyką T022-v1. Jakość decyzji modelu wymaga pomiaru. |
| DEC-11 | Zlecono projekt, 2026-11-16 | T020 ma zaprojektować obsługę wielu celów żywieniowych, np. low_kcal + keto. Zakres obejmuje semantykę połączeń i wpływ na kontrakt oraz backend. Nie jest zleceniem implementacji ani rozszerzeniem wszystkich pól do list. |
| DEC-12 | Przygotowano offline w T021, 2026-11-17; niewdrożone | Kandydat evals/routing_prompts/V5.txt zachowuje format V4, z 18 kontrastowymi demonstracjami zgodnymi z T017/T019. Zmieniono dwie reguły „bez mięsa” i wprowadzenie do przykładów w granicach T017; pozostałe instrukcje i wspólny schemat zachowano. Przygotowanie nie potwierdza skuteczności i nie upoważnia do płatnego pomiaru lub wdrożenia. |
| DEC-13 | Decyzja przeglądu T023, 2026-11-17 | V5 nie kwalifikuje się według T017-v1. W kompletnym pomiarze 02: application 78/96 wobec V4 86/96, sześć regresji per-case i 13 błędnych semantycznie dispatch. Niezamówione fish spadło 4 → 0 w obu trybach, ale intent_004 i diag_004 pozostały 0/3. Pozostawić aktywny V0; bez wdrożenia V4/V5 ani zaliczenia ACC. Przerwany przebieg 01 zachowano osobno. |
| DEC-14 | Wdrożono w T024, 2026-11-17 | Ograniczona gramatyka lokalnej negacji pojedynczego wykluczenia i nowych klauzul usuwa pięć wskazanych fałszywych blokad. Dodatnie nieobsługiwane wykluczenia, niejednoznaczne listy i pierwszeństwo alergii zachowano. Przejście preflight bez próby LLM nie zalicza interpretacji modelu; dawne wyniki i expected pozostają bez zmian. |
| DEC-15 | Wybrany projekt T025, 2026-11-18; niewdrożony | IR-1: jeden wymuszony submit_recipe_interpretation ze ścisłym schematem faktów, bez dostępu do katalogu. Aplikacja waliduje fakty, stosuje ROU i defaulty oraz wybiera search/no_search/error. Model nie wypełnia domyślnych argumentów. W przyszłym trybie IR brak calla jest błędem protokołu, a biznesowe no_tool oznacza brak dispatch. Legacy NTO i aktywny V0 pozostają; migracja i scenariusze są w interpretation-contract.md. |
| DEC-16 | Przegląd T027, 2026-11-18 | IR-1 nie kwalifikuje się według IR1-D1: raw 22/36 wobec świeżego V4 26/36, pięć regresji per-case i 11 błędnych symulowanych dispatch w replay. Format IR poprawny 36/36, lecz dokładne fakty tylko 19/36. Pozostawić domyślny legacy/V0; zakończyć eksperyment bez automatycznej podmiany lub kolejnego pomiaru. Następny T028 dotyczy projektu kompletności ekstrakcji, bez API i wdrożenia. |
| DEC-17 | Projekt T028, 2026-11-18; niewdrożony | CMP-1: ograniczona lokalna kontrola kategorii, celu, operatorów białka i wybranych wykluczeń przed dispatch. Zachować wire IR-1 i kompilator; nie dopisywać faktów. Wykryty brak lub nierozstrzygnięty zakres przy proponowanym search daje coverage error/MSG-06, nie poprawne no_tool. Brak dopasowania nie dowodzi kompletności. T029 implementuje i sprawdza ochronę offline na zachowanych odpowiedziach, bez ponawiania API i zmiany domyślnego legacy/V0. |

W tym etapie dopuszczalne są poprawki błędów, zmiany promptu, refaktoryzacja,
korekty istniejących danych, testy, narzędzia pomiarowe i dokumentacja,
jeśli służą obecnym funkcjom. Rozbudowa katalogu o nowe przepisy lub SKU
nie jest warunkiem ukończenia MVP. Przygotowanie testów i nowych przypadków
oceny jest pracą nad weryfikacją, a nie rozszerzeniem możliwości chatbota.

## 4. Użytkownik i podstawowy scenariusz

Użytkownikiem jest osoba szukająca pomysłu na posiłek z uwzględnieniem
preferencji obsługiwanych przez katalog. Autorka projektu przygotowuje
dane, reguły oraz środowisko demonstracyjne poza rozmową z użytkownikiem.

Przykładowe zapytanie: „Poleć dwie szybkie kolacje wegańskie do 30 minut”.

Oczekiwany przebieg:

1. Użytkownik wprowadza zapytanie po polsku.
2. Aplikacja sprawdza zakres obsługi i interpretuje parametry zapytania.
3. Backend wybiera przepisy zgodne z parametrami.
4. Dla odpowiednich składników dobiera zgodne SKU marki, jeśli są dostępne.
5. Oblicza wartości odżywcze na podstawie finalnego doboru składników.
6. Lokalny renderer przedstawia wynik. Brak wyników lub błąd prowadzi
   do odpowiedniego komunikatu zamiast wygenerowania zastępczego przepisu.

System może zwrócić mniej propozycji niż zażądano, jeżeli katalog nie zawiera
wystarczającej liczby zgodnych przepisów. Nie rozluźnia samodzielnie ograniczeń.

## 5. Istniejące funkcje objęte stabilizacją

Identyfikatory MVP oznaczają obszary zakresu. Szczegółowe wymagania
i przypadki akceptacyjne zostaną wyprowadzone z nich w kolejnym kroku SDD.
Poniższa lista nie jest planem dodania funkcji; określa, które istniejące
mechanizmy mają zostać opisane, sprawdzone i poprawione w razie błędów.

| ID | Obszar | Oczekiwany rezultat |
| --- | --- | --- |
| MVP-01 | Interpretacja zapytania | Rozpoznanie parametrów i decyzji o wyszukiwaniu na podstawie polskiej wypowiedzi. |
| MVP-02 | Filtrowanie i ranking | Wybór przepisów z katalogu według jawnych reguł, z zachowaniem aktywnych ograniczeń. |
| MVP-03 | Dobór produktów marki | Zastosowanie reguł wyboru SKU dla marki demonstracyjnej bez wymyślania produktów. |
| MVP-04 | Wartości odżywcze | Obliczenie kcal, białka, tłuszczów i węglowodanów z danych finalnie użytych składników i SKU. |
| MVP-05 | Prezentacja | Odpowiedź po polsku z nazwą przepisu, czasem, porcjami, makro na porcję oraz dostępnymi składnikami i instrukcjami. |
| MVP-06 | Kontrolowane sytuacje wyjątkowe | Rozróżnienie braku wyników, braku wyszukiwania, niepoprawnych argumentów, błędu danych i niedostępności LLM. |
| MVP-07 | Przygotowany katalog | Dane i polityki wystarczające do demonstracji, sprawdzone walidatorem i przeglądem treści. |
| MVP-08 | Weryfikacja i odtwarzalność | Testy, ewaluacja LLM oraz opis uruchomienia i odtworzenia wersji demonstracyjnej. |

### Obecnie obsługiwane parametry

- Dieta: brak wskazania, wegetariańska, wegańska, pescetariańska.
- Preferowane źródło białka: brak wskazania, mięso lub ryby, z kontrolą
  sprzeczności z dietą.
- Ograniczenia: `gluten_free`, `lactose_free` oraz ich połączenie.
- Cel żywieniowy: standardowy, niskokaloryczny, wysokobiałkowy lub keto.
- Kategoria: śniadanie, lunch, obiad, kolacja, deser lub przekąska.
- Maksymalny czas przygotowania i liczba oczekiwanych propozycji.

`gluten_free` i `lactose_free` są już obecne w schemacie narzędzia,
backendzie i testach. Ich wymienienie oznacza utrzymanie i weryfikację
istniejącej obsługi. MVP nie obejmuje wdrażania nowych ograniczeń ani
rozszerzania znaczenia obecnych flag.

Cele żywieniowe podlegają regułom katalogu, filtrowania i rankingu.
Nie oznaczają indywidualnego planu dietetycznego. Dokładne progi,
wartości domyślne, negacje i interpretacje słów takich jak „szybki”
muszą zostać opisane w szczegółowych wymaganiach.

### Zasady doboru SKU i prezentacji

- Produkt marki może zostać użyty tylko wtedy, gdy istnieje w katalogu
  i spełnia obowiązujące reguły zgodności.
- Promocja marki nie ma pierwszeństwa przed ograniczeniami użytkownika.
- Brak odpowiedniego SKU pozwala pozostawić składnik generyczny wyłącznie
  wtedy, gdy sam składnik spełnia aktywne warunki.
- Makro wynika z finalnego wyboru, z rozróżnieniem ilości na cały przepis
  i wartości na porcję.
- LLM interpretuje zapytanie; backend wybiera wyniki i oblicza wartości,
  a lokalny renderer przedstawia dane. Model nie dopisuje faktów do odpowiedzi.
- Puste sekcje danych są pomijane. Niepoprawny payload powoduje komunikat
  błędu zamiast zgadywania brakujących informacji.

### Wymagania szczegółowe: integralność i błędy (T005)

Opracowano 2026-11-03 na podstawie DEC-02/03; wdrożono w T006.
Wymagania pozostają kontraktem zachowania, a dowody są w raporcie T006.
Nie zmieniają interpretacji zapytań przez model, progów akceptacji ani danych SKU.

#### Zakres sprawdzania

**Kandydat** to przepis rozpatrywany przez backend po dopasowaniu kategorii
i limitu czasu, przed kwalifikacją według polityk składników i przygotowaniem
wyniku. Nie trzeba sprawdzać całego katalogu przy każdym zapytaniu.
Niezależny walidator nadal sprawdza wszystkie koncepty używane w katalogu.

Brak polityki oznacza brak rekordu dla `concept_id`, nie wartość `0`
ani dozwolone `NULL` w `is_lactose_free`. Integralność wymaga polityki
każdego składnika kandydata także wtedy, gdy nie wybrano diety. Dzięki temu
zachowanie nie zależy od przypadkowej kolejności składników i filtrów.

| ID | Wymaganie | Powiązanie |
| --- | --- | --- |
| INT-01 | Przed decyzją o zgodności kandydata sprawdzić obecność polityk wszystkich jego składników. Brak choć jednej jest błędem danych; nie zastępować jej wartościami domyślnymi, nie ratować przez SKU. Obowiązuje również bez diety, dla pescetarian i preferencji mięso/ryby. | DEC-02; ACC-01/07/08 |
| INT-02 | Jawna niezgodność poprawnej polityki z dietą lub ograniczeniem normalnie wyklucza kandydata. Poprawna polityka bez wymaganej cechy mięso/ryby również normalnie wyklucza wynik. Można sprawdzać pozostałych kandydatów. | ACC-01 |
| INT-03 | Legalne `is_lactose_free=NULL` nie jest błędem integralności. Przy `lactose_free` koncept z NULL wyklucza przepis, a SKU z NULL jest pomijane według dotychczasowych reguł; bez tego ograniczenia sam NULL nie wyklucza wyniku. Nie uzupełniać statusu. | DEC-01; ACC-01/02/08 |
| INT-04 | Nie da się ominąć kontroli braku polityki przez bezpośrednie przygotowanie przepisu poza rankingiem. Walidator raportuje brak polityki składnika używanego w przepisach jako ERROR. Polityka nieużywanego konceptu nie jest wymagana przez to wymaganie. | ACC-01/08 |
| ERR-01 | Rozpoznana niespójność danych podczas kwalifikacji lub przygotowania dowolnego rozpatrywanego kandydata przerywa całe zapytanie. Nie zwracać wcześniejszych poprawnych wyników, nie pomijać awarii i nie zastępować jej pustą listą. | DEC-03; ACC-07 |
| ERR-02 | Granica aplikacji zamienia rozpoznany błąd danych na stały polski komunikat bez przepisów, produktów i szczegółów wyjątku: „Nie udało się przygotować przepisów z powodu niespójnych danych. Spróbuj ponownie później.” Nie ponawia wyszukiwania ani nie prosi LLM o zastępczą odpowiedź. | ACC-05/07 |
| ERR-03 | Nieoczekiwany błąd programistyczny przerywa obliczenia i propaguje do kodu wywołującego oraz testu. Nie przechwytywać wszystkich Exception ani nie klasyfikować każdego ValueError/KeyError jako błędu danych bez rozpoznanej przyczyny. | DEC-03; ACC-07 |
| ERR-04 | Jeśli wszyscy poprawnie przetworzeni kandydaci odpadają przez warunki lub nie ma kandydatów, backend zwraca zwykły pusty wynik. Aplikacja używa istniejącego komunikatu braku wyników; nie jest to błąd danych. | ACC-05 |
| ERR-05 | Diagnostyka rozpoznanego błędu zawiera rodzaj problemu, ID przepisu i ID konceptu/SKU, jeśli dotyczy. Nie zapisuje sekretów, konfiguracji połączenia ani pełnej wypowiedzi użytkownika. Nie ujawnia tych szczegółów w odpowiedzi. | ACC-07 |

Kontrola polityk wszystkich składników kandydata poprzedza krótkie
zakończenie filtra z powodu niezgodności. Jeżeli jeden składnik jest jawnie
niezgodny, a drugi nie ma polityki, wynikiem jest błąd integralności,
nie zwykłe pominięcie przepisu. Kandydat poza kategorią lub limitem czasu
nie jest przygotowywany; jego brak polityki wykrywa walidacja katalogu.

**Rozpoznane błędy danych w T006:** brak polityki kandydata, brak danych
odżywczych używanego konceptu, reguła wskazująca nieistniejący lub błędnie
przypisany SKU, brak/niefinitywna/ujemna wartość wymaganego makro,
niedodatnia lub niefinitywna gramatura bądź liczba porcji.
Nieprawidłowa postać tych wartości także jest błędem danych. Wartość 0
kcal lub makro jest legalna. Normalny brak pasującej reguły SKU nie jest
błędem: nadal można użyć zgodnego konceptu generycznego.

W T006 nie rozszerzamy walidacji runtime na wszystkie możliwe wady katalogu.
Nie zmieniamy istniejącej obsługi błędów API, argumentów narzędzia ani
payloadu renderera. Nieoczekiwany błąd programistyczny nie jest kontrolowanym
komunikatem użytkowym w tym zadaniu; nie wolno jednak zwrócić po nim
pozornego sukcesu. Niedopasowanie do filtrów ma być zwykłym wynikiem
kwalifikacji, a nie wyjątkiem ukrywanym przez szerokie przechwycenie.

#### Scenariusze weryfikacji do implementacji w T006

Wszystkie scenariusze używają kontrolowanych katalogów. W testach granicy
aplikacji odpowiedź LLM jest podstawiona; nie wymaga to API ani zmian bazy.

| ID | Dane / zdarzenie | Oczekiwany wynik | Wymagania |
| --- | --- | --- | --- |
| SC-01 | Kompletne polityki, poprawne dane, pasujący przepis. | Dotychczasowa rekomendacja i obliczenia bez zmiany faktów. | INT-01/02 |
| SC-02 | Poprawny kandydat jawnie niezgodny z dietą; drugi zgodny. | Pierwszy odrzucony, drugi zwrócony; brak komunikatu błędu. | INT-02 |
| SC-03 | Brak polityki jednego składnika kandydata, kolejno dla vegan, vegetarian, pescetarian, meat, fish i bez preferencji. | Każda próba kończy się błędem danych, bez rekomendacji. | INT-01; ERR-01/02 |
| SC-04 | Brak polityki przy bezpośrednim przygotowaniu oraz w katalogu przekazanym walidatorowi. | Przygotowanie zgłasza błąd danych; walidator zgłasza ERROR z ID konceptu. | INT-04 |
| SC-05 | Jawnie niezgodny składnik i inny bez polityki; obie kolejności składników. | Błąd danych w obu wariantach, niezależnie od kolejności. | INT-01; ERR-01 |
| SC-06 | Koncept/SKU ma legalne NULL laktozy, próby z aktywnym ograniczeniem i bez niego. | Dotychczasowe wykluczenie/fallback tylko przy ograniczeniu, bez awarii integralności. | INT-03 |
| SC-07 | Poprawny przepis i kandydat z brakiem danych makro; obie kolejności kandydatów. | Całe zapytanie przerwane, brak częściowego wyniku, stały komunikat i diagnostyka. | ERR-01/02/05 |
| SC-08 | Niedodatnia porcja/gramatura, niepoprawne makro lub błędna referencja SKU. | Rozpoznany błąd danych; brak dalszego wyniku. Dla legalnego zera makro poprawne przygotowanie. | ERR-01/02 |
| SC-09 | W przygotowaniu kandydata występuje podstawiony RuntimeError niezwiązany z rozpoznaną wadą danych. | Wyjątek propaguje; ani backend, ani chat nie zamienia go na wynik lub ogólny komunikat danych. | ERR-03 |
| SC-10 | Wszystkie kompletne przepisy jawnie niezgodne albo brak kategorii/czasu pasujących do zapytania. | Pusta lista i dotychczasowy komunikat braku wyników, bez błędu danych. | ERR-04 |
| SC-11 | Przepis bez polityki poza kategorią lub limitem czasu; poprawny kandydat pasujący do zapytania. | Zapytanie zwraca poprawny wynik bez przygotowania wadliwego przepisu; walidator osobno wykrywa brak polityki. | INT-01/04 |
| SC-12 | Rozpoznany błąd danych przechodzi przez main.chat_with_bot. | Stały komunikat ERR-02, brak renderowania częściowych wyników i dodatkowych wywołań LLM; log spełnia ERR-05. | ERR-01/02/05 |

Oczekiwane wyniki przypadków to wymagania; nie należy zmieniać ich tylko
dlatego, że obecny kod zachowuje się inaczej. Status pokrycia i dowody są
w [verification.md](verification.md). Zatwierdzone progi pozostają bez zmian.

### Wymagania routingu i eksperyment T008

Opracowano 2026-11-03. To specyfikacja przyszłego porównania T009,
bez zmiany aktywnego promptu i bez uruchomienia API. Wymagania wynikają
z istniejącej roli modelu; nie dodają nowych interpretowanych preferencji.

#### Problem i hipoteza

W [diagnozie z 2026-10-15](../../docs/reports/no_tool_diagnosis_2026-10-15.md)
model dla wybranych znanych niepowodzeń zwracał poprawny JSON jako zwykły
tekst zamiast tool calla. To potwierdzony objaw w celowanej próbce.
Hipoteza: format przykładów i niejednoznaczność kanału odpowiedzi sprzyjają
takiej pomyłce. Dotychczasowy eksperyment nie izolował przyczyny.

Celem T009 jest sprawdzenie, czy jawna instrukcja kanału i zmiana formy
tych samych przykładów poprawią routing bez pogorszenia semantyki i granic
obsługi. Nowy baseline należy zmierzyć w tej samej kampanii; nie zastępuje
go historyczne 61,8% ani wyniki testów z mockami.

| ID | Oczekiwane zachowanie | Weryfikacja |
| --- | --- | --- |
| ROU-01 | Obsługiwana prośba wymaga dokładnie jednego tool calla `get_recommendations`, z poprawnymi argumentami zgodnymi z oczekiwaniem przypadku. Liczba propozycji jest parametrem `top_n`. | ACC-06/09; przypadki tool, count, protokół, walidacja i exact match pól. |
| ROU-02 | JSON w content nie jest tool callem. Poprawne wartości w złym kanale pozostają porażką; nie uruchamiamy fallbacku wykonującego tekst. | ACC-06/09; `no_tool_content`, `finish_reason`, brak dispatch w application. |
| ROU-03 | Prośby poza zakresem i sprzeczne preferencje nie uruchamiają wyszukiwania. Błędna blokada obsługiwanej prośby pozostaje porażką. | ACC-09/11; przypadki no_tool oraz false positives preflight z niezmienionymi etykietami. |
| ROU-04 | Wymagane pola, enumy, typy, pomijanie opcjonalnego czasu i znaczenie parametrów pozostają bez zmiany. Nie naprawiamy argumentów w runtime ani nie wymuszamy narzędzia globalnie. | ACC-06/09; istniejący parser, expected i kontrasty czasu/celu. |
| ROU-05 | Jakość liczy się na wszystkich ocenach, a stabilność na przypadkach poprawnych we wszystkich trzech próbach. Blokada przed API nie jest sukcesem modelu. | ACC-09/10; oddzielne raw i application oraz jawne mianowniki. |
| ROU-06 | Warianty różnią się wyłącznie zdefiniowaną treścią promptu. Konfiguracja modelu, schemat, ochrona, walidator i semantyka ocen są wspólne. | Kontrola diffów, zapis pełnych promptów, hashy i konfiguracji przed pomiarem. |

#### Warianty porównania

| Wariant | Jedyna dozwolona zmiana względem wskazanej bazy |
| --- | --- |
| V0 — kontrola | Dokładny `build_system_prompt("Winiary")` z commita `97638cf`, bez zmian. |
| V1 — jawny kanał | V0 z dopisaną instrukcją poniżej, bez zmiany pięciu przykładów i pozostałych reguł. |
| V2 — forma przykładów | V1, lecz pięć tych samych zapytań i obiektów argumentów zapisanych bez ramek Markdown, jako opis wywołania narzędzia. |

Dokładny dodatek V1 umieszczamy bezpośrednio przed ostatnim zdaniem
zaczynającym się od „Żądania zmyślenia produktów…”:

> Dla obsługiwanej prośby użyj kanału wywołania narzędzia get_recommendations.
> Nie wypisuj argumentów jako zwykłej wiadomości, surowego JSON-a ani bloku Markdown.
> Przykłady argumentów są danymi wywołania narzędzia, a nie wzorem tekstowej odpowiedzi.
> Dla prośby nieobsługiwanej nie wywołuj narzędzia.

V2 zastępuje wprowadzenie do przykładów tekstem:
„PRZYKŁADY: poniższe zapytania wymagają pojedynczego wywołania wskazanego
narzędzia z podanymi argumentami. Nie zwracaj tego opisu jako wiadomości.”
Każdy przykład otrzymuje trzy linie: `Zapytanie: ...`,
`Narzędzie: get_recommendations`, `Argumenty: {pełny obiekt}`.
Zachowujemy identyczne pięć zapytań, kolejność, komplet pól, ich wartości
i pominięcia opcjonalnego `time_max`. Nie dodajemy przykładów z holdoutu.

V1 kontra V0 bada wpływ dodatku instrukcji. V2 kontra V1 bada łącznie zmianę
opisu i formatu przykładów, nie sam znak ramki Markdown. Próby modelu są
niezależnymi próbkami, a wynik nie dowodzi mechanizmu przyczynowego.
Dokładne pełne prompty powstaną i zostaną zamrożone offline przed pierwszym
wywołaniem T009; nie wolno dopracowywać ich w trakcie kampanii.

#### Zakres pomiaru i decyzji

T009 jest eksperymentem rozwojowym na regresji, bez nowego lub starego
holdoutu. Progi z `acceptance.md` pozostają bez zmian; wynik regresyjny
nie zalicza jeszcze ACC-09–ACC-11 na niezależnych danych. Wyboru wariantu
nie dokonujemy na podstawie zawartości no_tool ani samej poprawności JSON-a.
Pełny protokół, metryki i reguła wyboru są w [plan.md](plan.md#5-protokół-eksperymentu-routingu-t009).

#### Scenariusze kontroli routingu i instrumentacji

| ID | Przypadek | Oczekiwany wynik |
| --- | --- | --- |
| RSC-01 | Obsługiwana prośba, w tym dwie propozycje. | Jeden poprawny tool call z właściwym top_n i pełnymi argumentami; jeden dispatch. |
| RSC-02 | Poprawne argumenty zwrócone jako tekst lub blok JSON. | Brak dispatch, porażka zapytania tool i zachowany materiał diagnostyczny. |
| RSC-03 | routing_001/004 — alergie; routing_002/003 i guard_001–004 — wykluczenia. | No_tool bez wyszukiwania; 8 przypadków ACC-11 ocenianych we wszystkich trzech próbach. |
| RSC-04 | routing_006 — sprzeczne preferencje; routing_005 — pytanie niezwiązane. | Oba no_tool. Pierwszy należy do ACC-11, drugi do ogólnej poprawności decyzji. |
| RSC-05 | guard_005/006, semantycznie obsługiwane prośby zatrzymywane przez ochronę. | Pozostają oczekiwania tool. Aktualna blokada to błąd application, a nie sukces no_tool. |
| RSC-06 | Nieznane/wielokrotne narzędzie, niepoprawne argumenty lub awaria API. | Właściwy etap błędu, brak sukcesu i brak backendu; błąd API wyklucza akceptację kampanii. |
| RSC-07 | V0/V1/V2 i ich przykłady, kontrolowane odpowiedzi w obu trybach. | Wspólny wariant w raw/application; identyczna semantyka pięciu przykładów; brak wycieku zmiany do domyślnego promptu. |
| RSC-08 | Trzy rundy, dry-run, przerwany raport i agregacja. | Bez API w dry-run, właściwe liczniki, brak duplikowania ocen/checkpointów; brakująca ocena nie jest sukcesem. |

RSC-01/02/06–08 wymagają testów instrumentacji z mockami w T009.
RSC-03–05 są zarazem stałymi grupami do raportu żywej kampanii. Ich expected
nie zmienia się na potrzeby promptu. Poprawa RSC-05 wymagałaby odrębnej
zmiany ochrony, dlatego nie przypisujemy jej możliwej poprawie modelu.

### Mały pilotaż diagnostyczny zamiast dużej kampanii

**Stan: zakończony.** Poniższy opis jest zamrożonym protokołem, a nie
poleceniem ponownego wykonania. Wyniki i decyzja:
[raport T009P](../../docs/reports/routing_pilot_2026-11-03.md).

Pilotaż jest osobną procedurą, nie wybiórczym wykonaniem ani wznowieniem
kampanii `_01`. Porównuje V0 z V2 na dokładnie 20 przypadkach zapisanych
w `evals/routing_pilot_cases.json`, bez zmiany ich expected:

- Znane błędy kanału: intent_003/004/010/013/031/051.
- Kontrole z wcześniejszej diagnozy: intent_015/025.
- Kontrasty: intent_001/007/008/032/059/063.
- Granice obsługi: routing_001–006 (dwie alergie, dwa wykluczenia,
  pytanie niezwiązane i sprzeczne preferencje).

To celowo dobrany zestaw rozwojowy znanych problemów i kontroli, nie losowa
próbka ani niezależny holdout. Wynik nie szacuje skuteczności dla wszystkich
użytkowników. Surowe próby mierzą interpretację i decyzję modelu; nie oceniają
preflight, bazy, doboru SKU ani czytelności odpowiedzi.

Oba warianty: gpt-4o-mini, temperatura 0.1, auto, parallel_tool_calls=false,
max_completion_tokens=512, brak retry SDK, timeout 30 s. Limit odpowiedzi
i retry różnią się od starego protokołu, dlatego wyników nie należy mieszać.
Trzy rundy, kolejność wariantów V0/V2, V2/V0, V0/V2; łącznie 120 wywołań.
Ucięcie odpowiedzi przez limit jest porażką i ma być raportowane oddzielnie.

Budżet ochronny pilotażu: 0,50 USD według konserwatywnego szacowania wejścia
(bajty UTF-8 + narzut) i maksymalnie 512 tokenów wyjścia na wywołanie.
Runner rezerwuje koszt przed wysłaniem żądania i nie uruchamia go, jeżeli
przekroczyłby budżet. To lokalna kontrola szacunku, nie gwarancja rachunku
dostawcy; nie obejmuje podatków ani innych równoległych wydatków na koncie.
Przed wykonaniem zapisujemy pełny manifest i kwotę planowanych rezerw.

Reguła wyboru: tylko kompletna kampania bez API errors i z jedną wersją
resolved model może wskazać kandydata. Wariant musi poprawnie obsłużyć
wszystkie 18 prób no_tool. Spośród dopuszczonych wygrywa więcej poprawnych
ocen z 60, następnie więcej stabilnych przypadków z 20; remis zachowuje V0.
Jeśli żaden wariant nie spełnia warunku granic, nie wybieramy kandydata.
Wynik to rekomendacja do dalszej regresji; nie deklarujemy naprawy całego
routingu ani automatycznie nie wdrażamy V2. Nie zmieniamy progów ACC.

W przyszłej pełnej ocenie rozdzielamy routing, deterministyczną poprawność
logiki i danych oraz czytelność i zgodność odpowiedzi. Pełny przepływ na
rzeczywistym katalogu dopełnia te oceny, zamiast zastępować je jednym procentem.

### Iteracja T014 — poprawa kanału bez utraty granic obsługi

T014 jest nowym zadaniem wynikającym z zakończonego T009P, nie wznowieniem
pełnej kampanii T009 i nie zmianą jej historycznej oceny. Celem jest
przygotowanie V3 na podstawie V2: zachować poprawę wywoływania narzędzia,
usuwając ujawnione pomijanie nieobsługiwanych wymagań.

| ID | Wymaganie | Powiązanie i weryfikacja |
| --- | --- | --- |
| ROU-07 | Nieobsługiwana prośba dotycząca alergii lub wykluczenia oraz sprzeczne preferencje mają pierwszeństwo przed instrukcją użycia narzędzia dla prośby o posiłek. Model nie może pomijać takiego wymagania ani zastępować go dietą lub innym filtrem. | ACC-09/11; raw: wszystkie próby no_tool, w szczególności routing_004, bez zmiany expected. |
| ROU-08 | V3 zachowuje znaczenie parametrów i pełne przykłady z V2. Modyfikacja dotyczy doprecyzowania pierwszeństwa granic obsługi; bez zmiany schematu, parsera, preflight i wykonywania JSON-a z content. | ROU-01–06; przegląd diffu V2/V3 i testy offline, potem poprawność kanału i wszystkich argumentów. |
| ROU-09 | Sam sukces preflight w application nie dowodzi poprawnej odmowy modelu. Błąd modelu widoczny w raw pozostaje błędem diagnostycznym, nawet gdy aplikacja go blokuje. | Oddzielne raw i application, liczby wywołań modelu i backendu, poprawne i fałszywe blokady. |
| ROU-10 | Nowy prompt nie jest wdrażany automatycznie po wzroście procentu. Wymagane są pozytywny wynik uzgodnionego porównania, przegląd regresji, osobna decyzja o wdrożeniu i aktualizacja dowodów. | Protokół T014 w planie, stan w tasks, raport z decyzją. Brak wyniku lub porażka pozostawia V0. |

Warunki ukończenia T014: wariant V3 zamrożony po przeglądzie offline,
porównanie według wcześniej ustalonej reguły, wyniki raw i application,
przegląd regresji oraz jawna decyzja „wdrożyć / pozostawić V0 / potrzebna
kolejna hipoteza”. Ukończenie zadania nie wymaga pozytywnej hipotezy,
ale wymaga dowodów i decyzji. Nie jest końcową akceptacją MVP.

T014.1 obejmuje tę specyfikację; T014.2 przygotowanie V3 i instrumentacji
offline; T014.3 osobno zatwierdzony pomiar; T014.4 ocenę i ewentualne wdrożenie.
Zgoda na poprzednie 120 wywołań V0/V2 została wykorzystana i nie jest zgodą
na następne wywołania. T009 i analiza pięciu SKU pozostają wstrzymane.

T014 zakończono przeglądem T014.4: **pozostawić V0; potrzebna kolejna
hipoteza** (DEC-07). V3 spełnił regułę kandydata, lecz nie został wdrożony.
Przegląd odróżnia brak nowej stałej regresji 3/3 → 0/3 od braku dowolnej
regresji: `intent_032` pogorszył się do 2/3, a w `intent_004` błędne
argumenty V3 przeszły walidację i trafiły do atrapy backendu.
Wynik tego zadania jest decyzją o konfiguracji, nie zaliczeniem jakości MVP.

Następna praca T015 została wykonana offline: najpierw zapisano hipotezę,
regułę porównania i scenariusze, następnie przygotowano V4 i instrumentację.
Nie pomijać diety ze względu na kategorię deseru; nie odmawiać obsługiwanej
preferencji ryby ani `top_n=4`. To obecna semantyka, nie nowe funkcje.
Zachowano rozdzielenie raw/application, granice no_tool i brak wykonywania
tekstu JSON. Żaden kolejny pomiar nie startuje automatycznie.

### T015 — zachowanie jawnych preferencji w wariancie V4

Hipoteza H-T015: doprecyzowanie w V3 niezależności preferencji od kategorii
oraz zakresu parametrów zmniejszy pomijanie diety i błędne odmowy, zachowując
poprawę kanału oraz pierwszeństwo nieobsługiwanych wymagań. Hipoteza dotyczy
całego dodatkowego akapitu; nie rozdziela przyczynowego wpływu każdej reguły.

V4 zachowuje cały V3 i dodaje jeden akapit przed `PARAMETRY`, bez nowych
przykładów i bez dosłownego kopiowania trzech zapytań pomiarowych.
Akapit ma przypomnieć przenoszenie jawnej diety niezależnie od kategorii,
obsługę preferencji ryby i dodatniej liczby propozycji, bez wymyślania limitów.
Nie zmienia znaczenia istniejących słowników; blokada nieobsługiwanego
wymagania nadal ma pierwszeństwo. Nie wymaga wyjaśnienia toku rozumowania.

| Scenariusz | Wymaganie już obowiązujące | Oczekiwanie i kontrola |
| --- | --- | --- |
| RSC-09 — dieta a kategoria | ROU-01/04/08; ACC-01/09 | `intent_004`: vegetarian także dla deseru. Nie zastępować jawnej diety przypuszczeniem o składzie kategorii; zachować kontrasty intent_059 i pozostałe diety. |
| RSC-10 — obsługiwana ryba | ROU-01/03/04; ACC-09 | `intent_010`: jedno narzędzie, fish, kolacja, time_max=20. Nie odmawiać z powodu ryby; zachować no_tool dla alergii i sprzeczności. |
| RSC-11 — liczba propozycji | ROU-01/04; ACC-09 | `intent_032`: pescetarian, protein_preference=none, top_n=4. Nie wymyślać limitu trzech; nie zamieniać liczby propozycji w liczbę wywołań. |
| RSC-12 — regresja i pominięte wymagania | ROU-05/09/10 | Raportować każde zmniejszenie liczby sukcesów per-case, także 3/3 → 2/3, oraz każde przekazanie do backendu argumentów niezgodnych z expected. |

T015 zakończyło specyfikację, V4, instrumentację, testy offline i manifest.
Samo przygotowanie nie dowodzi skuteczności H-T015 i nie wdraża V4.
T016 porównał V0/V4 na tych samych 20 ujawnionych przypadkach według
reguły ustalonej w sekcji 8 planu. V3 pozostaje źródłem hipotezy, a jego
historyczny wynik nie był równoczesną kontrolą tego pomiaru.

T016 zakończono pełnym pomiarem, audytem i przeglądem (DEC-08).
V4: raw 58/60, application 57/60, no_tool 18/18 w obu trybach.
`intent_004/010` poprawne 3/3 w obu trybach; `intent_032` raw 1/3,
application 0/3. Liczba propozycji jest poprawna, ale V4 nieuzasadnienie
ustawia fish z samej diety pescetarian. H-T015 uzyskała częściowe wsparcie,
lecz pełny cel nie został osiągnięty. Trzy warunki T015-v1 są niespełnione:
docelowe przypadki 3/3, brak regresji oraz brak dispatch z błędną semantyką.
Aktywny V0 pozostaje; nie zaliczono ACC ani nie wdrożono V4.
Wynik T016 wyznaczył T017: diagnozę kontrastów diet/protein, następną
hipotezę i sposób weryfikacji, bez automatycznego kolejnego pomiaru.
Ukończony kontrakt T017 opisano poniżej.

### T018 — usunięcie konfliktu INS-01 w opisie narzędzia

Na polecenie autorki z 2026-11-16 poprawka obejmuje wspólny opis funkcji
`get_recommendations`. Jest odrębna od dalszej diagnozy diet/protein T017.

**ROU-11:** opis funkcji wymaga dokładnie jednego wywołania dla prośby
o przepisy lub pomysł na posiłek, jeżeli wszystkie wymagania są obsługiwane.
Nie nakazuje wywołania dla próśb poza zakresem, doboru dla alergii,
nieobsługiwanych wykluczeń ani sprzecznych preferencji. Nieobsługiwane
wymaganie ma pierwszeństwo przed prośbą o posiłek; nie wolno go pominąć
ani zastąpić dostępnym filtrem. Powiązanie: ROU-01/03/07 i ACC-06/11.

Zakres zmiany: tekst opisu funkcji, bez zmiany pól, typów, wartości,
wymagalności, parsera, preflight i promptów V0–V4. Ukończenie wymaga
kontroli różnicy schematu i istniejących testów offline. Nie stanowi
pomiaru poprawy interpretacji ani zgody na nową kampanię API.

### Ustalenia po audycie — zakres T017, T019 i T020

Poniższa tabela została zaakceptowana przez autorkę jako semantyka prośby
(DEC-09). Jest podstawą kontraktu i scenariuszy weryfikacji; jej umieszczenie
tutaj nie oznacza dodania tych tekstów do przykładów wysyłanych modelowi.

| Prośba | diet | protein_preference |
| --- | --- | --- |
| Kolacja bez mięsa | vegetarian | none |
| Bez mięsa, ale ryby mogą być | pescetarian | none |
| Bez mięsa, ale chcę danie z rybą | pescetarian | fish |
| Wegańska kolacja bez mięsa | vegan | none |

### T017 — kontrakt interpretacji diety i źródła białka

Opracowano 2026-11-16 na podstawie DEC-09, audytu INS-02/05 i przeglądu
T016. To specyfikacja oczekiwanego zachowania, jeszcze niewdrożona do
instrukcji modelu. Nie zmienia interpretacji samego „bez mięsa” na
domyślne dopuszczenie ryb.

**Diagnoza:** w T016 `intent_032` miał poprawne jedno wywołanie i top_n=4
we wszystkich sześciu próbach V4. Błąd dotyczył wyłącznie dodanego fish:
2/3 prób raw i 3/3 application. W instrukcjach nie znaleziono nakazu
wyprowadzania fish z pescetarian; przeciwnie, opis pola i prompt tego
zabraniają. Brak kontrastowych przykładów jest hipotezą wyjaśniającą,
nie ustaloną przyczyną. Osobna niejednoznaczność INS-02 dotyczy pierwszeństwa
„bez mięsa” i jego doprecyzowań; nie wyjaśnia bezpośrednio `intent_032`,
który nie zawiera tej frazy. Szczegóły dowodów i ograniczeń: sekcja 9 planu.

| ID | Reguła interpretacji | Powiązanie |
| --- | --- | --- |
| ROU-12 | Odczytać całą prośbę przed wyborem diety. Samo „bez mięsa” daje vegetarian. „Bez mięsa, ryby mogą być” daje pescetarian/none, a „bez mięsa, chcę rybę” pescetarian/fish. To doprecyzowanie ogólnej frazy, nie automatyczna zmiana jawnie nazwanej diety vegetarian lub vegan. | DEC-09; INS-02; ACC-09/11 |
| ROU-13 | Jawna dieta vegan/vegetarian/pescetarian obowiązuje niezależnie od kategorii i celu. Zgodne dopowiedzenia jej nie osłabiają; „wegańska bez mięsa” pozostaje vegan. Samo dopuszczenie ryby nie usuwa wymogów jawnej diety. Jawne żądanie składnika wykluczonego przez tę dietę jest sprzecznością, bez wywołania narzędzia; nie wolno usuwać części prośby. | ROU-01/07; ACC-09/11 |
| ROU-14 | diet określa dopuszczalność składników, a protein_preference wymaga obecności wskazanego źródła. fish/meat ustawić tylko na podstawie dodatniej prośby o danie z rybą/mięsem. Samo „może być”, pescetarian i high_protein nie ustanawiają takiego wymagania. none oznacza brak jawnego wymagania, a nie wykluczenie ryb, mięsa lub białka. Sama prośba o rybę nie dodaje pescetarian. | INS-05; ROU-01/04; ACC-09 |
| ROU-15 | Rozróżnić cofnięcie wymagania od zakazu: „nie musi być z rybą” nie wymaga fish, „nie musi być bez mięsa” nie ustanawia vegetarian. Negacja nie usuwa innej, dodatnio wskazanej diety. „Bez ryb” jest rzeczywistym wykluczeniem i nie może zostać zakodowane jako none. Bez zgodnej reprezentacji całej prośby obowiązuje no_tool. „Bez mięsa i ryb” ma reprezentację vegetarian/none. | ROU-07; ACC-09/11 |
| ROU-16 | Po interpretacji sprawdzić zgodność pary diet/protein według macierzy poniżej. Nie rozwiązywać konfliktu przez domyślne none, usunięcie diety lub zamianę żądanej ryby na zamiennik. Brak wywołania nie jest pustym wynikiem wyszukiwania; komunikat i źródło przyczyny określi T019. | ROU-03/07; ACC-09/11 |
| ROU-17 | Pozostałe wymagania zachować bez zmian: ograniczenia, cel, kategorię, czas i top_n. Jawny dodatni top_n powyżej 3 jest obsługiwany. Nie zmieniać expected ani nie naprawiać semantyki przez bezwarunkową zamianę pescetarian/fish na pescetarian/none. | ROU-01/04; RSC-11/12; ACC-09 |

Kolejność: odczytać dodatnie wymagania, dopuszczenia i negacje w kontekście
całego zdania → ustalić dietę według ROU-12/13 → niezależnie ustalić jawne
źródło według ROU-14/15 → sprawdzić zgodność pary i całej prośby → dopiero
wtedy jedno wywołanie z pełnymi argumentami albo brak wywołania.
Nieobsługiwana alergia lub wykluczenie nadal ma pierwszeństwo (ROU-07/11).
Sprzeczności nie rozstrzyga ostatnie słowo ani kolejność fraz. Kontrakt
nie wprowadza obsługi alternatyw wielu diet lub źródeł w jednym polu.

Macierz dotyczy zgodności już wybranych wartości, a nie poprawności ich
przypisania do konkretnego zdania. Jest zgodna z istniejącym walidatorem:

| diet | protein=none | protein=fish | protein=meat |
| --- | --- | --- | --- |
| none | dozwolone | dozwolone | dozwolone |
| vegetarian | dozwolone | sprzeczne | sprzeczne |
| vegan | dozwolone | sprzeczne | sprzeczne |
| pescetarian | dozwolone | dozwolone | sprzeczne |

W szczególności legalne pescetarian/fish nie dowodzi, że użytkownik prosił
o rybę. Parser sprawdza strukturę i zgodność wartości, a ocena semantyczna
porównuje je z wymaganiami zapytania. Obecna aplikacja nie ma dodatkowego
mechanizmu sprawdzającego to znaczenie przed dispatch.

#### Scenariusze diet/protein do przyszłej weryfikacji

Poniższe DP-01–28 są jawnymi przypadkami rozwojowymi, nie wynikami modelu
ani końcowym holdoutem. Nie kopiować ich do demonstracji V5. Dla `tool`
obowiązują pełne argumenty bazowe: restrictions=[], nutrition_goal=standard,
category=kolacja, top_n=3; time_max pominięte. Wiersz podaje diet,
protein_preference oraz wszystkie odstępstwa od tej bazy. Znak „—” dla
no_tool oznacza brak argumentów i brak dispatch, nie wartości domyślne.

| ID | Zapytanie rozwojowe | Decyzja | diet | protein_preference | Odstępstwa od bazy / kontrola |
| --- | --- | --- | --- | --- | --- |
| DP-01 | Kolacja bez mięsa | tool | vegetarian | none | Reguła domyślna. |
| DP-02 | Kolacja bez mięsa, ryby mogą być | tool | pescetarian | none | Dopuszczenie nie jest żądaniem. |
| DP-03 | Kolacja bez mięsa, chcę danie z rybą | tool | pescetarian | fish | Jawne żądanie z doprecyzowaniem diety. |
| DP-04 | Wegańska kolacja bez mięsa | tool | vegan | none | Jawna dieta przed ogólną frazą. |
| DP-05 | Kolacja pescetariańska | tool | pescetarian | none | Samo pescetarian nie wymaga fish. |
| DP-06 | Kolacja pescetariańska z rybą | tool | pescetarian | fish | Nie usuwać poprawnej preferencji fish. |
| DP-07 | Kolacja z rybą | tool | none | fish | Sama ryba nie ustala diety. |
| DP-08 | Kolacja, ryby mogą być | tool | none | none | Samo dopuszczenie nie ustala żadnego z pól. |
| DP-09 | Kolacja z mięsem | tool | none | meat | Dodatnie wymaganie mięsa. |
| DP-10 | Kolacja, mięso może być | tool | none | none | Dopuszczenie mięsa nie wymaga meat. |
| DP-11 | Wysokobiałkowa kolacja pescetariańska | tool | pescetarian | none | nutrition_goal=high_protein. |
| DP-12 | Kolacja nie musi być z rybą | tool | none | none | Cofnięte wymaganie, bez zakazu ryby. |
| DP-13 | Kolacja nie musi być bez mięsa | tool | none | none | Zanegowane wykluczenie nie dodaje diety. |
| DP-14 | Kolacja bez mięsa i ryb | tool | vegetarian | none | Wykluczenie obu grup ma reprezentację. |
| DP-15 | Kolacja wegetariańska z prawdziwą rybą, nie zamiennikiem | no_tool | — | — | Sprzeczna para vegetarian/fish. |
| DP-16 | Wegańska kolacja z mięsem, nie zamiennikiem | no_tool | — | — | Sprzeczna para vegan/meat. |
| DP-17 | Kolacja pescetariańska z mięsem, nie zamiennikiem | no_tool | — | — | Sprzeczna para pescetarian/meat. |
| DP-18 | Kolacja bez ryb | no_tool | — | — | Sam zakaz ryb nie ma wiernej reprezentacji; nie rozszerzać go na vegetarian. |
| DP-19 | Kolacja bez mięsa, ale koniecznie z mięsem, nie zamiennikiem | no_tool | — | — | Sprzeczność w jednej prośbie. |
| DP-20 | Daj 4 kolacje pescetariańskie bez glutenu do 25 minut | tool | pescetarian | none | restrictions=[gluten_free], time_max=25, top_n=4. |
| DP-21 | Daj 4 kolacje pescetariańskie z rybą bez glutenu do 25 minut | tool | pescetarian | fish | restrictions=[gluten_free], time_max=25, top_n=4. |
| DP-22 | Kolacja bez mięsa, nie musi być z rybą | tool | vegetarian | none | Cofnięcie żądania ryby nie jest dopuszczeniem ryb wobec „bez mięsa”. |
| DP-23 | Kolacja nie musi być pescetariańska | tool | none | none | Zanegowana dieta nie dodaje pescetarian. |
| DP-24 | Kolacja bez mięsa i bez mleka | no_tool | — | — | Nieobsługiwane wymaganie ma pierwszeństwo. |
| DP-25 | Kolacja wegańska | tool | vegan | none | Kontrola jawnej diety. |
| DP-26 | Kolacja wegetariańska | tool | vegetarian | none | Kontrola jawnej diety. |
| DP-27 | Wysokobiałkowa kolacja | tool | none | none | nutrition_goal=high_protein; bez wymyślonego źródła. |
| DP-28 | Kolacja pescetariańska nie musi być z rybą | tool | pescetarian | none | Negacja źródła nie usuwa dodatniej diety. |

Kontrola offline T017 wykazała fałszywe blokady preflight dla DP-02/03/22:
ogon zdania po przecinku jest traktowany jako dalszy ciąg wykluczeń.
Expected pozostaje tool. To dalszy przejaw INS-06; instrukcja modelu nie
naprawi prośby zatrzymanej przed API. Nie przypisywać tym próbom błędu
rozumienia modelu, ale nadal liczyć je jako błędy całej aplikacji.
T024 usunęło te trzy blokady gramatyki. Historyczny wynik T017/T023
pozostaje bez zmiany; skuteczność modelu po odblokowaniu nie była mierzona.

**H-T017:** kontrastowe demonstracje dopuszczenia i żądania ryby, wraz
z minimalnym usunięciem bezwarunkowego brzmienia INS-02, zmniejszą liczbę
niezamówionych fish bez utraty poprawnych jawnych fish, diet, kanału
i granic odmowy. To hipoteza o całym nowym wariancie, nie dowód przyczyny
błędu T016 ani obietnica poprawy. Przygotowanie V5 prowadzi T021 po T019;
protokół i warunki oceny przed pomiarem określa sekcja 9 planu.

### T019 — kontrakt odpowiedzi no_tool

Opracowano 2026-11-17 na podstawie DEC-10 / INS-03 i ROU-12–17.
T022 wdrożyło komunikat i kontrolę protokołu; poprawność decyzji modelu
pozostaje do zmierzenia. Kontrakt rozdziela brak wywołania
narzędzia przez model, zatrzymanie przed modelem, pusty wynik po wyszukiwaniu
i awarię. W każdym przypadku końcową odpowiedź tworzy aplikacja.

| ID | Wymaganie | Powiązanie |
| --- | --- | --- |
| NTO-01 | Model nie wywołuje narzędzia dla wypowiedzi niezwiązanej z prośbą o przepis, rzeczywiście nieobsługiwanego wymagania, sprzeczności według T017 lub wypowiedzi, z której nie da się ustalić samodzielnej prośby o posiłek. Brak kategorii, diety, celu, liczby lub czasu nie jest sam w sobie brakiem informacji: stosować istniejące wartości domyślne. „Podaj przepis” jest obsługiwane. | ACC-09/11; ROU-01/07/12–17 |
| NTO-02 | No_tool z modelu oznacza brak pozycji w tool_calls w odpowiedzi bez sygnałów błędu technicznego. Nie istnieje narzędzie no_tool ani obiekt argumentów odmowy. Nie dodawać action/reason do schematu. content może być null, pusty lub niepusty; aplikacja go nie wykonuje, nie wyświetla i nie używa jako źródła przyczyny. | ACC-06; ROU-02/03 |
| NTO-03 | Uzasadnienie komunikatu może pochodzić tylko z lokalnie zaobserwowanego etapu: zadziałała reguła preflight, wystąpił błąd API/walidacji lub wyszukiwanie zwróciło pustą listę. Reguła alergii stwierdza wzmiankę, nie diagnozę użytkownika; reguła wykluczeń może oznaczać niejednoznaczny zapis. Sam brak tool_calls nie dowodzi alergii, konfliktu, nieobsługiwanego wymagania ani braku danych w katalogu. | ACC-05/07/11 |
| NTO-04 | Dla zwykłego no_tool modelu aplikacja zwraca jeden stały komunikat MSG-01, niezależny od content/refusal i domniemanego powodu. Komunikaty preflight oraz błędów dobiera z własnej ścieżki wykonania. Nie może twierdzić „nie znaleziono”, jeśli wyszukiwanie nie nastąpiło. Nie wolno przejść do wyszukiwania przez odczytanie JSON-a z content. | ACC-05/06/07 |
| NTO-05 | Poprawne pojedyncze wywołanie dopiero po walidacji uruchamia backend. Pusta lista recommendations oznacza wykonane wyszukiwanie bez wyników; zachować wymagania i użyć MSG-04. Błąd przygotowania/payloadu pozostaje błędem, nawet jeśli wystąpił po uruchomieniu backendu; nie zamieniać go na pustą listę ani no_tool. | ACC-05/06/07; DEC-03 |
| NTO-06 | Błąd API, brak choices, nieznane/wielokrotne narzędzie i niepoprawne argumenty nie są poprawnym no_tool. Jawne ucięcie (finish_reason=length), odfiltrowanie (content_filter) lub niepuste refusal także nie dowodzą decyzji biznesowej modelu. Przed dispatch zatrzymać takie odpowiedzi i zwrócić kontrolowany błąd; nie wykonywać nawet wyglądających poprawnie argumentów z uciętej odpowiedzi. | ACC-06/07; T017-v1 |
| NTO-07 | W ocenie porównywać działanie z expected ustalonym przed pomiarem. Brak narzędzia dla obsługiwanej prośby to błąd decyzji; fałszywa blokada preflight to błąd ochrony. Nie przypisywać brakującym argumentom wymyślonych wartości i nie zaliczać poprawnego JSON-a w content. Dla no_tool bez argumentów ocena pól jest nieadekwatna, a nie poprawna lub błędna. Błąd techniczny nie jest sukcesem odmowy. | ACC-06/09/11; ROU-09 |
| NTO-08 | Doprecyzowanie oznacza możliwość podania nowego, samodzielnego zapytania, bez pamięci poprzedniej wypowiedzi. Model nie prowadzi dialogu i nie musi wygenerować pytania. Nie wymagać literalnej odpowiedzi „no_tool”, kodu przyczyny ani pustego content jako warunku poprawnej decyzji. Brak takiego dodatkowego sygnału jest świadomą granicą MVP. | Z-03/04; INS-03; ACC-09 |

**Podział odpowiedzialności:** model interpretuje prośbę i wybiera jedno
narzędzie z argumentami albo brak wywołania. Aplikacja odpowiada za preflight,
walidację odpowiedzi i argumentów, dispatch oraz komunikat. Ewaluacja zna
etykietę expected i może stwierdzić błędną odmowę; aktywna aplikacja nie ma
takiej etykiety i nie może odtwarzać przyczyny z samej nieobecności wywołania.
Metadane refusal/finish_reason są sygnałem przebiegu odpowiedzi, nie
wiarygodnym uzasadnieniem dietetycznym. Ich treści nie pokazywać użytkownikowi.

#### Decyzja → wykonanie → komunikat

Liczby oznaczają wywołania backendu, nie liczbę przepisów. API nie jest
wywoływane przy blokadzie preflight. Dla pozostałych ścieżek nie dodawać
drugiego wywołania modelu do redakcji ani ustalenia powodu.

| Sytuacja | Oczekiwana decyzja / źródło wiedzy | Backend | Komunikat |
| --- | --- | --- | --- |
| Preflight rozpoznaje wzmiankę o alergii. | Zatrzymanie aplikacji przed modelem; znana jest reguła, nie stan zdrowia. | 0 | MSG-02 |
| Preflight rozpoznaje wykluczenie lub niejednoznaczny zapis. | Zatrzymanie aplikacji przed modelem; poprawność blokady ocenić osobno. | 0 | MSG-03 |
| Model poprawnie nie wywołuje narzędzia dla prośby poza zakresem, sprzeczności lub braku samodzielnej prośby. | No_tool; aplikacja zna brak wywołania, bez pewnego powodu biznesowego. | 0 | MSG-01 |
| Model nie wywołuje narzędzia dla obsługiwanej prośby. | Błędna decyzja w ewaluacji; aplikacja nadal zna tylko brak wywołania. | 0 | MSG-01; wynik testu pozostaje błędem. |
| Poprawne jedno wywołanie i niepusty wynik. | Wyszukiwanie wykonane, payload poprawny. | 1 | Lokalny renderer. |
| Poprawne jedno wywołanie i pusta lista wyników. | Wyszukiwanie wykonane bez zgodnych wyników. | 1 | MSG-04 |
| Wyjątek API. | Błąd usługi interpretacji, bez decyzji modelu. | 0 | MSG-05 |
| Brak choices, nieznane narzędzie, wiele wywołań lub błędne argumenty. | Błąd protokołu albo argumentów. | 0 | MSG-06 |
| Ucięcie, filtrowanie lub refusal, z narzędziem albo bez. | Błąd/odmowa na poziomie odpowiedzi dostawcy; nie utożsamiać z granicą katalogu. | 0 | MSG-06 |
| Błąd przygotowania danych po dispatch. | Błąd danych, nie pusty wynik. | 1 | MSG-07 |
| Niepoprawny payload po dispatch. | Błąd prezentacji danych, nie pusty wynik. | 1 | MSG-08 |

#### Komunikaty aplikacji

MSG to identyfikatory specyfikacji, nie nowe narzędzia lub pola API.
MSG-01 oraz dobór MSG-06 dla błędów metadanych i nieznanej funkcji wdrożono
w T022. Komunikaty preflight zachowują swój tekst.

| ID | Treść lub istniejący szablon |
| --- | --- |
| MSG-01 | „Nie wyszukano przepisów. Możesz ponownie opisać posiłek i swoje wymagania. Obsługiwane są dostępne diety oraz ograniczenia bez glutenu i bez laktozy. Bez laktozy nie oznacza bez mleka ani bez nabiału. Chatbot nie obsługuje doboru przepisów dla alergii.” |
| MSG-02 | Istniejące UNSUPPORTED_ALLERGY_RESPONSE: informacja o wzmiance o alergii, braku wyszukiwania i braku obsługi doboru dla alergii. Nie stwierdza, że użytkownik ma alergię. |
| MSG-03 | Istniejące UNSUPPORTED_EXCLUSION_RESPONSE: wykluczenie nieobsługiwane lub niejednoznaczny zapis, bez wyszukiwania i zastępowania wymagania innym filtrem. |
| MSG-04 | „Nie znaleziono przepisów spełniających podane kryteria.” — wyłącznie po poprawnym wyszukiwaniu. |
| MSG-05 | Istniejące API_ERROR_RESPONSE: „Usługa interpretacji zapytań jest obecnie niedostępna. Spróbuj ponownie później.” |
| MSG-06 | Istniejące INVALID_TOOL_RESPONSE: „Nie udało się odczytać parametrów zapytania. Doprecyzuj wymagania i spróbuj ponownie.” |
| MSG-07 | Istniejący komunikat danych: „Nie udało się przygotować przepisów z powodu niespójnych danych. Spróbuj ponownie później.” |
| MSG-08 | Istniejący komunikat payloadu: „Nie udało się wyświetlić przepisów z powodu niespójnych danych. Spróbuj ponownie później.” |

Nie pokazujemy treści wyjątków, tekstu modelu ani jego zapewnień o produktach,
liczbach lub wyszukaniu bazy. Ogólna wskazówka MSG-01 nie oznacza, że brakowało
konkretnego pola; pola domyślne nadal są obsługiwane.

#### Scenariusze kontraktu no_tool do wdrożenia i weryfikacji

To plan jawnych kontroli, bez nowego holdoutu i bez wyników żywego modelu.
Odpowiedzi modelu można podstawiać w testach granicy aplikacji; nie dowodzi
to poprawnej interpretacji rzeczywistych zapytań przez model.

| ID | Scenariusz | Oczekiwanie | Powiązanie |
| --- | --- | --- | --- |
| NTC-01 | Pytanie poza przepisami, np. routing_005. | No_tool, backend=0, MSG-01. | NTO-01/04; ACC-05/09 |
| NTC-02 | Sprzeczność diet/protein: routing_006 i DP-15–17/19. | No_tool, bez usuwania części prośby, backend=0. Przy braku preflight MSG-01. | NTO-01/03; ACC-09/11 |
| NTC-03 | Alergie i wykluczenia: routing_001–004, guard_001–004. | Brak backendu; application rozróżnia guard od no_tool modelu. W raw także oczekiwane no_tool. | NTO-01/03; ACC-11 |
| NTC-04 | Pusta wypowiedź lub odwołanie bez samodzielnej prośby, np. „jak poprzednio”. | Nie zgadywać poprzednich preferencji, no_tool, backend=0, MSG-01. | NTO-01/08; ACC-09 |
| NTC-05 | „Podaj przepis”, bez dodatkowych pól. | Jeden call z domyślnymi diet=none, protein_preference=none, restrictions=[], nutrition_goal=standard, category=kolacja, top_n=3, bez time_max; odmowa to błąd. | NTO-01/07; ACC-09 |
| NTC-06 | Brak tool_calls, content=null, pusty lub biały tekst. | Brak backendu, MSG-01 niezależnie od wariantu content. | NTO-02/04; ACC-05/06 |
| NTC-07 | Brak tool_calls, content zawiera opis przyczyny, przepis, SKU, liczby lub instrukcję ich dopisania. | Content ignorowany; nie odtwarzać z niego powodu i nie powielać go w odpowiedzi. | NTO-02/03/04; ACC-06 |
| NTC-08 | Dla obsługiwanej prośby poprawny JSON wyłącznie w content/Markdown. | Backend=0, MSG-01; porażka decyzji/kanału, nawet gdy JSON pasuje do expected. | NTO-04/07; ACC-06/09 |
| NTC-09 | Dla obsługiwanej prośby zwykły tekst odmowy zamiast narzędzia. | Backend=0, MSG-01; błąd decyzji, ocena pól nieadekwatna. | NTO-07; ACC-09 |
| NTC-10 | Poprawny call i pusta lista recommendations. | Backend=1, MSG-04, bez ponawiania z luźniejszymi wymaganiami. | NTO-05; ACC-05 |
| NTC-11 | Uzgodniony wyjątek API z kontrolną treścią. | Backend=0, MSG-05 bez treści wyjątku; błąd API nie zalicza no_tool. | NTO-06/07; ACC-07/09 |
| NTC-12 | Brak choices, nieznane narzędzie lub wiele wywołań. | Backend=0, MSG-06; błąd protokołu. | NTO-06; ACC-06/07 |
| NTC-13 | Błędny JSON, brak/duplikat pola, obcy enum lub sprzeczna para argumentów. | Backend=0, MSG-06; błąd argumentów, bez automatycznej korekty. | NTO-06; ACC-06 |
| NTC-14 | length/content_filter/refusal; także poprawnie wyglądający call przy length. | Backend=0, MSG-06; brak sukcesu decyzji biznesowej w obu trybach oceny. | NTO-06/07; ACC-06/07/09 |
| NTC-15 | RecommendationDataError albo ResponsePayloadError po dispatch. | Backend=1, odpowiednio MSG-07/08, bez pozornego braku wyników. | NTO-05; ACC-07 |
| NTC-16 | Fałszywe blokady guard_005/006 i DP-02/03/22. | Zachować expected=tool. Historyczne blokady T022/T023 pozostają porażkami preflight bez próby modelu. Po T024 zapytania przechodzą preflight; poprawność dalszej decyzji zależy od odpowiedzi, nie od samego odblokowania. | NTO-03/07; PFL-01/07; ACC-09/11 |
| NTC-17 | Jednocześnie wzmianka alergii i nieobsługiwane wykluczenie. | Pierwszeństwo istniejącej reguły alergii, API=0, backend=0, MSG-02; bez diagnozowania użytkownika. | NTO-03; ACC-07/11 |
| NTC-18 | Model bez narzędzia twierdzi w content „przeszukano bazę, brak wyników”. | Backend=0 i MSG-01, bez powielenia twierdzenia ani MSG-04. | NTO-03/04; ACC-05/06 |

T021 zapisze demonstrację odmowy jako `Narzędzie: brak wywołania` oraz
`Argumenty: nie dotyczy`, zachowując linię `Zapytanie: ...`. To opis decyzji
w przykładzie systemowym, nie treść do wypisania użytkownikowi ani nowe
narzędzie. Pozostałe instrukcje V4 już powierzają odpowiedź aplikacji;
do wprowadzenia przykładów dopisać znaczenie braku wywołania zgodne z NTO-02/08.

Nie dodajemy kanału powodu odmowy, nowego schematu odpowiedzi ani drugiego
modelu. T022 wdrożyło komunikat ogólny, klasyfikację znanych błędów
odpowiedzi przed dispatch i zgodną diagnostykę raw/application.
Poprawa gramatyki preflight pozostaje osobnym zakresem; jej fałszywe blokady
nie zostały w T019 zaakceptowane jako poprawne no_tool.

T020 zamyka projekt z DEC-11 / INS-07. W wersji proponowanej po MVP
keto kwalifikuje przepis według finalnych węglowodanów na porcję.
Niższa kaloryczność i wyższa zawartość białka porządkują zgodne dania.
Projekt określa sposób rozstrzygania dwóch preferencji, dobór SKU, kontrakt
v2 i migrację. W obecnym MVP obowiązują Z-04, jeden `nutrition_goal`
i dotychczasowa granica T019. [Projekt T020](nutrition-goals.md).

**Punkty 4/5 audytu — kierunek ustalony (DEC-12):** T021 ma przygotować
`evals/routing_prompts/V5.txt`. Zachować format V4: zapytanie, wskazane
narzędzie i pełne argumenty; wymienić zestaw przykładów na kontrastowy.
Przykłady no_tool opisać zgodnie z T019, jako brak wywołania, bez fikcyjnego
narzędzia no_tool. Z zastrzeżeniem wyjątków T017 poniżej zachować pozostałe
instrukcje V4. Nie zmieniać parametrów modelu, wspólnego schematu ani
historycznych V0–V4. Każdy przykład powiązać z regułą
kontraktu i sprawdzić offline. Zakres oraz warunki ukończenia prowadzi T021.
Samo przygotowanie V5 nie potwierdza naprawy zachowania modelu.

Uszczegółowienie zakresu po T017: w nowym V5 dopuszczona jest minimalna
korekta dwóch bezwarunkowych zdań o „bez mięsa” (akapity OBSŁUGIWANE
PREFERENCJE i DIETA) do ROU-12/13 oraz wprowadzenia do przykładów,
które w V4 zapowiada wyłącznie wywołania. Bez tych wyjątków zachowanie
całego tekstu V4 kolidowałoby z kontrastami DEC-09 i no_tool. Pozostała
treść pozostaje bez zmian; diff ma osobno pokazać te korekty i demonstracje.
Nie jest to polecenie edycji promptów w ramach T017.

### T021 — V5 przygotowane offline

Wykonano 2026-11-17: [V5](../../evals/routing_prompts/V5.txt) zawiera 14
demonstracji wywołania z pełnymi argumentami oraz 4 demonstracje braku
wywołania. Zachowano format V4 i zakres korekt INS-02/wprowadzenia ustalony
w T017/T019. Każdy przykład ma ID D5-01–18 i regułę kontraktu w mapie
pokrycia w sekcji 13 planu; ID nie są dopisywane do promptu modelu.

[Nowe przypadki diagnostyczne](../../evals/routing_v5_cases.json) są odrębne
od demonstracji. Do małego porównania zaplanowano 20 niezmienionych
przypadków starego pilota i 12 nowych. Pięć znanych fałszywych blokad
preflight ma osobny audyt offline z zachowanym expected=tool; nadal
pozostają błędami aplikacji i luką w akceptacji MVP.

[Program przygotowania](../../evals/prepare_routing_v5.py) kontroluje
argumenty, kontrasty, zakres diffu i rozdzielenie zapytań, a następnie może
zamrozić wejścia i plan. Nie importuje SDK/main/bazy, nie potrzebuje klucza
i nie ma trybu wykonania płatnego pomiaru. Przygotowanie T021 zamroziło
stan przed T022; po wdrożeniu T022 wymagany jest nowy manifest.
Dowody przygotowania są w `verification.md`. Nie uznano H-T017 ani ACC
za potwierdzone. Aktywny V0, wspólny schemat po T018 i historyczne V0–V4
pozostały bez zmian. Wykonanie porównania otrzymało odrębne T023.

### T022 — wdrożony kontrakt no_tool w aplikacji i diagnostyce

Wykonano 2026-11-17. Aplikacja używa MSG-01 dla zwykłego braku wywołania
i MSG-06 dla nieznanej funkcji oraz znanych błędów odpowiedzi. Wspólna
funkcja w [llm_response_validation.py](../../core/llm_response_validation.py)
wykrywa brak choices, length, content_filter i niepuste refusal przed
odczytaniem argumentów lub dispatch. Nie analizuje content jako przyczyny.

W [runnerze](../../evals/run_routing_eval.py) te odpowiedzi mają
failure_stage=protocol, effective_action=error oraz brak oceny decyzji
modelu i pól. Zachowano diagnostyczny ślad liczby/nazw/argumentów wywołań
i metadane, bez wykonywania częściowo poprawnego wywołania. Raporty i wiersze
oznaczono response_validation_version=T022-v1; response_failure_reason
jest technicznym powodem błędu, a nie polem schematu modelu lub powodem
niezgodności prośby z katalogiem.

Regresja obejmuje 283 testy z kontrolowanymi odpowiedziami, bez rzeczywistych
żądań OpenAI. Znane fałszywe blokady preflight nadal pozostają błędami
application, bez przypisywania modelowi próby. Dowody i pokrycie NTC są
w `verification.md`. Nie potwierdzono jakości interpretacji przez model.
Aktywny V0, schemat narzędzia, parser preferencji, preflight, katalog,
V0–V5 oraz etykiety zachowano. Nowy plik walidacji jest uwzględniany w hashach
nowych przygotowań; historyczne przygotowanie T021 i dawne raporty pozostają
niezmienione. Następny pomiar jest odrębnym T023.

### T023 — pomiar i przegląd V4/V5 zakończone

Zakończono 2026-11-17: [runner V4/V5](../../evals/run_routing_v5.py),
kontrole, osobno zatwierdzony pomiar, audyt i przegląd T017-v1.
**DEC-13: V5 nie kwalifikuje się; aktywny V0 pozostaje bez zmiany.**
[Raport i uzasadnienie](../../docs/reports/t023_routing_2026-11-17.md).

Kompletny przebieg 02 obejmuje 384 oceny / 354 wywołania, 32 przypadki,
trzy rundy i oba tryby, jeden resolved model oraz 0 błędów technicznych.
V5: 75/96 raw, 78/96 application; V4: 84/96 raw, 86/96 application.
V5 zachował no_tool 21/21 i ograniczył niezamówione fish 4 → 0 w obu
trybach, lecz ma sześć regresji w każdym, 13 błędnych dispatch application
i tylko 25/32 przypadków stabilnych. Intent_004 i diag_004 pozostały 0/3
w obu trybach. Nie zmieniono progów, expected ani H-T017 po wynikach.
Poprawa fish daje częściowe wsparcie kierunku, bez pełnej kwalifikacji V5.

Wykonawca egzekwuje hash planu i budżet przed klientem, dokładne payloady,
rezerwację przed SDK, retry=0 i zakaz selektywnego wznowienia. Pierwszy
zatwierdzony przebieg 01 przerwał błąd zastąpienia pliku Windows po 262
ocenach i 242 odpowiedziach. Zachowano go osobno; poprawiono lokalny zapis
i dopiero po nowej zgodzie wykonano cały 02. Wyników nie połączono.
Pełna regresja po poprawce: **302/302**, bez pominięć, z generacją SDK
i zapisami do katalogu zablokowanymi. Symulacje są oznaczone jako mock.

Koszt referencyjny z usage bez cache: 02 — 0,19128450 USD,
01 — 0,13034625 USD; suma 0,32163075 USD nie jest rachunkiem dostawcy.
Osobny audyt zachowuje pięć fałszywych blokad jako błędy preflight poza
mianownikiem 32. Badano interpretację z atrapą lookup, bez nowego holdoutu,
pełnej jakości rekomendacji i akceptacji ACC. Katalog, V0–V5, schemat
i kod aplikacji pozostały bez zmian. Dowody są w `verification.md`.

### T024 — poprawa fałszywych blokad preflight

Zlecono 2026-11-17 po przeglądzie T023. Zakres obejmuje gramatykę
`mentions_unsupported_exclusion`, testy i dostosowanie audytu do aktualnego
stanu ochrony. Bez nowego filtra, zmiany promptu, argumentów narzędzia,
backendu lub danych i bez płatnego pomiaru modelu. Pięć historycznych
przypadków zachowuje treść i expected=tool.

**Zakończono 2026-11-17 (DEC-14).** Pięć przypadków przechodzi preflight.
Pełna regresja: **314/314**, bez pominięć, rzeczywiste żądania SDK i zapisy
katalogu zablokowane. Poprawny podstawiony call ma jeden dispatch,
błędne podstawione no_tool nadal jest porażką decyzji. Audyt bez LLM
oznacza tylko wynik preflight, bez sukcesu modelu. Nie zmieniono V0–V5,
schematu, golden labels i historycznych dowodów ani nie wykonano płatnej
kampanii. [Dowody](verification.md#t024--poprawa-preflight-zakończona).

| ID | Wymaganie | Weryfikacja |
| --- | --- | --- |
| PFL-01 | guard_005/006 i DP-02/03/22 przechodzą preflight. Przy podstawionej odpowiedzi bez tool_calls mają jeden call modelu, brak backendu i błąd decyzji; przy poprawnym pojedynczym callu mają jeden dispatch z expected. Sam brak blokady nie jest dowodem jakości modelu. | Pięć przypadków w gramatyce i rzeczywistym przepływie application z atrapami. |
| PFL-02 | Lokalna konstrukcja „nie musi/muszą być bez …” znosi wymóg jednego wykluczenia. Nie znosi kolejnych samodzielnych wykluczeń. Niejednoznaczna lista z nieobsługiwanym drugim elementem, inne negacje i cytaty pozostają konserwatywnie blokowane. Nie dodaje to ograniczenia ani parametru. | Kontrasty negacji, list, cytatów i ponownego dodatniego wymagania. |
| PFL-03 | Po „i/oraz” rozpoznać nazwę posiłku lub parę przymiotnik szybkości + posiłek, w tym „szybki obiad”, zamiast traktować je jako nazwę wykluczanego składnika. Samo „na/do” nie kończy listy. Zachować sprawdzanie wszystkich osobnych wykluczeń oraz nieobsługiwanych elementów list. | guard_006 i odmiany; dodane „bez mleka/jaj” oraz elipsy „i na pewno mleka / oraz do tego jaj” nadal blokują całość. |
| PFL-04 | Po przecinku rozpoznać „ryby mogą być / ryby są dozwolone”, prośbę zaczynającą się od „chcę” i „nie musi/muszą być z …” jako nowe klauzule. Sama obecność „ryby” lub „nie” nie kończy listy wykluczeń. | DP-02/03/22 oraz „bez mięsa, ryb, jaj”, „bez mięsa, nie jem jaj”. |
| PFL-05 | Zachować blokadę nieobsługiwanych dodatnich wykluczeń, złożeń typu bezmleczny, samotnego „bez ryb”, pustych i niejednoznacznych wykluczeń. Ochrona alergii, także przy negacji lub innych filtrach, zachowuje pierwszeństwo i dotychczasowy komunikat. | Istniejące przypadki blokad, list, Unicode i priorytetu oraz nowe kontrasty. |
| PFL-06 | Preflight nie ustala diety ani innych argumentów i nie naprawia odpowiedzi modelu. Przepuszczenie zapytania umożliwia interpretację; no_tool i błędy odpowiedzi nadal podlegają NTO-01–08 i T022-v1. | Application: poprawny call, błędne no_tool i brak echa treści modelu. |
| PFL-07 | Audyt oddziela wynik samego preflight od pomiaru modelu. Dla przepuszczonego zapytania bez próby LLM nie zapisuje sukcesu semantyki lub decyzji. Niezgodność z zamrożonym stanem ochrony zatrzymuje wykonawcę przed klientem płatnym. | Audyt bez SDK/backendu; zachowane hashe dawnych pakietów T021/T023. |

Warunek ukończenia: pięć przypadków przechodzi preflight, wszystkie
uzgodnione kontrasty i pełna regresja przechodzą bez pominięć, rzeczywista
generacja i zapisy katalogu są zablokowane, dokumentacja odróżnia stan
po T024 od historycznych wyników. Zakres to ograniczona gramatyka,
bez deklaracji obsługi dowolnej negacji lub wszystkich parafraz.

### T025 — projekt kontraktu interpretacji zakończony

Zakończono 2026-11-18 jako projekt, bez implementacji. DEC-15 wybiera
[IR-1](interpretation-contract.md), [schemat](contracts/interpretation-v1.schema.json)
i [fixture'y projektu](contracts/interpretation-v1.examples.json). Nie ma
nowego pomiaru modelu, adaptera SDK, kompilatora ani promptu V6.
T026 następnie zaimplementowało odrębny tryb IR offline; dowody są poniżej.
Poniższe wymagania dotyczą tego kandydata. Aktywne
ROU/NTO, RECIPE_TOOLS, parser, preflight T024 i V0 są bez zmian.

| ID | Wymaganie projektu | Weryfikacja po implementacji |
| --- | --- | --- |
| IR-01 | Po preflight jeden wymuszony submit_recipe_interpretation, strict=true, bez dostępu narzędzia do katalogu. Nie wymuszać wyszukiwania. | IRC-15/17/19; osobne liczniki SDK, calla interpretacyjnego i dispatch. |
| IR-02 | Model przekazuje request_kind i fakty kind/value/status/source według wersji IR-1, bez faktów none/standard i domyślnych parametrów. | Schemat, 35 poprawnych formalnie fixture'ów, IRC-01–13. |
| IR-03 | Walidować cały pakiet, dokładne typy i źródła przed kompilacją. Błąd nie jest brakiem wymagań; nie usuwać niepoprawnego faktu. | IRC-14/16; brak defaultów i backendu po błędzie. |
| IR-04 | Czysty lokalny kompilator stosuje ROU-12–17, rozróżnia wymaganie/dopuszczenie/cofnięcie, wykrywa konflikty i ustala defaulty. Wynik search zawiera dotychczasowe argumenty, bez zmiany backendu. | Reguły 1–12 w IR-1; IRC-01–12; istniejący parser argumentów. |
| IR-05 | Brak zgodnej reprezentacji całej prośby daje no_search bez argumentów i dispatch; nie łączyć automatycznie wielu celów, kategorii czy diet. | IRC-05–13; T020 nadal odrębne. |
| IR-06 | W IR brak wymaganego calla jest błędem protokołu, nie no_tool. No_tool biznesowe oznacza no_search aplikacji, mimo technicznego zgłoszenia interpretacji. Legacy NTO zachowuje stare znaczenie. | Tabela migracji NTO/NTC w IR-1, IRC-15/20. |
| IR-07 | Zachować MSG-01–08, T022-v1 i INT/ERR. Zwykły content oraz modelowe uzasadnienia nie sterują backendem ani komunikatem; bez drugiego LLM. | IRC-14–19; błędy dostawcy przed parsowaniem, lokalny renderer. |
| IR-08 | Nie uznawać wymuszonego calla za sukces decyzji. Osobno mierzyć transport, fakty, kompilację i wynik końcowy względem dotychczasowych expected. | Diagnostyka IR-1; ocena pól nieadekwatna bez poprawnego search. |
| IR-09 | Brak faktu lub dosłowny source nie dowodzą poprawnego rozumienia. Model może pominąć wymóg lub przypisać mu złą etykietę; takie błędy pozostają porażkami semantycznymi. | Dwa jawne przykłady ograniczeń, adnotacje faktów i przyszły pomiar. |
| IR-10 | Implementacja i kwalifikacja są osobnymi etapami. T026 pozostawia domyślny legacy/V0; T027 wymaga świeżego planu i zgody. Diagnostyka 72 wywołań nie dopuszcza wdrożenia ani nie zalicza ACC. | Reguła IR1-D1, T010/T013, nienaruszone dawne etykiety i dowody. |

Projekt ma 20 scenariuszy akceptacji IRC-01–20, reguły kompilatora,
wersjonowaną migrację ROU/NTO oraz plan porównania całej warstwy. Nowe
adnotacje faktów są propozycją do przeglądu przed pomiarem; istniejące
12 zapytań i expected backendu zachowano dokładnie. Kontrola T025 dotyczy
spójności projektu i schematu, nie działania kompilatora lub jakości LLM.
[Dowody](verification.md#t025--projekt-ir-1-zakończony).

### T026 — implementacja IR-1 offline zakończona

Zakończono 2026-11-18 według IR-01–10. Dostępny jest wewnętrzny tryb
facts_v1: ścisła walidacja całego pakietu, czysty kompilator i adapter
jednego submit_recipe_interpretation. Instrukcje kandydata IR1 nie zawierają
pełnych zapytań diagnostycznych. Brak lub błędny call daje błąd protokołu;
poprawna interpretacja może dać no_search bez wywołania backendu.
Diagnostyka rozdziela żądanie SDK, call interpretacyjny i dispatch,
nie przypisując automatycznie sukcesu modelowi.

IRC-01–20 sprawdzono na kontrolowanych odpowiedziach; pełna regresja
347/347 bez pominięć. Zamrożono konfigurację kandydata, bez API modelu,
zapisów do katalogu i zmiany domyślnego legacy/V0. Parser, backend,
renderer i artefakty projektowe T025 zachowano. Skuteczność rozpoznawania
faktów jest niezmierzona; IR-09 pozostaje ograniczeniem. T027 wymaga
osobnego przygotowania i zgody na płatny plan. [Dowody i pokrycie IRC](verification.md#t026--implementacja-ir-1-offline-zakończona).

### T027 — diagnostyka IR-1 zakończona

Zakończono 2026-11-18: po osobnej zgodzie na plan b2fc0dad3729… wykonano
72/72 SDK, 0 błędów API/metadanych, jeden resolved model. DEC-16 odrzuca
IR-1 według zapisanej IR1-D1: raw 22/36 wobec V4 26/36, no_tool 3/9,
obsługiwane 19/27, stabilne 6/12 i pięć regresji per-case. Replay ma
25/36 wobec 29/36 V4 i 11 błędnych symulowanych dispatch; realny backend=0.

Wszystkie 36 interpretacji IR są formalnie poprawne, lecz komplet faktów
zgadza się w 19/36. Pomijane kategorie/cel i błędne fakty o wymaganym
mięsie/bezmleczności wyjaśniają porażki. Koszt referencyjny z usage bez
cache 0,026496 USD, przy rezerwie 0,1637217 USD i progu 0,50 USD.
[Raport](../../docs/reports/t027_interpretation_2026-11-18.md),
[dowody](verification.md#t027--diagnostyka-zakończona).

Domyślny legacy/V0 pozostaje, bez zaliczenia ACC. T028 ma zaprojektować
rozróżnienie braku wymagania od pominięcia ekstrakcji i sposób kontroli
kompletności; nie uruchamia automatycznie nowego promptu lub API.

#### Przygotowanie przed pomiarem

T027.1 zakończono 2026-11-18. Wykonawca porównuje świeże V4 i IR-1
według IR1-D1 z T025: 12 zachowanych zapytań i expected, po trzy próby
w obu ramionach, 72 wywołania SDK. Wynikiem głównym jest decyzja i semantyka
raw interpretacji/kompilacji. Z tej samej odpowiedzi odtwarzamy zachowanie
preflight i dispatch aplikacji; jest to ocena zależna, bez drugiego LLM
i rzeczywistego backendu. Osobno raportujemy ekstrakcję faktów.

Zamrożono payloady, adnotacje po przeglądzie, źródła, runtime, cennik,
harmonogram i regułę. Rezerwa szacunkowa 0,1637217 USD, proponowany lokalny
próg 0,50 USD; nie jest to gwarancja rachunku. Rzeczywisty SDK retry=0,
limit odpowiedzi 1024. Wykonanie wymaga zgody na dokładny hash planu
i próg. Po pierwszej awarii SDK/metadanych lub niezgodnym resolved model
pomiar jest przerywany, bez selektywnego wznowienia.

19 nowych metod testowych; pełna regresja 366/366 bez pominięć, na atrapach.
Poza testami jeden odczyt GET metadanych potwierdził widoczność modelu;
generacje: 0. Nie zmierzono H-IR1 ani nie oceniono IR1-D1 na modelu.
Na etapie przygotowania T027 pozostawało w toku. Pomiar i przegląd
wykonano następnie, jak opisano powyżej; domyślny tryb to legacy/V0.
[Plan, pokrycie i stan zgody](verification.md#t027--przygotowanie-diagnostyki-zakończone).

### T028 — projekt kontroli kompletności zakończony

Zakończono 2026-11-18 jako projekt CMP-1 (DEC-17).
[Kontrakt i zamknięty zakres reguł](interpretation-completeness.md)
porównują listę faktów, jawne grupy pól oraz reguły domenowe. Wybrano
najmniejszą warstwę ochronną: kontrolę wykrytych sygnałów przed dispatch,
bez zmiany modelu, promptu, schematu lub kompilatora.

Projekt rozróżnia brak wymagania, waived, pominięcie, błędną etykietę
i nierozstrzygnięty zakres. Default pozostaje dla poprawnej prośby bez
preferencji, lecz lokalny sygnał deser bez faktu kategorii ma zatrzymać
search. To kontrolowany błąd interpretacji (MSG-06), nie poprawna odmowa
biznesowa ani automatyczna naprawa. Nie twierdzimy, że brak sygnału
potwierdza brak wymagania.

CMP-01–12 obejmują lokalny zakres operatorów, preflight, niezmienność
faktów, defaulty, diagnostykę, replay i ochronę przed fałszywymi blokadami.
35 kontrastów zawiera trzy jawne ograniczenia; kontrola T028 sprawdza
adnotacje i spójność projektu, nie działający detektor. [Dowody](verification.md#t028--projekt-cmp-1-zakończony).
T029 ma wykonać implementację offline i replay T027, bez SDK. Ochrona
aplikacji nie podnosi historycznej oceny rozpoznawania modelu. Nie
zmieniono runtime ani danych; T009/T012 nadal wstrzymane.

### T029 — kontrola przed wyszukiwaniem w trybie wewnętrznym

Tryb `facts_checked_v1` sprawdza kategorię, cel, białko i wybrane wykluczenia
po kompilacji IR-1. Wykryte pominięcie lub nierozstrzygnięty operator przy
proponowanym wyszukaniu kończy zapytanie komunikatem MSG-06. Na 36 odpowiedziach
z T027 aplikacja zatrzymała wszystkie 11 wcześniej błędnych wyszukiwań
i zachowała 25 poprawnych wyników. [Raport T029](../../docs/reports/t029_completeness_2026-11-18.md).

## 6. Granice obsługi

Ograniczenia bez glutenu i bez laktozy oznaczają zgodność z udokumentowaną
polityką katalogu. Nie są deklaracją certyfikacji, pomiaru zawartości substancji
ani gwarancją bezpieczeństwa dla osoby z alergią.

MVP nie obejmuje doboru przepisów dla alergii ani oceny kontaktu z alergenami.
„Bez laktozy” nie jest zamiennikiem „bez mleka” lub „bez nabiału”.
Nieobsługiwane wymaganie nie może zostać świadomie pominięte lub zastąpione
innym filtrem. Zakres rozpoznawania takich próśb oraz znane pomyłki wymagają
osobnych przypadków ewaluacyjnych; nie zakładamy bezbłędnego rozpoznawania
dowolnej parafrazy przez model lub reguły tekstowe.

## 7. Poza zakresem pierwszej wersji

- Nowe funkcje użytkowe, w tym nowe diety, ograniczenia i parametry zapytania.
- Rozbudowa katalogu o kolejne przepisy, produkty lub marki jako cel tego etapu.
- Zwiększanie liczby SKU dopuszczonych do polityki laktozy: obecne nieznane
  statusy pozostają, a takie SKU nadal są wykluczane przy `lactose_free`
  (decyzja autorki z 2026-10-22). Weryfikacja podstawy makro istniejących
  danych jest odrębną kwestią i nie oznacza dopuszczenia SKU do tej polityki.
- Nowy interaktywny interfejs konsolowy lub inny nowy sposób obsługi użytkownika.
- Produkcyjny SaaS, konta klientów, role, płatności i abonamenty.
- Jednoczesna obsługa wielu marek i izolacja ich danych.
- Osadzalny widget, rozbudowany frontend i panel administracyjny.
- Publiczne API oraz produkcyjne wdrożenie i skalowanie usługi.
- Pamięć rozmowy, profile użytkowników i długoterminowa personalizacja.
- Dowolne wykluczenia składników, obsługa alergii i porady medyczne.
- Generowanie nowych przepisów lub dowolnych zamienników w trakcie rozmowy.
- Wyszukiwanie w internecie podczas rekomendacji i automatyczne aktualizacje
  deklaracji produktów.
- Zaawansowane wyszukiwanie semantyczne i infrastruktura wektorowa.
- Swobodna redakcja odpowiedzi przez drugi LLM oraz brand voice wielu marek.
- Dashboard analityczny i badanie skuteczności marketingowej produktu.

Narzędzia generowania danych mogą wspomagać przygotowanie katalogu.
Ich wynik wymaga weryfikacji przed dopuszczeniem do demonstracji.

## 8. Warunki uznania MVP za ukończone

Jedyną listą kryteriów ukończenia jest [acceptance.md](acceptance.md),
obejmująca ACC-01–ACC-14 i zatwierdzone progi. Stan wykonania pracy zapisujemy
w [tasks.md](tasks.md), a powiązania z dowodami w [verification.md](verification.md).
Nie utrzymujemy tu drugiej checklisty.

Kontrola bazowa została wykonana. Skład końcowych zbiorów i przypadki
pomiarowe pozostają do przygotowania. Problem routingu oraz wstrzymana
luka makro nadal nie są zamknięte; samo przejście istniejących testów
nie stanowi akceptacji MVP.

## 9. Kolejny krok SDD i kontrola zmian

Stan zastany, kontrola bazowa, wymagania T005, wdrożenie T006 i specyfikacja
T008 są zapisane. Część offline T009 jest wykonana; płatną kampanię
wstrzymano na decyzję autorki (DEC-05). T009P jest zakończone.
Iteracja routingu T014 jest zakończona: przygotowanie offline, zatwierdzony
pomiar i decyzja przeglądu T014.4 (DEC-07). T015 przygotowało V4 offline,
a T016 zakończyło jego pomiar i przegląd: V4 nie zakwalifikował się
według T015-v1 (DEC-08). Aktywny prompt pozostaje V0. T017 zakończyło
diagnozę i specyfikację relacji diet/protein offline, bez wdrożenia poprawki.
T019 określiło kontrakt no_tool bez wdrożenia, a T021 przygotowało V5 offline.
T022 wdrożyło kontrakt w aplikacji i diagnostyce. T023 zakończyło pomiar
V4/V5 na nowym zamrożeniu źródeł: V5 nie kwalifikuje się (DEC-13), aktywny
V0 pozostaje. T024 poprawiło pięć fałszywych blokad preflight i zakończyło
regresję offline; poprawność modelu po odblokowaniu pozostaje niezmierzona.
T025 zakończyło projekt IR-1, z migracją ROU/NTO i planem oceny; nie zmieniło
aplikacji. T026 zaimplementowało projekt offline: walidację faktów,
kompilator reguł i adapter w wewnętrznym trybie facts_v1. Pełna regresja
347/347 na atrapach nie jest pomiarem modelu. Domyślny tryb to nadal
legacy/V0. T027 zakończyło zatwierdzony pomiar i przegląd z wynikiem
negatywnym (DEC-16). T029 zakończyło implementację i lokalną weryfikację
kontroli CMP-1 (DEC-17). T020 zakończyło projekt wielu celów po MVP.
T007 i T011 pozostają gotowymi zadaniami stabilizacyjnymi.
Kolejność opisuje [plan](plan.md), a stan prac
[zadania](tasks.md). Nie uruchamiamy ponownie wykonanych etapów na podstawie
dawnych notatek.

Ocena obejmuje poprawność interpretacji i routingu, stabilność w powtórzeniach,
zgodność rekomendacji z ograniczeniami, poprawność liczb i produktów,
czytelność oraz kompletność odpowiedzi względem danych, a także zachowanie
w sytuacjach błędnych. Zatwierdzone progi są w `acceptance.md`; przypadki
i konfiguracja kampanii muszą zostać ustalone przed jej wykonaniem.

Nowa funkcja poza powyższym zakresem trafia do planu dalszego rozwoju.
Włączenie jej do MVP wymaga jawnej aktualizacji tego dokumentu wraz
z uzasadnieniem i wpływem na warunki ukończenia.

## 10. Dokumenty powiązane

- [Indeks dokumentacji technicznej i raportów](../../docs/README.md).
- [Architektura obecnego kodu](../../docs/architecture.md).
- [Kontrakt danych](../../docs/reference/data-contract/README.md).
- [Stan zastany](../../docs/archive/baseline/current_state_2026-10-22.md)
  i [kontrola bazowa](../../docs/reports/baseline_2026-10-22.md).
