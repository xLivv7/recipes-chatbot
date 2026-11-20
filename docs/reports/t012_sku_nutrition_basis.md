# T012 — podstawa wartości odżywczych pięciu produktów Winiary

## Wdrożenie T030 z 20 listopada 2026 r.

Po wyborze wariantów receptury zapisano 42 ilości w ml w 41 przepisach PostgreSQL.
Przyjęto dotychczasowe liczby jako nowe porcje kulinarne dla czterech SKU. Przykładowo
R069 przewiduje 30 ml Sosu Czosnkowego w butelce i 500 ml gotowego bulionu na dwie porcje.
Generyczne odpowiedniki mają osobne ilości w gramach. Polecenie
`python apply_data_curation.py --volumes-only` odtwarza zaakceptowane objętości.
Ponowne wykonanie zmieniło zero wierszy.

Tabela Sosu Czosnkowego **300 ml** z importu odpowiada deklaracji dla tej butelki
(543 kcal, 1,2 g białka, 55,8 g tłuszczu i 8,8 g węglowodanów na 100 ml).
Karta producenta porównywana w pierwszym przeglądzie opisuje obecnie butelkę **200 ml**.
[Deklaracja dla 300 ml](https://dhtonline.pl/pl/p/Winiary-Sos-czosnkowy-300-ml/3625) · [Karta butelki Winiary](https://www.winiary.pl/produkty/sos-czosnkowy-winiary-w-butelce/)

W 64 kombinacjach zapytań porównano 3271 zwróconych pozycji z niezależnym rachunkiem
kcal i B/T/W na porcję z ilości recepturowych. W wynikach wystąpiły sos i oba buliony.
W M01 z atrapą modelu i rzeczywistym backendem chatbot podał dla R069 353,8 kcal,
9,9 g białka, 12 g tłuszczu i 52,4 g węglowodanów na porcję. Lista składników
i pierwszy krok wskazały ilość gotowego wywaru. Walidator bazy zgłosił
0 błędów, 16 ostrzeżeń i 9 informacji. [Dane kontroli](../../dokumentacja%20pracy/2026-11-20_t030/catalog.json)

Wariant Majonezu Wegańskiego sprawdzono oddzielnie na kontrolowanej regule z rzeczywistą
tabelą produktu. 15 ml wnosi 95,55 kcal. W obecnym katalogu jedyna reguła wyboru tego SKU
wymaga diety wegańskiej, a polityka konceptu C001 wyklucza go z tej diety przed doborem SKU.
Weryfikacja tego produktu obejmuje obsługę jego jednostki i rachunek.
[Regresja 380/380, bez wywołań API](../../dokumentacja%20pracy/2026-11-20_t030/final.json)

**Pokrycie diety wegańskiej bez osobnego wariantu R119.** Na katalogu 180 przepisów
wywołanie `get_recommendations(diet="vegan", category="", top_n=180)` z domyślnym celem
i bez dodatkowych ograniczeń zwróciło 27 różnych przepisów kwalifikowanych przez backend:
2 śniadania, 7 lunchów, 3 obiady, 6 kolacji, 6 przekąsek i 3 desery.
R119 występuje w wynikach bez filtra diety i odpada po włączeniu filtra wegańskiego.
Wśród wegańskich lunchów są m.in. R066 (tortilla z hummusem i pieczonymi warzywami)
i R077 (sałatka tabbouleh).

## Przebieg przeglądu przed T030

**Ustalenie z 20 listopada 2026 r.** Autorka zaakceptowała opis bulionu w mililitrach gotowego wywaru. Przy przyszłym przywróceniu SKU przepis ma podać sposób przygotowania według opakowania oraz objętość wywaru do odmierzenia. Obliczenia mają używać tej samej objętości i tabeli produktu po przygotowaniu. Wariant generyczny wymaga danych zgodnych z jego jednostką i postacią. Obecna implementacja receptur używa gramów.

W rozmowie o przybliżeniu dla Majonezu Wegańskiego i Sosu Czosnkowego sprawdzono ilości na porcję w PostgreSQL. Koncept majonezu C001 występuje w 21 przepisach w ilości 15–100 g na porcję, w tym w dziesięciu co najmniej 50 g. Koncept sosu C004 występuje w dziewięciu przepisach w ilości 15–50 g na porcję, w tym w czterech po 50 g. Są to gramatury składników przed doborem marki. Brak pomiaru gęstości dla tych dwóch SKU pozostawia błąd przybliżenia nieokreślony. Decyzja o wprowadzeniu tego przybliżenia jest otwarta.

**Aktualizacja 19 listopada 2026 r.** Autorka przyjęła tabelę producenta dla słoika Majonezu Dekoracyjnego 400 ml. Na 100 g przypada 704 kcal, 1,5 g białka, 76,3 g tłuszczu i 2,9 g węglowodanów. To rozstrzygnięcie dla tego konkretnego wariantu ma pierwszeństwo przed oznaczeniem „per 100 ml” w historycznym CSV. Liczby zaimportowane do PostgreSQL są już zgodne z tabelą. Przywrócono wybór SKU w istniejących regułach. Cztery pozostałe SKU są nadal czasowo pomijane. [Karta Winiary dla 400 ml](https://www.winiary.pl/produkty/majonez-dekoracyjny-winiary-400-ml/)

Na bieżącym katalogu w standardowym wyszukiwaniu bez ograniczeń wszystkie 21 przepisów z C001 użyło przywróconego produktu. Dla każdego z nich porównano kcal i B/T/W na porcję z niezależnym rachunkiem dziesiętnym (różnica poniżej 0,00000001). W M01 otrzymano pięć lunchów: R081, R065, R083, R064 i R079. Trzy z nich zawierają Majonez Dekoracyjny, R083 zawiera Sos Spaghetti, a R079 jest generyczny. Poniżej zachowano przebieg pierwotnego przeglądu.

**Przegląd z 18 listopada 2026 r.** Porównano dane źródłowe importu, karty produktów Winiary i działający katalog PostgreSQL (odczyt na wersji kodu `15dace7`). Backend mnoży cztery wartości produktu przez masę składnika w gramach podzieloną przez 100. Żeby uzasadnić ten rachunek, wartości muszą odnosić się do 100 g składnika w postaci wskazanej w recepturze.

| SKU | Katalog · kcal / B / T / W na źródłowe 100 ml | Wynik przeglądu |
| --- | --- | --- |
| `WINIARY_MAJONEZ_DEKORACYJNY_400ML` | 704 / 1,5 / 76,3 / 2,9 | Karta słoika 400 ml przypisuje te liczby do 100 g. Winiary podaje jednak również 704 kcal na 100 ml, a katalog importu opisuje wszystkie cztery liczby jako wartości na 100 ml. Potrzebna jest etykieta tego wariantu lub potwierdzenie producenta wyjaśniające rozbieżność. [Karta 400 ml](https://www.winiary.pl/produkty/majonez-dekoracyjny-winiary-400-ml/) · [Porównanie Winiary](https://www.winiary.pl/majonez-dekoracyjny/) |
| `WINIARY_MAJONEZ_WEGANSKI_300ML` | 637 / 0,4 / 68,4 / 4,6 | Karta produktu podaje wartości na 100 ml. Do przeliczenia potrzebna jest masa netto znanej objętości tego majonezu albo tabela na 100 g. [Karta Winiary](https://www.winiary.pl/produkty/majonez-weganski-winiary/) |
| `WINIARY_SOS_CZOSNKOWY_BUTELKA_300ML` | 543 / 1,2 / 55,8 / 8,8 | Karta butelki podaje wartości na 100 ml. Występuje też różnica składu odżywczego względem importu (52,6 g tłuszczu i 8,6 g węglowodanów w karcie). Tabela i ewentualny pomiar masy muszą dotyczyć tej samej wersji produktu. [Karta butelki Winiary](https://www.winiary.pl/produkty/sos-czosnkowy-winiary-w-butelce/) |
| `WINIARY_BULION_DROBIOWY_160G` | 6 / 0,2 / 0,3 / 0,5 | Wartości dotyczą 100 ml gotowego wywaru. Słoik zawiera 160 g pasty. Dawkowanie 45 g na litr wody określa sposób przygotowania. Brakuje masy znanej objętości gotowego wywaru. [Bulion drobiowy Winiary](https://www.winiary.pl/produkty/bulion-drobiowy-winiary/) |
| `WINIARY_BULION_WARZYWNY_SLOIK_160G` | 4 / 0,2 / 0,1 / 0,6 | Ta sama podstawa po przygotowaniu i dawkowanie jak dla wariantu drobiowego. Potrzebna jest wartość na 100 g lub pomiar gotowego wywaru warzywnego. [Bulion warzywny Winiary](https://www.winiary.pl/produkty/bulion-warzywny-w-sloiku-winiary/) |

## Wpływ na przepisy

Odczyt w transakcji tylko do odczytu potwierdził wartości wszystkich pięciu rekordów w `client_skus` oraz siedem wskazujących je reguł. W 180 przepisach majonez C001 występuje 21 razy, sos C004 dziewięć razy, bulion C007 dwanaście razy. Łącznie to **41 różnych przepisów**. R069 zawiera sos i bulion. Faktyczny dobór SKU zależy także od diety, celu i ograniczeń.

W przepisach na bulion przewidziano od 200 do 1000 g składnika C007. Na przykład w R045 kucharz dodaje 500 g bulionu chochlami, a w R080 podgrzewa 1000 g bulionu przed dodaniem warzyw. Ilości opisują gotowy wywar. Samo przeliczenie makro pasty w słoiku na 100 g nie rozwiązuje problemu. Również nazwa i gramatura w odpowiedzi muszą dotyczyć tej samej postaci.

Symulacja w kopii katalogu w pamięci pominęła siedem reguł tych SKU. Backend dla parametrów M01 (pięć lunchów) zwrócił przed zmianą R069, R081, R078, R065 i R062, wszystkie z produktem marki. Po symulowanej zmianie zwrócił R083 i R072 z jednym SKU każdy oraz trzy lunche generyczne (R079, R078 i R076). R069 po osobnym przygotowaniu zmienił się z 353,75 na 309,30 kcal na porcję po zastąpieniu obu produktów składnikami generycznymi. To porównanie wpływu reguł na ranking i dane wyjściowe. Wykonano je bez wywołania modelu i bez zapisu do katalogu.

## DEC-04 — decyzja autorki i działanie MVP

18 listopada 2026 r. autorka zatwierdziła czasowe pominięcie wszystkich pięciu SKU i przejęła sprawdzenie produktów. T012 zakończono dla obecnego zakresu MVP. W PostgreSQL zachowano rekordy, ich liczby i reguły. Lista `SKUS_PENDING_NUTRITION_REVIEW` w [module rekomendacji](../../core/recommendations.py) obowiązuje także po odtworzeniu bazy. Gdy pasująca reguła wskazuje produkt z listy, silnik przechodzi do wariantu generycznego. Dzięki temu np. reguła bulionu dla wegan nie prowadzi do domyślnego bulionu drobiowego.

Generyczny majonez C001 ma w katalogu flagę `is_vegan_ok=0`. Przy C004 i C007 podstawowe flagi diety dopuszczały kombinacje sprzeczne z zatwierdzonym opisem generycznego składnika. Dla wariantu generycznego wykluczono C004 (sos z nabiałem) z diety wegańskiej i C007 (wywar mięsno-warzywny) z diet wegańskiej, wegetariańskiej i pescetariańskiej. W takim przypadku aplikacja pomija przepis. Obowiązują też dotychczasowe filtry glutenu i laktozy. [Definicje składników](../../curation/lactose_concept_policy.csv) · [Polityka wariantów generycznych](../../core/recommendation_catalog.py)

### Sprawdzenie po wdrożeniu

- Na lokalnym PostgreSQL wykonano 64 kombinacje czterech diet, czterech celów i czterech zestawów ograniczeń. W 3231 zwróconych pozycjach (łącznie z powtórzeniami przepisów) sprawdzono przypisania SKU i zgodność składników z dietą oraz ograniczeniami. Wystąpiło 41 różnych przepisów z badanymi konceptami. Dla każdej pozycji cztery wartości na porcję porównano z niezależnym rachunkiem dziesiętnym na finalnych składnikach. Różnica była mniejsza niż 0,00000001 w jednostce pola. [Wynik kontroli katalogu](../../dokumentacja%20pracy/2026-11-18_t012/catalog.json)
- Backend i renderer sprawdzono na parametrach M01–M08. Długości list wyniosły kolejno 5, 5, 2, 2, 2, 2, 5 i 0. W M01 produkty marki wystąpiły w R083 (Sos Spaghetti) i R072 (Sos Amerykański BBQ). Trzy kolejne lunche były generyczne. W R069 cztery wartości na porcję to 309,30 kcal, 12,004 g białka, 5,883 g tłuszczu i 53,848 g węglowodanów. Przykładowe ID w zamrożonym materiale T010 odnoszą się do wcześniejszego katalogu. Pełna demonstracja i ocena odpowiedzi przez autorkę pozostają w T013.
- Pełna regresja przeszła **376/376**, bez pominięć. Liczba wywołań API i zapisów w PostgreSQL wyniosła zero. [Raport regresji](../../dokumentacja%20pracy/2026-11-18_t012/full.json)

### Przywrócenie pojedynczego SKU

Przy zachowaniu produktu można użyć etykiety na 100 g lub udokumentować masę znanej objętości oraz zgodną tabelę na 100 ml. Jeśli 100 ml właściwej postaci waży *m* gramów, każdą z czterech wartości na 100 ml mnożymy przez *100 / m*. Pomiar powinien identyfikować wariant i postać produktu. Przy bulionach potrzebne jest też jednoznaczne oznaczenie gotowego wywaru w odpowiedzi.

Po zweryfikowaniu źródła zapisać wartości na 100 g właściwej postaci oraz sposób odtworzenia danych. Zdjąć z listy właściwy identyfikator i sprawdzić dobór, ograniczenia, makro na porcję oraz nazwę i gramaturę w odpowiedzi. Dla bulionu sprawdzić też regułę domyślną przy diecie pescetariańskiej, aby wykluczała bulion drobiowy.
