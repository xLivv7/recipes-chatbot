# Kryteria akceptacji MVP — stabilizacja obecnych funkcji

Data: 2026-10-22<br>
Wersja: 0.2<br>
Status: progi zaakceptowane przez autorkę projektu 2026-10-22;
autorka zatwierdziła przypadki i scenariusze T010 2026-11-18. [Materiał i oczekiwania](final-evaluation-cases.md)
oraz [stan przeglądu autorki](verification.md#t010--przygotowanie-zestawów).

Nawigacja: [specyfikacja](spec.md) · [plan](plan.md) ·
[zadania](tasks.md) · [weryfikacja](verification.md).

## 1. Cel i zakres

Dokument określa, jak ocenić gotowość MVP opisanego w [zakresie](spec.md).
Punktem wyjścia jest [stan zastany](../../docs/archive/baseline/current_state_2026-10-22.md). Kryteria dotyczą
istniejących możliwości, jakości danych, niezawodności i prezentacji.
Nie wprowadzają nowych diet, ograniczeń, interfejsów ani obsługi wielu marek.

Każde kryterium otrzymuje ocenę: **nieocenione**, **spełnione**,
**niespełnione** lub **pomiar nieważny/niepełny**, wraz z odsyłaczem do dowodu.
Na dzień utworzenia wszystkie kryteria są nieocenione. Istniejący test
lub raport historyczny jest materiałem wejściowym, a nie automatycznym
potwierdzeniem gotowości aktualnej wersji.

Przyjęte progi mają charakter inżynierski dla lokalnego demonstratora.
Nie wynikają z normy ani z dowodu statystycznego, że system osiąga taką jakość
dla wszystkich przyszłych wypowiedzi. Nie należy dopasowywać ich do wyników.
Zatwierdzono pełne przejście wymaganych testów deterministycznych, co najmniej
90% poprawnych ocen routingu application, co najmniej 85% przypadków poprawnych
we wszystkich trzech powtórzeniach i brak wyszukiwania dla wszystkich ustalonych
przypadków nieobsługiwanych wymagań. Nie oznacza to zaliczenia kryteriów ani
zatwierdzenia jeszcze nieopracowanej zawartości holdoutu i zestawu ręcznego.

## 2. Kryteria deterministycznej części aplikacji

W tej grupie wymagamy przejścia wszystkich uzgodnionych przypadków.
„Wszystkie” oznacza jawny zestaw testowy, a nie dowód dla dowolnych danych.
Zestaw musi pokrywać przypadki pozytywne, negatywne i brzegowe.

| ID | Kryterium i warunek zaliczenia | Sposób weryfikacji / istniejący punkt zaczepienia | Zakres |
| --- | --- | --- | --- |
| ACC-01 | Każdy zwrócony przepis spełnia wybrane ograniczenia, kategorię i limit czasu; sprzeczne preferencje są odrzucane. Wszystkie przypadki przechodzą. | Testy `test_recommendations*.py`, `test_lactose_recommendations*.py`, `test_lactose_recipe_filter.py`; kontrolowane katalogi i integracja z katalogiem demonstracyjnym. | MVP-02; ST-03 |
| ACC-02 | SKU istnieje, jest przypisane do właściwego składnika i spełnia aktywne ograniczenia; brak zgodnego SKU nie dopuszcza niezgodnego konceptu. Wszystkie przypadki przechodzą. | Testy brandingu, ograniczeń i polityk SKU; weryfikacja wariantu generycznego. | MVP-03 |
| ACC-03 | Makro wynika z finalnych składników i SKU, z poprawnym przeliczeniem porcji. Wszystkie porównania z niezależnie obliczonym wynikiem przechodzą przy jawnej tolerancji. | Testy odżywcze i obliczeń w `test_recommendations.py`; tolerancja zgodna z kontraktem normalizacji, zapisana przy przypadku. | MVP-04 |
| ACC-04 | Renderer zachowuje nazwy, kolejność, liczby i przypisania produktów z poprawnego payloadu. Nie dopisuje brakujących treści; niepoprawny payload jest odrzucany. Wszystkie przypadki przechodzą. | `test_response_renderer.py`, `test_chat_response_protection.py`, offline `run_renderer_eval.py`. | MVP-05; ST-05 |
| ACC-05 | Pusty wynik daje komunikat bez wymyślonych przepisów i bez rozluźnienia ograniczeń. Brak wyszukiwania jest komunikowany odrębnie. Wszystkie przypadki przechodzą. | Testy pustych wyników, renderera i ścieżki bez wywołania narzędzia. | MVP-05, MVP-06 |
| ACC-06 | Niepoprawny JSON, brak wymaganych pól, nieznane pola/enumy, sprzeczności, nieznane narzędzie i wiele wywołań nie uruchamiają backendu. JSON ze zwykłej wiadomości nie jest wykonywany. Wszystkie przypadki przechodzą. | `test_tool_call_validation.py`, `test_chat_response_protection.py`. | MVP-01, MVP-06; ST-01 |
| ACC-07 | Dla uzgodnionych awarii API i błędów payloadu aplikacja zwraca kontrolowany komunikat bez treści wyjątków i sekretów. Błędy przygotowania danych nie są po cichu uznawane za poprawny brak wyników. | Testy błędów oraz przegląd szerokiego `except Exception` w przygotowaniu przepisów; lista ocenianych awarii ustalona przed testem. Nie wymaga ukrywania błędów programistycznych pod ogólnym komunikatem. | MVP-06; ST-04 |
| ACC-08 | Walidator katalogu demonstracyjnego: 0 nierozwiązanych ERROR. Każdy WARNING ma uzasadnioną decyzję i nie podważa spełnienia pozostałych kryteriów. Zasady dla brakujących polityk są jawne i przetestowane. | Raport `validate_db.py`, przegląd decyzji curation i kompletności polityk. | MVP-07; ST-03, ST-05 |

Pełny uzgodniony zestaw regresyjny musi przejść. Test pominięty nie jest
testem zaliczonym. Przypadek uznany za nieaktualny wymaga jawnego uzasadnienia
i aktualizacji specyfikacji; nie usuwa się go wyłącznie dlatego, że zawodzi.
Obecność wskazanych plików nie oznacza, że pokrywają już całe kryterium.

## 3. Kryteria interpretacji zapytań i routingu

Ocena ma dwa poziomy: `raw` mierzy zachowanie modelu, a `application`
rzeczywisty routing z ochroną i walidacją aplikacji. W obu przypadkach
wyszukiwanie jest zastąpione kontrolowanym wynikiem. Poprawność rekomendacji
na danych i pełny przepływ są sprawdzane osobno w ACC-01–ACC-04 i ACC-14.

### Przyjęte progi

| ID | Kryterium | Warunek zaliczenia |
| --- | --- | --- |
| ACC-09 | Poprawność obsługi zapytań w trybie application | Co najmniej 90% poprawnych ocen łącznie oraz co najmniej 90% w podzbiorze obsługiwanych próśb o przepisy. Warunek spełniony osobno na regresji i nowym holdoucie. |
| ACC-10 | Stabilność application w powtórzeniach | Co najmniej 85% przypadków poprawnych we wszystkich trzech powtórzeniach, osobno na regresji i holdoucie. |
| ACC-11 | Granice obsługi w application | Wszystkie przypadki oznaczone przed pomiarem jako nieobsługiwane wykluczenia, prośby alergiczne i sprzeczne preferencje kończą się bez uruchomienia wyszukiwania. Ochrona nie tworzy gwarancji dla dowolnych parafraz. |

Wynik pojedynczej oceny jest poprawny tylko wtedy, gdy zgadza się
decyzja o wyszukiwaniu oraz, dla obsługiwanej prośby, wszystkie wymagane
wartości argumentów. Poprawna struktura JSON bez poprawnej semantyki
nie wystarcza. Zablokowanie obsługiwanej prośby jest błędem także wtedy,
gdy jest zgodne z obecną ostrożną heurystyką.

Tryb raw jest obowiązkowym pomiarem diagnostycznym raportowanym oddzielnie,
bez dodatkowego progu w tej propozycji. Blokada przed wywołaniem modelu
nie jest jego sukcesem. Należy pokazać także wyniki raw dla przypadków
zatrzymywanych przez aplikację i ograniczenia samych zabezpieczeń.

### Zbiory i warunki pomiaru

1. Regresja obejmuje istniejące 76 przypadków routingu. Ewentualne zmiany
   etykiet wymagają uzasadnienia i nowej wersji zbioru, z zachowaniem historii.
2. Propozycja nowego holdoutu: co najmniej 40 przypadków — co najmniej
   30 obsługiwanych próśb i 10 przypadków bez wyszukiwania. Powinien obejmować
   różne preferencje, negacje, limity i połączenia warunków oraz granice obsługi.
   Dokładny skład i oczekiwania trzeba zamrozić przed kampanią akceptacyjną.
3. Oczekiwania sprawdza autorka projektu. Należy zapisać sposób autorstwa
   i przeglądu zbioru oraz ograniczenia jego niezależności.
4. Holdout nie służy do strojenia. Ujawniony v1 może pełnić rolę regresji;
   kolejne strojenie na wynikach nowego zbioru wymaga nowego holdoutu do
   niezależnej oceny. Jeden zachowany błąd nie uzasadnia usunięcia przypadku.
5. Każdy przypadek jest oceniany trzy razy w każdym trybie. Nie wybiera się
   najlepszego przebiegu. Progi liczy się na dokładnych ułamkach, bez
   zaokrąglania procentów w celu zaliczenia.
6. Przed kampanią zamraża się commit, prompt, schemat, konfigurację modelu,
   zbiory, polecenia uruchomienia i wersję niniejszego dokumentu. Zapisuje się
   identyfikator modelu faktycznie zwrócony przez API, jeżeli jest dostępny.
7. W kampanii nie zmienia się promptu, ochrony, etykiet ani kryteriów.
   Każda zmiana tworzy nowy wariant i nowy komplet raportów.
8. Raport pokazuje liczby poprawnych/ocenianych, wynik każdego powtórzenia,
   stabilne przypadki i błędy: API, protokołu, argumentów, decyzji,
   semantyki oraz ochrony wejścia. Wymienione podzbiory mają jawne mianowniki.

Do rozstrzygnięcia ACC-09–ACC-11 potrzebna jest pełna kampania bez błędów
API i brakujących ocen. Kampanię z awariami zachowuje się, raportuje wynik
ogólny z awariami i oznacza jako niewystarczającą do akceptacji jakości.
Nie usuwa się awarii z raportu ani nie ponawia wybiórczo samych porażek.
Ewentualny nowy pełny przebieg musi mieć osobny raport.

Zakończenie runnera kodem 1 może oznaczać choćby jedną niepoprawną ocenę.
Nie jest samo w sobie rozstrzygnięciem progów 90%/85%; trzeba ocenić raport.
Niepełny raport nie stanowi dowodu zaliczenia.

## 4. Czytelność, demonstracja i odtwarzalność

| ID | Kryterium | Warunek zaliczenia |
| --- | --- | --- |
| ACC-12 | Czytelność i kompletność odpowiedzi | Wszystkie pozycje checklisty poniżej spełnione dla ustalonego zestawu przeglądowego. |
| ACC-13 | Odtwarzalność i aktualność dokumentacji | Zapisane wersje kodu, środowiska, danych, konfiguracji i raportów; instrukcja pozwala odtworzyć lokalne uruchomienie, a dokumentacja opisuje aktualny przepływ. |
| ACC-14 | Demonstracja pełnego przepływu na istniejącym katalogu | Przechodzą uzgodnione scenariusze od zapytania do odpowiedzi z rzeczywistym backendem, bez zastępowania samego wyszukiwania. |

Zestaw do ACC-12 i ACC-14 ustala się przed przeglądem. Propozycja: minimum
12 scenariuszy obejmujących poprawną rekomendację z SKU, wynik generyczny,
ograniczenia osobno i łącznie, cel i czas, mniej wyników niż żądano, brak
wyników, prośbę poza zakresem oraz kontrolowane błędy. Nie wymaga to nowych
rekordów produkcyjnych: przypadki syntetyczne mogą sprawdzać renderer i awarie,
ale scenariusze wyszukiwania w ACC-14 muszą używać katalogu demonstracyjnego.
Podstawienia API dla kontrolowanych awarii trzeba jawnie oznaczyć; nie są
dowodem działania modelu na żywo.

Checklista ręcznej oceny odpowiedzi:

- Teksty aplikacji są po polsku i zrozumiałe; nie zawierają surowych wyjątków.
- Wyraźnie rozdzielono przepisy, porcje, czas i jednostki.
- Kalorie i B/T/W są opisane na porcję, ilości składników zgodnie z kontraktem.
- Dostępne składniki i kroki są przedstawione; brakujące nie są wymyślane.
- Nazwy produktów odpowiadają przypisaniom właściwego przepisu.
- Instrukcje istniejących przepisów nie przeczą wskazanym składnikom
  lub ograniczeniom w ocenianej próbce.
- Komunikat braku wyszukiwania nie sugeruje przeszukania pustej bazy.
- Odpowiedź nie zawiera nieuzasadnionych zapewnień o bezpieczeństwie dla alergików.

Przegląd zapisuje dla każdej pozycji: tak/nie/nie dotyczy i uzasadnienie
ewentualnego „nie dotyczy”. Autorka projektu zapisuje uwagi oraz wynik.
To ocena według checklisty, nie badanie satysfakcji reprezentatywnej grupy.

ACC-13 wymaga wskazania commita, wersji Pythona i bibliotek, sposobu
przygotowania bazy, identyfikatora i miejsca przechowywania snapshotu danych,
poleceń oraz ścieżek raportów. Sekrety nie trafiają do repozytorium.
Raporty mogą być poza Git, ale muszą być trwale dostępne i powiązane z wersją.

## 5. Decyzja o gotowości MVP

MVP można uznać za gotowe, gdy wszystkie ACC-01–ACC-14 są spełnione dla
tej samej wersji kandydującej, nie ma otwartej wady podważającej kryterium,
a znane ograniczenia mają jawny opis. Po zmianie kodu lub danych trzeba
ocenić, które dowody tracą aktualność, i ponowić zależne kontrole.

Raport akceptacji powinien zawierać:

| Pole | Zawartość |
| --- | --- |
| Wersja kandydująca | Commit, konfiguracja, dane i wersja kryteriów. |
| Kryteria | Ocena każdego ACC, odsyłacz do dowodu i niewyjaśnione rozbieżności. |
| Wyniki pomiarów | Pełne mianowniki, powtórzenia, błędy i ograniczenia oceny. |
| Decyzja | Przyjęte / nieprzyjęte / brak wystarczających dowodów, data i uzasadnienie autorki. |

Znane ograniczenie poza zakresem nie blokuje MVP. Wada naruszająca ustalone
kryterium nie może być uznana za zaakceptowaną wyłącznie przez dopisanie jej
do ograniczeń. Zmiana kryteriów wymaga uzasadnionej nowej wersji i nie zmienia
wstecznie oceny wcześniejszego pomiaru.

## 6. Następny krok

Wstępne powiązania kryteriów i luki opisuje [mapa](verification.md).
Kontrola bazowa jest zapisana; kolejne czynności prowadzi [lista zadań](tasks.md).
T012 i T030 rozstrzygnęły podstawę makro pięciu SKU. Cztery warianty
receptur korzystają z tabel na 100 ml, a Majonez Dekoracyjny 400 ml z tabeli na 100 g.
Końcową ocenę całego ACC-03 zapisuje się dla wersji kandydującej w T013.
Nowe pomiary i poprawki mają własne raporty; samo zatwierdzenie progów
nie uruchamia kampanii API.
