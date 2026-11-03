# Specyfikacja — stabilizacja istniejącego MVP

Data: 2026-10-22<br>
Wersja dokumentu: 0.8; przegląd i decyzja T014.4: 2026-11-03<br>
Status: zakres, progi i DEC-01–03 zatwierdzone; wymagania integralności
i błędów wdrożone w T006; protokół T008 opracowany. Pięć SKU pozostaje wstrzymanych.

Nawigacja: [kryteria](acceptance.md) · [plan](plan.md) ·
[zadania](tasks.md) · [weryfikacja](verification.md).

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

Kolejna praca nad routingiem otrzymuje ID T015 i pozostaje offline:
przed zmianą promptu określić hipotezę naprawy `intent_004/010/032`,
regułę porównania i scenariusze dla istniejących ROU-01–ROU-04/07–ROU-10.
Nie pomijać diety ze względu na kategorię deseru; nie odmawiać obsługiwanej
preferencji ryby ani `top_n=4`. To obecna semantyka, nie nowe funkcje.
Zachować rozdzielenie raw/application, granice no_tool i brak wykonywania
tekstu JSON. Implementacja wariantu eksperymentalnego wymaga najpierw
tego uzupełnienia specyfikacji; żaden kolejny pomiar nie startuje automatycznie.

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
pomiar i decyzja przeglądu T014.4 (DEC-07). Aktywny prompt pozostaje V0;
V3 jest kandydatem wymagającym dopracowania. Następna iteracja T015 zaczyna
się od specyfikacji hipotezy i przygotowania offline, bez wdrożenia lub nowej
kampanii API. T007 i T011 pozostają niezależnymi zadaniami.
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
