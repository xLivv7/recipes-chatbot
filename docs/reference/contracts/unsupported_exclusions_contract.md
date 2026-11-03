# Ochrona nieobslugiwanych wykluczen

Status: wdrozona ochrona leksykalna w chat_with_bot, 2026-10-15.
To ochrona zakresu prototypu, nie filtr nowych skladnikow ani pelny parser NLP.

## Decyzja
Rozpoznane wykluczenie spoza kontraktu zatrzymuje cale zapytanie przed API
i backendem. Nie uruchamiamy wyszukiwania z czescia wymagan ani nie
zastepujemy wykluczenia innym filtrem. Nie zmieniamy diet ani danych katalogu.
Wczesniejsza ochrona alergii ma pierwszenstwo i swoj osobny komunikat.

| Wypowiedz | Zachowanie preflight |
| --- | --- |
| bez orzechow / jaj / jajek / mleka / nabialu | zatrzymanie |
| bez soi / pomidorow / cukru | zatrzymanie |
| bez mleka i bez glutenu | zatrzymanie calej prosby |
| weganskie, ale bez jaj | zatrzymanie jawnego nieobslugiwanego wykluczenia |
| bez glutenu / bez laktozy / oba razem | przekazanie do interpretacji LLM |
| bez miesa / bez produktow miesnych | przekazanie do LLM: dotychczasowa dieta |
| bez miesa i ryb / bez ryb i miesa | przekazanie do LLM: dotychczasowa dieta |
| tylko bez ryb | zatrzymanie: brak samodzielnego filtra fish_free |
| nie musi byc bez jaj | zatrzymanie z prosba o doprecyzowanie |
| nie musi byc bez glutenu | przekazanie do LLM: dotychczasowa negacja |

Brak blokady oznacza jedynie przejscie do interpretacji, nie gwarantuje
poprawnego wyboru parametrow przez model. Bez mleka/nabialu nie jest
lactose_free. Jawnego "bez jaj" nie redukujemy do vegan, nawet jesli przy
poprawnej interpretacji diety skladnik bylby juz wykluczony.

## Mechanizm
`mentions_unsupported_exclusion` normalizuje wielkosc liter, polskie znaki
(w tym l) i Unicode. Analizuje ograniczona gramatyke po slowach: bez,
wykluczam, wyklucz, unikam, nie jem, nie spozywam, nie moge jesc/spozywac,
z wykluczeniem/wylaczeniem. Angielskie without jest odrzucane bez tlumaczenia.
Nazwy w tej gramatyce inne niz glutenu/laktozy/miesa sa odrzucane; ryb
wymaga rownoczesnego wykluczenia miesa. Rozpoznaje forme produktow miesnych.
Listy moga uzywac i/oraz/ani/lub/albo, symboli / + & i przecinka. Nowa klauzula
po przecinku moze zaczynac sie m.in. ale, prosze, podaj lub nazwa posilku.
Kazde osobne "bez" jest sprawdzane, wiec drugi filtr nie maskuje pierwszego.

Zlozenia zaczynajace sie od bez sa konserwatywnie odrzucane poza rodzinami
bezglutenowy/bezlaktozowy oraz niebedacymi wykluczeniem bezpieczny/bezwzgledny.
Dlatego bezmleczny, beznabialowy i bezjajeczny sa zatrzymywane.
Wyjatki ogolne obejmuja bez ograniczen/preferencji/znaczenia/limitu czasu.
Nie stosuje sie listy wszystkich nieobslugiwanych produktow.

## Negacje i niejednoznacznosc
Nie dodano ogolnego rozpoznawania zakresu negacji. Sama wzmianka o
nieobslugiwanym wykluczeniu w negacji lub cytacie nadal blokuje zapytanie.
To celowe false positive. Komunikat prosi o doprecyzowanie i nie sugeruje
usuniecia koniecznego wykluczenia tylko po to, by uruchomic wyszukiwanie.
"Bez laktozy i szybki obiad" jest niejednoznacznym ogonem listy i tez blokuje.
To udokumentowany koszt uzytecznosci, nie nowe wymaganie jezykowe aplikacji.

## Granice i ryzyka
Nie jest to dowod obslugi wszystkich wykluczen. Parafrazy poza gramatyka
(np. "pomijaj jajka", "nie chce mleka"), literowki, obfuskacja, odmienne
jezyki, implikowane wymagania i skomplikowane negacje moga nie zostac
wykryte. Zlozenia i zakresy list nie sa ogolnie parsowane: np. konstrukcje
rozpoczete od "bezglutenowy" bez osobnego "bez" nie inicjuja analizy listy.
Te luki wymagaja oddzielnych przypadkow i dalszej decyzji o architekturze.
Nie deklarujemy niezawodnosci ani medycznego bezpieczenstwa wynikow.
Bezposrednie wywolanie backendu poza chat_with_bot omija ta warstwe.

## Weryfikacja i pomiary
13 nowych testow z subprzypadkami sprawdza wykluczenia, Unicode, listy,
negacje, priorytet alergii, brak API/backendu i brak echa tresci uzytkownika.
Regresja obejmuje wszystkie 64 dotychczasowe obslugiwane zapytania intencji:
nowa ochrona nie blokuje zadnego. Nie uruchamiano LLM ani nowego pomiaru
jakosci modelu. run_llm_eval.py nadal celowo mierzy surowy model.
