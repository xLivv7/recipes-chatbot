# Ochrona nieobslugiwanych wykluczen

Status: wdrozona ochrona leksykalna w chat_with_bot, 2026-10-15;
gramatyka poprawiona w T024, 2026-11-17 (PFL-01–07).
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
| nie musi byc bez jaj, chce kolacje | przekazanie do LLM: lokalne zniesienie wymogu |
| nie musi byc bez glutenu | przekazanie do LLM: dotychczasowa negacja |
| bez laktozy i szybki obiad | przekazanie do LLM: nowa klauzula posilku |
| bez miesa, ryby moga byc / chce danie z ryba / nie musi byc z ryba | przekazanie do LLM; preflight nie ustala diety ani bialka |
| nie musi byc bez jaj, ale bez mleka | zatrzymanie dodatniego wymogu bez mleka |
| nie musi byc bez jaj i mleka | zatrzymanie niejednoznacznej listy |

Brak blokady oznacza jedynie przejscie do interpretacji, nie gwarantuje
poprawnego wyboru parametrow przez model. Bez mleka/nabialu nie jest
lactose_free. Jawnego "bez jaj" nie redukujemy do vegan, nawet jesli przy
poprawnej interpretacji diety skladnik bylby juz wykluczony.

## Mechanizm
`mentions_unsupported_exclusion` normalizuje wielkosc liter, polskie znaki
(w tym l) i Unicode. Analizuje ograniczona gramatyke po slowach: bez,
wykluczam, wyklucz, unikam, nie jem, nie spozywam, nie moge jesc/spozywac,
z wykluczeniem/wylaczeniem oraz without, bez tlumaczenia nazw.
Nazwy w tej gramatyce inne niz glutenu/laktozy/miesa sa odrzucane; ryb
wymaga rownoczesnego wykluczenia miesa. Rozpoznaje forme produktow miesnych.
Listy moga uzywac i/oraz/ani/lub/albo, symboli / + & i przecinka. Nowa klauzula
po przecinku moze zaczynac sie m.in. ale, prosze, podaj, chce lub nazwa posilku.
Kazde osobne "bez" jest sprawdzane, wiec drugi filtr nie maskuje pierwszego.

T024 rozpoznaje tez poczatki "ryby moga byc", "ryby sa dozwolone" oraz
"nie musi/musza byc z ...". Samo "ryby" lub "nie" nie konczy listy.
Po i/oraz nowa klauzula wymaga rozpoznanej nazwy posilku albo pary
szybki/szybka/szybkie lub ekspresowy/ekspresowa/ekspresowe z ta nazwa.
Samo "na" lub "do" nie konczy listy: "i na pewno mleka" oraz
"oraz do tego jaj" nadal blokuja nieobslugiwane wykluczenie.
Nie obsluguje to dowolnego przymiotnika lub kazdej parafrazy zdania.
Nowa klauzula nie wylacza sprawdzania nastepnych jawnych wykluczen.

Zlozenia zaczynajace sie od bez sa konserwatywnie odrzucane poza rodzinami
bezglutenowy/bezlaktozowy oraz niebedacymi wykluczeniem bezpieczny/bezwzgledny.
Dlatego bezmleczny, beznabialowy i bezjajeczny sa zatrzymywane.
Wyjatki ogolne obejmuja bez ograniczen/preferencji/znaczenia/limitu czasu.
Nie stosuje sie listy wszystkich nieobslugiwanych produktow.

## Negacje i niejednoznacznosc
Nie dodano ogolnego rozpoznawania zakresu negacji. Wyjatek T024 obejmuje
bezposrednie "nie musi/musza byc bez ...": znosi wymog jednego elementu
(takze formy produktow miesnych). Nie dodaje zadnego filtra. Kolejne
samodzielne wykluczenie jest nadal sprawdzane; niejednoznaczna lista
nieobslugiwanych elementow pozostaje blokowana. "Nie wymagam dania bez
orzechow" i "nie unikam mleka" nadal sa poza rozpoznawana gramatyka.
Wiadomosci ze znakami cytowania nie korzystaja z wyjatku lokalnej negacji;
nie interpretujemy zakresu cytatow. Nie dotyczy to ochrony alergii:
jej pierwszenstwo i rozpoznawanie wzmianek, takze zanegowanych, sa bez zmian.

Przed T024 piec znanych przypadkow bylo falszywie blokowanych. Historyczne
raporty T021/T023 zachowuja tamten wynik. Po T024 przechodza preflight;
to nie dowod, ze model wywola narzedzie lub dobierze poprawne argumenty.

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
Pierwotne wdrozenie mialo 13 nowych testow z subprzypadkami. T024 dodalo
12 kolejnych: gramatyke bez SDK/bazy, przeplyw application z atrapami,
priorytet alergii i odroznienie audytu preflight od oceny modelu.
Pelna regresja po T024: 314/314, bez pominiec, z generacja SDK i zapisami
katalogu zablokowanymi. Wszystkie 64 dotychczasowe obslugiwane zapytania
intencji nadal przechodza preflight. Osobne kontrole pokazuja, ze po
odblokowaniu pieciu zapytan poprawny call wykonuje jeden dispatch,
a bledny brak calla pozostaje porazka decyzji, bez backendu.
Nie uruchamiano LLM ani nowego pomiaru jakosci modelu. Surowe wyniki
historyczne i etykiety pozostaja bez zmian; run_llm_eval.py nadal mierzy
surowy model. Dowody: [mapa weryfikacji](../../../specs/001-mvp-stabilization/verification.md#t024--poprawa-preflight-zakończona).
