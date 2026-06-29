# Slowniki kontrolowane

[Powrot do indeksu](../data_contract.md)

Slowniki kontrolowane ograniczaja dryf danych, np. mieszanie wartosci `vegan`, `weganskie`, `plant_based`.

## Preferencja dietetyczna uzytkownika: `user_pref`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie | Uwagi |
| --- | --- | --- |
| `none` | brak preferencji dietetycznej | wartosc domyslna |
| `vegetarian` | dieta wegetarianska | bez miesa i ryb |
| `vegan` | dieta weganska | bez produktow odzwierzecych |
| `meat` | uzytkownik chce danie miesne | przepis musi zawierac skladnik z `is_meat = 1` |
| `fish` | uzytkownik chce danie rybne | przepis musi zawierac skladnik z `is_fish = 1` |
| `pescetarian` | dieta pescetarianska | ryby dozwolone, mieso niedozwolone |

Wartosc `vege` moze byc tolerowana jako alias wejsciowy, ale powinna byc normalizowana do `vegetarian`.

## Cel zywieniowy: `nutrition_goal`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie |
| --- | --- |
| `standard` | brak specjalnego celu |
| `low_kcal` | preferencja nizszej kalorycznosci |
| `high_protein` | preferencja wyzszej zawartosci bialka |
| `keto` | preferencja niskoweglowodanowa |

Uwagi:

- W danych SKU pojawia sie wartosc `no_sugar`, ale nie wystepuje obecnie w definicji narzedzia LLM. Dla MVP powinna byc traktowana jako ostrzezenie walidatora albo przeniesiona do osobnego slownika.
- Wartosc `spicy` z regul SKU nie jest celem zywieniowym. Jesli ma zostac utrzymana, powinna trafic do osobnego slownika, np. `taste_pref`.

## Kategoria posilku: `category`

Dozwolone wartosci dla MVP:

| Wartosc | Znaczenie |
| --- | --- |
| `śniadanie` | sniadanie |
| `obiad` | obiad |
| `kolacja` | kolacja |
| `deser` | deser |
| `przekąska` | przekaska |

Obecny kod domyslnie uzywa `kolacja`. Walidator powinien sprawdzac, czy kategorie przepisow naleza do slownika.

## Typ dania: `dish_type`

`dish_type` sluzy do roznicowania wynikow, aby chatbot nie zwracal kilku podobnych dan.

Docelowo wartosci powinny byc ujednolicone do jednego stylu, np. `snake_case`:

- `pasta`
- `salad`
- `wrap`
- `bowl`
- `stew`
- `casserole`
- `omelette`
- `baked_potatoes`
- `chicken_dish`
- `other`

Obecne dane zawieraja wartosci angielskie i mieszane, np. `Pasta`, `Salad`, `Wrap`, `Baked potatoes`. Dla MVP mozna je tolerowac, ale walidator powinien zglaszac ostrzezenie o wartosciach spoza docelowego slownika.

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
| `nutrition_goal` | regula zalezy od celu zywieniowego |
| `default` | fallback dla danego konceptu |

Dla `condition_type = default` dozwolona wartosc `condition_value` to `any`.

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
