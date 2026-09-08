# Slowniki kontrolowane

[Powrot do indeksu](../data_contract.md)

Slowniki kontrolowane ograniczaja dryf danych, np. mieszanie wartosci `vegan`, `weganskie`, `plant_based`.

## Dieta uzytkownika: `diet`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie | Uwagi |
| --- | --- | --- |
| `none` | brak preferencji dietetycznej | wartosc domyslna |
| `vegetarian` | dieta wegetarianska | bez miesa i ryb |
| `vegan` | dieta weganska | bez produktow odzwierzecych |
| `pescetarian` | dieta pescetarianska | ryby dozwolone, mieso niedozwolone |

## Preferowane zrodlo bialka: `protein_preference`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie | Uwagi |
| --- | --- | --- |
| `none` | brak wymaganego zrodla bialka | wartosc domyslna |
| `meat` | uzytkownik chce danie miesne | przepis musi zawierac skladnik z `is_meat = 1` |
| `fish` | uzytkownik chce danie rybne | przepis musi zawierac skladnik z `is_fish = 1` |

`diet` i `protein_preference` sa niezaleznymi wymiarami, ale sprzeczne kombinacje sa odrzucane. Diety `vegetarian` i `vegan` nie moga byc laczone z `meat` ani `fish`, a `pescetarian` nie moze byc laczone z `meat`.

## Dodatkowe ograniczenia: `restrictions`

Pole jest lista niezaleznych ograniczen zywieniowych. W obecnym etapie lista obslugiwanych wartosci jest pusta, dlatego poprawna wartosc to `[]`.

Pierwsza planowana wartosc to `gluten_free`. Nie wolno jej jeszcze przekazywac do runtime przed uzupelnieniem kontraktu danych, flag skladnikow, walidacji i testow.

## Cel zywieniowy: `nutrition_goal`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie |
| --- | --- |
| `standard` | brak specjalnego celu |
| `low_kcal` | preferencja nizszej kalorycznosci |
| `high_protein` | preferencja wyzszej zawartosci bialka |
| `keto` | preferencja niskoweglowodanowa |

Uwagi:

- Slownik `nutrition_goal` dotyczy obecnego tool callingu i filtrowania runtime.
- Reguly SKU moga zawierac przyszlosciowe wartosci biznesowe, np. `no_sugar`, ktore nie sa jeszcze obslugiwane przez tool calling. Sama obecnosc takiej wartosci nie jest bledem walidacji bazy.

## Kategoria posilku: `category`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie |
| --- | --- |
| `śniadanie` | sniadanie |
| `obiad` | obiad |
| `lunch` | lunch |
| `kolacja` | kolacja |
| `deser` | deser |
| `przekąska` | przekaska |

Obecny kod domyslnie uzywa `kolacja`. Walidator powinien sprawdzac, czy kategorie przepisow naleza do slownika.

## Typ dania: `dish_type`

`dish_type` sluzy do roznicowania wynikow, aby chatbot nie zwracal kilku podobnych dan.

To pole nie ma sztywnego slownika dozwolonych wartosci. Jest czescia opisu przepisu i moze byc generowane swobodnie, np. `Kanapka`, `Soup`, `Pudding`, `Danie glowne`, `Sałatka`.

Walidator powinien sprawdzac tylko, czy `dish_type` jest niepustym tekstem.

## Kategoria skladnika: `ingredient.category`

Kategorie obecne w pliku `data/raw/ingredient_concepts.csv`:

- `sauce`
- `spice`
- `fat`
- `dairy`
- `protein`
- `carb`
- `veg`
- `other`

Uwaga: obecny model SQLAlchemy tabeli `ingredients` przechowuje tylko `id` i `name_pl`. Kategorie, synonimy i alergeny sa obecne w CSV, ale nie sa jeszcze przenoszone do bazy.

## Typ warunku reguly SKU: `condition_type`

Dozwolone wartosci:

| Wartosc | Znaczenie |
| --- | --- |
| `user_pref` | regula zalezy od preferencji dietetycznej |
| `diet` | regula zalezy od diety uzytkownika |
| `protein_preference` | regula zalezy od oczekiwanego zrodla bialka |
| `restriction` | regula zalezy od elementu listy dodatkowych ograniczen |
| `nutrition_goal` | regula zalezy od celu zywieniowego |
| `default` | fallback dla danego konceptu |

Dla `condition_type = default` dozwolona wartosc `condition_value` to `any`.

Dla warunkow innych niz `default` pole `condition_value` musi byc niepuste, ale nie jest zamknietym enumem na poziomie walidacji bazy. Pozwala to przechowywac przyszlosciowe reguly, ktore obecny runtime moze jeszcze ignorowac.

`user_pref` jest tolerowane w bazie tylko jako przejsciowy typ starszych, przyszlosciowych regul. Aktywne reguly dla obslugiwanych diet i zrodel bialka powinny zostac przeniesione odpowiednio do `diet` albo `protein_preference` przez `apply_data_curation.py`.

## Typ dopasowania SKU do konceptu: `match_type`

Dozwolone wartosci w mapowaniu SKU na koncept:

| Wartosc | Znaczenie |
| --- | --- |
| `exact` | produkt jest bezposrednim odpowiednikiem konceptu |
| `close` | produkt jest bliskim zamiennikiem konceptu |
| `substitute` | produkt moze byc zamiennikiem, ale wymaga ostroznej reguly |

W MVP rekomendowane jest uzywanie `exact` i `close`. `substitute` powinno byc traktowane ostroznie, szczegolnie dla diet i alergenow.

## Poziomy walidacji

| Poziom | Znaczenie |
| --- | --- |
| `ERROR` | blad blokujacy poprawne dzialanie systemu |
| `WARNING` | problem jakosciowy lub ryzyko, ale system moze dzialac |
| `INFO` | informacja diagnostyczna/statystyczna |
