# Kontrakt lactose_free i audyt danych

Status: decyzja projektowa do implementacji. Data audytu: 2026-10-01.
Aktualizacja: dodano nullable kolumny i import polityk; filtrowanie oraz
obsluga parametru lactose_free pozostaja do wdrozenia. Fragmenty audytu
ponizej opisuja stan z dnia poprzedzajacego import.
Obecny backend obsluguje tylko gluten_free. Ten dokument nie aktywuje
nowego ograniczenia ani nie nadaje flag rekordom.

## Znaczenie

`restrictions = ["lactose_free"]` oznacza wybor skladnikow i SKU jawnie
zakwalifikowanych jako zgodne z polityka bez laktozy w katalogu projektu.
Nie oznacza diety weganskiej, wykluczenia nabialu ani wykluczenia bialek mleka.
Nie jest deklaracja klinicznej tolerancji, certyfikacji ani zerowej zawartosci
laktozy potwierdzonej pomiarem. Nie wyznaczamy progu gramow laktozy: baza
nie zawiera takiego pomiaru, a weglowodany nie sa jego zamiennikiem.

Rozroznienie nietolerancji laktozy i alergii na bialka mleka:
https://www.niddk.nih.gov/health-information/digestive-diseases/lactose-intolerance/symptoms-causes
Produkty lactose-free i lactose-reduced oraz ograniczenia tolerancji:
https://www.niddk.nih.gov/health-information/digestive-diseases/lactose-intolerance/eating-diet-nutrition

## Parametry i interpretacja

- Nowy token: lactose_free w restrictions; niezalezny od diet,
  protein_preference, nutrition_goal, category i time_max.
- Kombinacja gluten_free + lactose_free wymaga spelnienia OBU polityk dla
  kazdego skladnika i kazdego uzytego SKU.
- Brak ograniczenia nie wlacza filtrowania laktozy.
- "bez laktozy", "bezlaktozowy", jawna nietolerancja laktozy: lactose_free.
- "nie musi byc bez laktozy": nie dodawac ograniczenia.
- "bez nabialu", "bez mleka", "alergia na mleko": nie zamieniac na
  lactose_free ani vegan. To odrebne, nieobslugiwane potrzeby; wymagaja
  doprecyzowania/komunikatu o zakresie obslugi w pozniejszej warstwie rozmowy.
- "vegan" nie dodaje automatycznie lactose_free; oba warunki moga byc
  jawnie polaczone. Mleko bez laktozy pozostaje niedozwolone dla vegan.

## Polityka rekordow i dowody

Planowane pole `is_lactose_free` w diet_policies oraz client_skus:

| Wartosc | Znaczenie | Zachowanie dla lactose_free |
| --- | --- | --- |
| 1 | jawnie dopuszczony w udokumentowanej klasyfikacji | dopuszczenie |
| 0 | niezgodny z polityka | odrzucenie |
| NULL / brak rekordu | niezweryfikowany | odrzucenie |

Nie stosowac default=1 ani reguly "nie ma na liscie zakazanych, wiec 1".
Kazdy rekord wymaga jawnego wiersza klasyfikacji. Pliki curation powinny
zawierac ID, status, uzasadnienie, zrodlo, date przegladu. NULL jest legalnym
stanem oczekiwania, a nie dowodem zgodnosci. Walidator ma odrzucac wartosci
inne niz 0/1/NULL i zglaszac niezweryfikowane pozycje uzywane w przepisach.

Koncepty proste mozna kwalifikowac po zweryfikowaniu ich definicji. Produkty
zlozone wymagaja skladu lub deklaracji konkretnego wariantu. Nie wyprowadzac
flagi z vegan, low-carb, keto, fermentacji ani samej nazwy sera. Niska
zawartosc laktozy nie jest rownoznaczna z przyjeta polityka bez laktozy.

