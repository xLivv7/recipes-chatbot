# Kryteria walidatorow

[Powrot do indeksu](../data_contract.md)

Ten plik jest robocza checklista dla implementacji `validate_db.py`. Jesli trzeba cos znalezc podczas pisania walidatora, zaczynaj tutaj.

## Format problemu

Rekomendowany format pojedynczego problemu:

```text
ERROR | recipes | R004 | ingredients_data[2].concept_id | Concept C999 does not exist in ingredients.
WARNING | sku_selection_rules | rule_id=12 | condition_value | Value spicy is not allowed for condition_type user_pref in MVP.
INFO | client_skus | WINIARY_MAJONEZ_LEKKI_300ML | concept_id | SKU maps to brandable concept C001.
```

## Minimalny raport

Walidator powinien zwracac:

- liczbe rekordow w kazdej tabeli,
- liczbe bledow `ERROR`,
- liczbe ostrzezen `WARNING`,
- liste problemow z identyfikatorem rekordu,
- podsumowanie pokrycia brandyfikacji,
- podsumowanie brakow danych odzywczych,
- podsumowanie wartosci spoza slownikow.

## Etap 2A: walidatory relacyjne

Te kryteria warto zaimplementowac jako pierwsze.

| Sprawdzenie | Poziom |
| --- | --- |
| `nutrients.ingredient_id` istnieje w `ingredients.id` | `ERROR` |
| `diet_policies.ingredient_id` istnieje w `ingredients.id` | `ERROR` |
| `client_skus.client_id` istnieje w `clients.id` | `ERROR` |
| `client_skus.concept_id` istnieje w `ingredients.id` | `ERROR` |
| `sku_selection_rules.client_id` istnieje w `clients.id` | `ERROR` |
| `sku_selection_rules.concept_id` istnieje w `ingredients.id` | `ERROR` |
| `sku_selection_rules.preferred_sku_id` istnieje w `client_skus.id` | `ERROR` |
| `recipes.ingredients_data[].concept_id` istnieje w `ingredients.id` | `ERROR` |

## Etap 2B: walidatory JSONB przepisow

| Sprawdzenie | Poziom |
| --- | --- |
| `ingredients_data` jest lista | `ERROR` |
| `ingredients_data` nie jest pusta | `ERROR` |
| kazdy element `ingredients_data` jest obiektem | `ERROR` |
| kazdy element ma `concept_id` | `ERROR` |
| kazdy element ma `grams` | `ERROR` |
| `grams` jest liczba dodatnia | `ERROR` |
| `steps_pl` jest niepusta lista tekstow | `ERROR` |

## Etap 2C: walidatory slownikow

| Sprawdzenie | Poziom |
| --- | --- |
| `recipes.category` nalezy do slownika | `ERROR` |
| `recipes.dish_type` nalezy do slownika | `WARNING` |
| `sku_selection_rules.condition_type` nalezy do slownika | `ERROR` |
| `sku_selection_rules.condition_value` pasuje do typu warunku | `ERROR` |
| `ingredient.category` z CSV nalezy do slownika | `WARNING` |
| `sku_to_concept_map.match_type` nalezy do slownika | `ERROR` |

## Etap 2D: walidatory dietetyczne

| Sprawdzenie | Poziom |
| --- | --- |
| flagi dietetyczne maja wartosci `0` albo `1` | `ERROR` |
| `is_vegan_ok = 1` implikuje `is_vegetarian_ok = 1` | `ERROR` |
| mieso nie moze byc wegetarianskie ani weganskie | `ERROR` |
| ryba nie moze byc wegetarianska ani weganska | `ERROR` |
| skladnik uzyty w przepisie ma polityke dietetyczna | `WARNING` teraz, docelowo `ERROR` |
| SKU dla reguly `user_pref = vegan` nie moze byc jawnie nieweganskie | `WARNING` teraz, docelowo `ERROR` |

## Etap 2E: walidatory wartosci odzywczych

| Sprawdzenie | Poziom |
| --- | --- |
| wartosci kcal i makro sa liczbami | `ERROR` |
| wartosci kcal i makro sa nieujemne | `ERROR` |
| skladnik uzyty w przepisie ma dane odzywcze albo SKU | `ERROR` |
| SKU uzyte w regule ma kompletne dane odzywcze | `ERROR` |
| kcal sa orientacyjnie zgodne z makro | `WARNING` |
| suma makro nie przekracza sensownego zakresu | `WARNING` |
| `nutrition_basis` SKU jest zgodne z zalozeniem przeliczania | `WARNING` |

## Etap 2F: walidatory brandyfikacji

| Sprawdzenie | Poziom |
| --- | --- |
| SKU z reguly nalezy do tego samego klienta co regula | `ERROR` |
| SKU z reguly mapuje sie na koncept reguly | `ERROR` |
| kazdy brandowalny koncept ma fallback `default` | `WARNING` |
| regula dla `vegan` nie wskazuje produktu nieweganskiego | `ERROR` |
| SKU z katalogu klienta nieuzyte w zadnej regule jest raportowane | `INFO` lub `WARNING` |
| koncept uzywany w przepisach, majacy SKU klienta, ale bez reguly, jest raportowany | `WARNING` |

## Kryteria dla poszczegolnych encji

### `ingredients`

Implementacyjnie sprawdz:

- puste `id`,
- puste `name_pl`,
- duplikaty `id`,
- `id` spoza oczekiwanego formatu, np. `C001`,
- skladniki uzyte w przepisach, ale nieobecne w `ingredients`.

### `nutrients`

Implementacyjnie sprawdz:

- obce `ingredient_id`,
- brak rekordu nutrient dla skladnika uzytego w przepisie,
- wartosci `None`,
- wartosci nieliczbowe,
- wartosci ujemne,
- skrajnie wysokie kcal,
- niespojnosc kcal z makro.

### `diet_policies`

Implementacyjnie sprawdz:

- obce `ingredient_id`,
- flagi inne niz `0` lub `1`,
- `vegan_ok` bez `vegetarian_ok`,
- mieso oznaczone jako vegetarian/vegan,
- ryba oznaczona jako vegetarian/vegan.

### `recipes`

Implementacyjnie sprawdz:

- puste `id` i `title_pl`,
- `category` spoza slownika,
- `dish_type` spoza slownika,
- `time_min <= 0`,
- `servings <= 0`,
- niepoprawny JSONB `ingredients_data`,
- niepoprawny JSONB `steps_pl`,
- brak danych odzywczych dla skladnikow.

### `client_skus`

Implementacyjnie sprawdz:

- puste `id`,
- puste `name_pl`,
- obce `client_id`,
- obce `concept_id`,
- brak makro dla SKU uzytego w regule,
- wartosci odzywcze ujemne lub nieliczbowe,
- SKU bez `concept_id` uzyte w brandyfikacji.

### `sku_selection_rules`

Implementacyjnie sprawdz:

- obcy `client_id`,
- obcy `concept_id`,
- obcy `preferred_sku_id`,
- SKU z innego klienta niz regula,
- SKU mapowane na inny koncept niz regula,
- `rule_order <= 0`,
- `condition_type` spoza slownika,
- `condition_value` spoza slownika dla danego `condition_type`,
- brak fallbacku `default/any` dla brandowalnego konceptu.

### Mapowanie SKU na koncepty

Implementacyjnie sprawdz:

- `client_sku_id` spoza katalogu klienta,
- `concept_id` spoza `ingredients`,
- `match_type` spoza slownika,
- `promotion_priority` nieliczbowe albo ujemne,
- wiele konfliktowych mapowan jednego SKU.
