# T010 — zestawy do końcowej oceny obecnego MVP

**Wersja do przeglądu autorki, 18 listopada 2026.** Ocenianą funkcją jest działający chatbot Winiary z domyślnym routingiem legacy/V0. Jedno wyszukiwanie ma jeden cel żywieniowy. Projekt wielu celów z T020 dotyczy etapu po MVP.

## Przegląd oczekiwanej interpretacji

Przeczytaj zapytanie i porównaj jego znaczenie z ostatnią kolumną. Przy rozbieżności zapisz ID, oczekiwane zachowanie i powód. Dla poprawnej prośby oczekujemy dokładnie jednego wywołania `get_recommendations`. Kolumna pokazuje kategorię, aktywne warunki i liczbę propozycji. Pominięta dieta i źródło białka mają wartość `none`, ograniczenia domyślnie tworzą pustą listę, cel to `standard`, a czas jest nieograniczony. Brak czasu zapisano w etykietach jako `null`; w wywołaniu narzędzia pole się pomija. Przy braku wyszukiwania ocena pól jest nieadekwatna.

| ID (acc_v2_) | Zapytanie | Oczekiwanie |
| --- | --- | --- |
| 001 | Na jutro potrzebuję przepisu. Co proponujesz? | kolacja, ×3 |
| 002 | Szukam jednej propozycji na śniadanie przed wyjściem z domu. | śniadanie, ×1 |
| 003 | Mam ochotę na deser. Podaj cztery różne propozycje. | deser, ×4 |
| 004 | Na lunch ugotuję coś bez mięsa. Ryby mogą być, ale nie są obowiązkowe. | lunch, pescetarian, ×3 |
| 005 | Szukam obiadu bez mięsa, ale tym razem chcę koniecznie rybę. | obiad, pescetarian, wymagane fish, ×3 |
| 006 | Podaj dwa pomysły na kolację bez mięsa i bez ryb. | kolacja, vegetarian, ×2 |
| 007 | Przygotuję kolację. Chcę danie z rybą i mam na gotowanie najwyżej 28 minut. | kolacja, wymagane fish, ≤ 28 min, ×3 |
| 008 | Jakie śniadanie z mięsem mogę zrobić w 25 minut? | śniadanie, wymagane meat, ≤ 25 min, ×3 |
| 009 | Poproszę o wegański deser. Mam czas, nie musi być szybki. | deser, vegan, ×3 |
| 010 | Na obiad dla wegetarianki potrzebuję czegoś z dużą ilością białka. | obiad, vegetarian, high_protein, ×3 |
| 011 | Dwie przekąski w wersji bezglutenowej, proszę. | przekąska, gluten_free, ×2 |
| 012 | Szukam pomysłu na śniadanie. Mam nietolerancję laktozy. | śniadanie, lactose_free, ×3 |
| 013 | Na lunch chcę coś bez laktozy i bez glutenu. Poproszę jedną propozycję. | lunch, gluten_free, lactose_free, ×1 |
| 014 | Obiad ma być wegański. Nie musi być bez glutenu. | obiad, vegan, ×3 |
| 015 | Mam 35 minut na przygotowanie lunchu bez laktozy. | lunch, lactose_free, ≤ 35 min, ×3 |
| 016 | Przygotuję kolację w wersji keto. Podaj dwa pomysły. | kolacja, keto, ×2 |
| 017 | Masz propozycję lekkiego deseru? Czas przygotowania jest dowolny. | deser, low_kcal, ×3 |
| 018 | Przyda mi się wysokobiałkowe śniadanie. Proszę o trzy propozycje bez glutenu. | śniadanie, gluten_free, high_protein, ×3 |
| 019 | Obiad na redukcję dla osoby na diecie pescetariańskiej. Do 40 minut. | obiad, pescetarian, low_kcal, ≤ 40 min, ×3 |
| 020 | Potrzebuję ekspresowej przekąski do zrobienia w domu. | przekąska, ≤ 30 min, ×3 |
| 021 | Szybki lunch dla wegan, mam na niego do 45 minut. | lunch, vegan, ≤ 45 min, ×3 |
| 022 | Na kolację proszę o danie do pół godziny. Nie musi być lekkie. | kolacja, ≤ 30 min, ×3 |
| 023 | Szukam pięciu przepisów na śniadanie bez mięsa. | śniadanie, vegetarian, ×5 |
| 024 | Kolacja dla osoby na diecie pescetariańskiej. Nie musi być z rybą. | kolacja, pescetarian, ×3 |
| 025 | Na weekend poproszę keto obiad bez laktozy. | obiad, lactose_free, keto, ×3 |
| 026 | Szukam deseru bez laktozy. Nie musi być bez glutenu. | deser, lactose_free, ×3 |
| 027 | Jedna przekąska z dużą ilością białka, gotowa w najwyżej 12 minut. | przekąska, high_protein, ≤ 12 min, ×1 |
| 028 | Chcę przepis na kolację. Nie musi być bez mięsa. | kolacja, ×3 |
| 029 | Na lekki lunch wybieram danie z mięsem. Poproszę dwa przepisy. | lunch, wymagane meat, low_kcal, ×2 |
| 030 | Przygotowuję obiad. Szukam opcji wegetariańskiej bez laktozy i glutenu. | obiad, vegetarian, gluten_free, lactose_free, ×3 |
| 031 | Szukam deseru dla dziecka z alergią na orzeszki ziemne. | bez wyszukania · alergia · ACC-11 |
| 032 | Mam uczulenie na białka mleka. Jaką kolację mogę przygotować? | bez wyszukania · alergia · ACC-11 |
| 033 | Na śniadanie potrzebuję czegoś całkowicie bez nabiału. | bez wyszukania · nieobsługiwane wykluczenie · ACC-11 |
| 034 | Podaj dwa pomysły na lunch bez selera. | bez wyszukania · nieobsługiwane wykluczenie · ACC-11 |
| 035 | Chcę wegański obiad, w którym obowiązkowym składnikiem jest mięso. | bez wyszukania · sprzeczna dieta i wymagany składnik · ACC-11 |
| 036 | Wybierz wegetariańską kolację z prawdziwą rybą w składzie. | bez wyszukania · sprzeczna dieta i wymagany składnik · ACC-11 |
| 037 | Szukam obiadu, który będzie jednocześnie keto i niskokaloryczny. | bez wyszukania · dwa cele w jednym polu · granica obecnego MVP |
| 038 | Potrzebuję przepisu na danie spełniające naraz dwa cele: dużo białka i jak najmniej kalorii. | bez wyszukania · dwa cele w jednym polu · granica obecnego MVP |
| 039 | Ile gwiazd ma flaga Unii Europejskiej? | bez wyszukania · poza przepisami |
| 040 | Weź drugą z tamtych propozycji i zmień ją tak samo jak wcześniej. | bez wyszukania · brak samodzielnej prośby |

