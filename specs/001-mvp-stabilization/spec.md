# Specyfikacja — stabilizacja istniejącego MVP

Data: 2026-10-22<br>
Wersja dokumentu: 0.4; aktualizacja T005: 2026-11-03<br>
Status: zakres, progi i DEC-01–03 zatwierdzone; wymagania integralności
i błędów opisane, implementacja oczekuje w T006. Pięć SKU pozostaje wstrzymanych.

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
| DEC-02 | Zasada zatwierdzona; implementacja oczekuje | Brak wymaganej polityki składnika nie oznacza zgodności. Szczegóły opisują INT-01–INT-04 i scenariusze T005. |
| DEC-03 | Zatwierdzona; implementacja oczekuje | Błąd przygotowania przepisu przerywa zapytanie; nie zwracamy częściowego sukcesu ani pozornego braku wyników. Błędy programistyczne nie są maskowane jako poprawna odpowiedź. |
| DEC-04 | Wstrzymana przez autorkę | Nie prowadzimy obecnie przeglądu źródeł pięciu SKU ani zależnych korekt czy wyłączeń. Luka podstawy makro pozostaje otwarta. |

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

Opracowano 2026-11-03 na podstawie DEC-02/03. Poniższe wymagania opisują
zachowanie docelowe do wdrożenia w T006, a nie wynik nowych testów.
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

Stan zastany, kontrola bazowa i wymagania T005 są zapisane.
Najbliższy krok to T006: testy i implementacja INT-01–INT-04 oraz
ERR-01–ERR-05. Kolejność opisuje [plan](plan.md), a stan prac
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