Dla SKU potrzebny jest pelny sklad/deklaracja producenta zgodna z wariantem
i opakowaniem. Skrocony sklad i brak alergenu mleko nie wystarczaja.
Deklaracja mleka wymaga rozroznienia bialek mleka i laktozy; produkt jawnie
bez laktozy moze zawierac mleko. `may_contain` nie stanowi pomiaru laktozy;
w MVP wzmianka mleka bez wyjasnienia pozostawia status niezweryfikowany.

## Filtrowanie i SKU

### Przeglad reczny 2026-10-01

Przyjeto definicje receptur konceptow z klasyfikacji wlascicielki katalogu.
To nie gwarancja skladu dowolnego produktu sklepowego. C108 oznacza tylko
Parmigiano Reggiano DOP, C109 Grana Padano DOP; zrodla zapisano w CSV.
C104 pozostaje NULL. Stan klasyfikacji: 327 dopuszczonych, 48 wykluczonych,
1 niezweryfikowany. Nie zaimportowano tych decyzji do bazy.

GIS zaleca 0.01% jako granice oznaczalnosci metody referencyjnej; nie jest
to jednolity ustawowy prog UE. Tolerancja 12 g opisana przez EFSA nie
kwalifikuje produktu jako bezlaktozowego. Nie deklarujemy pomiarow, ktorych
nie posiadamy, ani nie utozsamiamy galaktozy z laktoza.
https://www.gov.pl/web/gis/znakowanie-srodkow-spozywczych-komunikatem-bez-laktozy
https://www.efsa.europa.eu/en/efsajournal/pub/1777

Na poczatek zachowac aktualny model: najpierw dopuszczenie konceptow,
potem wybor SKU. Kazdy koncept musi miec 1. Kazdy wybrany SKU tez musi miec
1 dla wszystkich aktywnych restrictions. Zgodnosc konceptu nie zatwierdza SKU.
Nie szukac automatycznie zamiennika mleka, jogurtu czy sera.

Niezgodny SKU jest pomijany; mozna wybrac kolejny SKU wedlug istniejacych
regul. Gdy brak zgodnego SKU, pozostaje generyczny koncept tylko jesli sam
jest dopuszczony. Generyczne mleko nie moze zostac uratowane przez SKU bez
laktozy na tym etapie. Makro i used_skus musza odzwierciedlac finalny wybor.
Brak zgodnych przepisow zwraca pusta liste, bez rozluzniania ograniczen.

## Audyt katalogu

Odczytano PostgreSQL bez zapisu: 376 konceptow, 20 SKU, 180 przepisow.
Zrodlowy ingredient_concepts.csv ma 47 rekordow: 329 konceptow nie ma
w tym pliku metadanych kategorii/alergenow. Wszystkie 376 konceptow i 20 SKU
sa obecnie niezakwalifikowane dla lactose_free, bo pole jeszcze nie istnieje.

| Grupa | ID | Decyzja przygotowawcza |
| --- | --- | --- |
| Nabial generyczny | C015-C019; C091-C093; C095-C123 | 37 pozycji do indywidualnego przegladu; nie dopuszczac automatycznie |
| Mleko bez laktozy | C094 | kandydat do 1 po potwierdzeniu definicji/zrodla; nie vegan |
| Produkty zlozone | C001-C009, C090, C143-C151, C292, C300, C315-C318, C324-C327, C339-C342 | przeglad receptury; nazwa nie rozstrzyga skladu |
| Alternatywy roslinne | C304-C309 | kandydaci do dopuszczenia po przegladzie; nie zatwierdzac calego zakresu automatycznie |
| Pozostale koncepty | pozostale ID z C001-C376 | jawna klasyfikacja definicji; brak na powyzszej liscie nie oznacza 1 |

37 konceptow nabialowych wystepuje w 89 ze 180 przepisow. To liczba
przepisow wymagajacych uwagi, nie prognoza liczby odrzuconych wynikow.
C094 wystepuje w 0 przepisach: sam dostepny koncept nie zapewnia pokrycia
przepisow z nabialem bez laktozy. Sery dojrzewajace i ghee wymagaja osobnego
potwierdzenia; nie uznawac ich za zgodne tylko na podstawie typu produktu.

## Audyt wszystkich SKU