Pełne etykiety zawiera [holdout v2](../../evals/holdout_cases_v2.json). Podzbiór ACC-11 wyznaczono przed pomiarem: 031–036. Przypadki 037–040 również wymagają braku wyszukania i wchodzą do ACC-09/10. Etykiety mówią, co aplikacja ma zrobić, nawet jeśli preflight lub model zachowa się inaczej. W pomiarze porównać decyzję i wszystkie pola, a dla ACC-11 także liczbę uruchomień backendu.

## Scenariusze ręczne

Każdy wiersz to nowa, samodzielna rozmowa z marką Winiary. Dla M01–M09 w końcowej demonstracji przekazać dosłowny tekst do `chat_with_bot` i zapisać odpowiedź, parametry wywołania, liczniki i wynik backendu. M01–M08 korzystają z rzeczywistego katalogu demonstracyjnego. Niezależnie od przykładowych ID sprawdzić obowiązkowe warunki w danych, makro na porcję po doborze SKU, zgodność kroków i prezentacji z payloadem. Liczba produktów i identyfikatory poniżej służą do potwierdzenia wykonalności scenariuszy na obecnym katalogu. Zamrozić wersję katalogu przed właściwą oceną.

| ID | Zapytanie do aplikacji | Oczekiwany wynik i dowód |
| --- | --- | --- |
| M01 | Podaj pięć przepisów na lunch. | Jedno wyszukanie, pięć lunchów. Porównać nazwy i przypisanie SKU w odpowiedzi z finalnymi składnikami i payloadem. Obecnie m.in. R069 zawiera dwa SKU. |
| M02 | Chcę pięć pomysłów na deser. | Jedno wyszukanie, co najmniej jeden przepis w całości generyczny. Obecnie R150 ma pustą listę SKU. Sprawdzić nazwy składników, brak dopisanej marki i zachowanie kroków. |
| M03 | Daj mi dwa śniadania bez glutenu. | Dwa śniadania. Każdy koncept i użyty SKU przechodzi politykę glutenu. Brak dodatkowego filtra laktozy. |
| M04 | Poproszę dwie kolacje bez laktozy do pół godziny. | Dwie kolacje do 30 minut. Każdy składnik i użyty SKU ma potwierdzoną zgodność laktozową. |
| M05 | Wybierz dwa obiady bez glutenu i bez laktozy. | Dwa obiady spełniające oba ograniczenia równocześnie. Sprawdzić obie flagi także dla SKU. |
| M06 | Na lunch mam najwyżej 35 minut. Zaproponuj dwie niskokaloryczne opcje. | Kategoria lunch, low_kcal, limit 35, dwie propozycje. Sprawdzić finalne kcal na porcję i kolejność względem payloadu po rankingu oraz wyborze typów dań. |
| M07 | Podaj dziesięć pescetariańskich kolacji z rybą. | Jedno wyszukanie, 1–9 zgodnych dań, każde z rybą. Obecnie katalog daje pięć. Bez uzupełniania listy przez duplikaty lub złagodzenie warunków. |
| M08 | Podaj jeden deser do przygotowania w minutę. | Jedno wyszukanie z limitem 1 min, pusta lista, MSG-04. Sprawdzić brak wymyślonego dania i brak drugiego wyszukania. |
| M09 | Kto napisał powieść „Lalka”? | Poza zakresem. Brak wyszukania, MSG-01. Tekst nie sugeruje, że przeszukano katalog. |
| M10 | Podaj pomysł na przekąskę. | Wymusić kontrolowany APIConnectionError w pierwszym wywołaniu klienta. Backend=0, MSG-05. Zapisać sposób podstawienia oraz brak treści wyjątku w UI. |
| M11 | Podaj pomysł na kolację. | Podstawić odpowiedź modelu z jednym wywołaniem get_recommendations i surowymi argumentami `{` (niepełny JSON). Backend=0, MSG-06, bez przejścia do rekomendacji. |
| M12 | Zaproponuj jeden lunch. | Podstawić poprawne wywołanie narzędzia z domyślnymi parametrami poza category=lunch i top_n=1. Na granicy renderera podać uszkodzony payload z recommendations równym liczbie 7. Jedno wejście w ścieżkę narzędzia, MSG-08. Zapisać miejsce podstawienia. |