Zrodlo lokalne: data/raw/clients/Winiary/client_skus_canonical.csv.
20/20 rekordow ma ingredients_pl_short i source_url, ale bez daty weryfikacji,
ilosci laktozy i deklaracji lactose-free. Zrodla to w wiekszosci sprzedawcy;
jedyny URL winiary.pl w CSV dotyczy sosu BBQ. Nie odwiedzano tych URL ani
nie potwierdzano aktualnych receptur. Wszystkie SKU pozostaja pending.

| Grupa | Liczba wariantow | Kolejny krok |
| --- | --- | --- |
| Majonez Dekoracyjny 250/400/700 ml | 3 | pelny sklad kazdego wariantu |
| Majonez Salatkowy, Lekki, Delikatny, Weganski, Omega 3:6 | 5 | pelny sklad; nazwa weganski nie zastapi dowodu |
| Ketchup Lagodny, Pikantny, Bez dodatku cukru | 3 | aktualne deklaracje producenta |
| Sos czosnkowy sloik/butelka | 2 | szczegolnie sprawdzic skladniki mleczne |
| Sos BBQ, Spaghetti, Bolonski | 3 | pelne sklady konkretnych wariantow |
| Bulion drobiowy, warzywny, wolowy, grzybowy | 4 | rozwinac skrot "baza/aromaty" i zweryfikowac deklaracje |

Dodatkowe zastane ryzyko: czesc SKU ma makro per 100 ml lub po przygotowaniu,
a runtime liczy po gramach. To osobny problem kontraktu odzywczego;
wdrozenie lactose_free nie powinno go maskowac ani poszerzac zakresu prac.

## Kolejnosc wdrozenia i kryteria akceptacji

### Migracja i import 2026-10-01

DietPolicy oraz ClientSku maja nullable Integer is_lactose_free bez default.
apply_data_curation.py --lactose-only tworzy brakujace kolumny i importuje
obie polityki w jednej transakcji danych. Migracja DDL jest osobna transakcja.
Import wymaga dokladnego pokrycia ingredients, diet_policies i SKU Winiary;
duplikaty, nieznane/brakujace ID i wartosci inne niz puste/0/1 sa bledami.
Nie tworzy rekordow i nie zmienia innych flag. Powtorzenie jest idempotentne.
Pelny apply_curation() rowniez obejmuje te polityki przy odbudowie bazy.
Nie aktywowano filtrowania, normalizacji parametrow ani deklaracji LLM.

### Aktualizacja przegladu SKU 2026-10-01

Przeglad publicznych skladow producenta zapisano w
curation/winiary_sku_lactose_policy.csv: 8 dopuszczonych, 12 NULL, 0
potwierdzonych wykluczen. Wczesniejszy audyt powyzej opisuje stan raw
przed przegladem. Nie zmieniono raw ani bazy. Dopuszczenie wynika z
pelnego skladu bez skladnikow mlecznych i dopasowania wariantu, nie
pomiaru poziomu laktozy. Kolejka i ograniczenia dowodow sa opisane w
curation/lactose_sku_manual_review.md. Deklaracje may_contain milk
pozostaja NULL; nowsze opakowania nie zatwierdzaja starszych SKU.

1. Jawne pliki klasyfikacji dla wszystkich ID; nieznane pozostaja NULL.
2. Migracja nullable flag bez automatycznego dopuszczania; idempotentny import.
3. Loader, filtr konceptow i SKU, walidator, testy jednostkowe/integracyjne.
4. Tool enum i maxItems dla dwoch ograniczen; normalizacja i intent eval.
5. Final-answer eval: brak gwarancji medycznych, brak zamiennikow z LLM.

Testy musza obejmowac mleko zwykle vs C094, C094 + vegan, NULL/0/brak polityki,
obie restrictions naraz, zgodny koncept + niezgodny SKU, fallback generyczny,
brak wynikow i powtarzalny import. Testy nie moga wymagac wynikow dla kategorii,
w ktorej sklasyfikowany katalog faktycznie nie ma zgodnych przepisow.