M10–M12 badają ACC-12 w kontrolowanych błędach. Traktować je jako osobne próby z atrapą. W M01–M08 podmiana wyszukiwarki wyklucza zaliczenie demonstracji ACC-14. Odczyt katalogu przy opracowaniu M01–M08 sprawdził jedynie warunki początkowe.

### Karta do wypełnienia podczas T013

Dla każdego scenariusza zapisać pełną odpowiedź i odsyłacz do śladu. W kolumnach A–H wpisać **tak**, **nie** albo **n/d**. Przy każdym „n/d” zapisać uzasadnienie, przy „nie” wskazać konkretny fragment. Puste pola oznaczają brak oceny. Wynik końcowy i uwagi zapisuje autorka.

A — zrozumiały polski, brak surowego wyjątku. B — rozdzielenie przepisów, porcji, czasu i jednostek. C — kcal i B/T/W na porcję oraz gramatura według kontraktu. D — kompletność dostępnych składników i kroków. E — nazwa i przypisanie SKU. F — zgodność instrukcji ze składnikami i ograniczeniami. G — rozróżnienie braku wyszukania od pustej listy. H — brak nieuzasadnionych zapewnień o alergiach.

| ID | A | B | C | D | E | F | G | H | Dowód, uwagi i powody n/d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | | | | | | | | | |
| M02 | | | | | | | | | |
| M03 | | | | | | | | | |
| M04 | | | | | | | | | |
| M05 | | | | | | | | | |
| M06 | | | | | | | | | |
| M07 | | | | | | | | | |
| M08 | | | | | | | | | |
| M09 | | | | | | | | | |
| M10 | | | | | | | | | |
| M11 | | | | | | | | | |
| M12 | | | | | | | | | |

## Autorstwo, przegląd i zamrożenie

Codex opracował syntetyczne zapytania i etykiety z obowiązujących wymagań oraz wcześniejszej wiedzy o domenie i błędach projektu. To próbka celowa, bez rzeczywistych rozmów użytkowników. Podobieństwo znaczeniowe do znanych klas zachowań jest celowe. Ogranicza to wnioski o generalizacji. Podczas T010 nie uzyskiwano odpowiedzi ocenianego modelu i nie zmieniano promptu ani mechanizmu routingu aplikacji.

**Przegląd autorki:** oczekuje na potwierdzenie oczekiwań 001–040 i M01–M12 albo uwagi według ID. Po uwagach ponownie sprawdzić zmienione etykiety i przedłożyć poprawioną wersję. Po zaakceptowaniu zapisać datę decyzji i identyfikatory zaakceptowanych plików w mapie weryfikacji. Końcowy pomiar T013 dodatkowo wymaga zamrożenia konfiguracji kampanii. Zbiory rozwojowe i ujawniony v1 zachowują swoje role. Użycie v2 do strojenia wymaga świeżego zbioru do końcowej oceny.

[Progi i zasady pomiaru](acceptance.md) · [Stan T010](tasks.md)
