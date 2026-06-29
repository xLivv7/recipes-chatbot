# Kontrakty tabel

[Powrot do indeksu](../data_contract.md)

Ten dokument opisuje kontrakt rekordow dla tabel i plikow zrodlowych. Kryteria w bardziej implementacyjnym ukladzie sa w pliku [Kryteria walidatorow](07_validator_criteria.md).

## `ingredients`

Obecne pola w bazie:

- `id`
- `name_pl`

Pola obecne w CSV, ale jeszcze nie w modelu bazy:

- `category`
- `synonyms_pl`
- `allergens_pl`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `id` musi byc niepuste i unikalne | `ERROR` |
| `id` powinno byc stabilnym identyfikatorem konceptu, np. `C001` | `ERROR` |
| `name_pl` musi byc niepuste | `ERROR` |
| kazdy skladnik uzyty w przepisie musi istniec w `ingredients` | `ERROR` |
| kazdy skladnik z `nutrients` i `diet_policies` musi istniec w `ingredients` | `ERROR` |
| `category`, jesli jest dostepne, musi nalezec do slownika kategorii skladnikow | `WARNING` teraz, `ERROR` po dodaniu kolumny do bazy |
| synonimy, jesli sa dostepne, powinny byc rozdzielone znakiem `|` i nie powinny zawierac pustych wartosci | `WARNING` |
| alergeny, jesli sa dostepne, powinny byc rozdzielone znakiem `|` i standaryzowane | `WARNING` |

Decyzja projektowa:

- `ingredients` reprezentuje generyczne koncepty kulinarne, nie produkty marek.
- Produkt marki musi trafic do `client_skus`, nie do `ingredients`.

## `nutrients`

Obecne pola:

- `ingredient_id`
- `energy_kcal_100g`
- `protein_g_100g`
- `fat_g_100g`
- `carbs_g_100g`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `ingredient_id` musi istniec w `ingredients.id` | `ERROR` |
| wartosci kcal, bialka, tluszczu i weglowodanow musza byc liczbami | `ERROR` |
| wartosci nie moga byc ujemne | `ERROR` |
| skladnik uzyty w przepisie musi miec rekord w `nutrients`, chyba ze zawsze jest brandyfikowany SKU z pelnym makro | `ERROR` |
| `energy_kcal_100g` powinno miescic sie w sensownym zakresie, np. 0-950 kcal | `WARNING` |
| suma makro nie powinna przekraczac ok. 100 g na 100 g produktu | `WARNING` |
| kcal powinny byc orientacyjnie zgodne z makro: `4*protein + 9*fat + 4*carbs` | `WARNING` |

## `diet_policies`

Obecne pola:

- `ingredient_id`
- `is_vegetarian_ok`
- `is_vegan_ok`
- `is_meat`
- `is_fish`
- `is_keto_ok`

Pola obecne w CSV, ale nieprzenoszone obecnie do modelu:

- `is_animal_product`
- `notes`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `ingredient_id` musi istniec w `ingredients.id` | `ERROR` |
| flagi musza miec wartosci `0` lub `1` | `ERROR` |
| `is_vegan_ok = 1` implikuje `is_vegetarian_ok = 1` | `ERROR` |
| `is_meat = 1` implikuje `is_vegetarian_ok = 0` oraz `is_vegan_ok = 0` | `ERROR` |
| `is_fish = 1` implikuje `is_vegetarian_ok = 0` oraz `is_vegan_ok = 0` | `ERROR` |
| skladnik bez polityki dietetycznej uzyty w przepisie powinien zostac zgloszony | `WARNING` teraz, docelowo `ERROR` |
| skladnik keto powinien miec niska zawartosc weglowodanow albo byc swiadomym wyjatkiem | `WARNING` |

Decyzja projektowa:

- Dla diety weganskiej i wegetarianskiej system powinien odrzucac przepis, jezeli jakikolwiek skladnik narusza polityke.
- Dla `meat` i `fish` system szuka obecnosci odpowiedniego skladnika, a nie usuwa innych skladnikow.

## `clients`

Obecne pola:

- `id`
- `name`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `id` musi byc unikalne | `ERROR` |
| `name` musi byc niepuste | `ERROR` |
| `name` powinno byc unikalne | `ERROR` |
| klient demonstracyjny powinien miec co najmniej jeden SKU albo zostac oznaczony jako nieaktywny | `WARNING` |

## `client_skus`

Obecne pola:

- `id`
- `client_id`
- `concept_id`
- `name_pl`
- `energy_kcal_100`
- `protein_g_100`
- `fat_g_100`
- `carbs_g_100`

Pola obecne w CSV, ale obecnie nieprzenoszone do modelu:

- `brand`
- `pack_size`
- `ingredients_pl_short`
- `allergens_pl`
- `may_contain_pl`
- `salt_g_100`
- `nutrition_basis`
- `source_url`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `id` musi byc niepuste i unikalne | `ERROR` |
| `client_id` musi istniec w `clients.id` | `ERROR` |
| `concept_id`, jesli istnieje, musi wskazywac `ingredients.id` | `ERROR` |
| `name_pl` musi byc niepuste | `ERROR` |
| wartosci kcal i makro musza byc liczbami nieujemnymi | `ERROR` |
| SKU uzywane w regule wyboru musi miec kompletne makro | `ERROR` |
| SKU z `concept_id = NULL` nie moze byc uzywane w regule brandyfikacji | `ERROR` |
| `nutrition_basis` inne niz `per 100 g` powinno zostac zgloszone, bo obecne pola w bazie nie rozrozniaja gramow i mililitrow | `WARNING` |
| alergeny SKU powinny byc zgodne z dieta i mapowanym konceptem | `WARNING` |
| SKU klienta powinno miec marke zgodna z klientem | `WARNING` |

Decyzja projektowa:

- SKU jest konkretnym produktem klienta.
- SKU moze zastapic tylko taki koncept, z ktorym jest powiazane przez `concept_id`.
- LLM nie moze zmieniac nazwy SKU ani dopisywac produktu, jesli nazwa nie wynika z bazy.

## Mapowanie SKU na koncepty

Obecnie mapowanie pochodzi z pliku:

- `data/raw/clients/Winiary/sku_to_concept_map.csv`

Pola:

- `client_sku_id`
- `concept_id`
- `match_type`
- `promotion_priority`
- `notes`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `client_sku_id` musi istniec w katalogu SKU klienta | `ERROR` |
| `concept_id` musi istniec w `ingredients.id` | `ERROR` |
| `match_type` musi nalezec do slownika | `ERROR` |
| jedno SKU powinno mapowac sie na jeden glowny koncept w MVP | `WARNING` |
| jeden koncept moze miec wiele SKU | `INFO` |
| SKU z `match_type = close` powinno miec swiadomy komentarz albo uzasadnienie | `WARNING` |
| `promotion_priority` powinno byc liczba dodatnia | `WARNING` |

Decyzja projektowa:

- Dla MVP mapowanie moze byc materializowane w `client_skus.concept_id`.
- Docelowo osobna tabela mapowan bylaby czytelniejsza, bo przechowuje `match_type`, priorytet i uzasadnienie.

## `sku_selection_rules`

Obecne pola:

- `id`
- `client_id`
- `concept_id`
- `rule_order`
- `condition_type`
- `condition_value`
- `preferred_sku_id`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `client_id` musi istniec w `clients.id` | `ERROR` |
| `concept_id` musi istniec w `ingredients.id` | `ERROR` |
| `preferred_sku_id` musi istniec w `client_skus.id` | `ERROR` |
| `preferred_sku_id` musi nalezec do tego samego klienta co regula | `ERROR` |
| `preferred_sku_id.concept_id` musi byc zgodne z `rule.concept_id` albo miec jawny typ zamiennika | `ERROR` |
| `rule_order` musi byc liczba dodatnia | `ERROR` |
| dla pary `client_id + concept_id` kolejnosc regul powinna byc jednoznaczna | `WARNING` |
| `condition_type` musi nalezec do slownika | `ERROR` |
| `condition_value` musi nalezec do odpowiedniego slownika dla danego `condition_type` | `ERROR` |
| dla `condition_type = default`, `condition_value` powinno byc `any` | `ERROR` |
| dla brandowalnego konceptu powinien istniec fallback `default` | `WARNING` |
| regula nie moze wybierac SKU sprzecznego z dieta uzytkownika | `ERROR` |

Znane ryzyko obecnego kodu:

- Funkcja `choose_sku` w `main.py` wybiera reguly po `concept_id`, ale nie przyjmuje `client_id`. Dla jednego klienta demonstracyjnego to dziala, ale dla SaaS musi zostac zmienione na wybor w zakresie konkretnego klienta.

## `recipes`

Obecne pola:

- `id`
- `title_pl`
- `category`
- `dish_type`
- `time_min`
- `servings`
- `ingredients_data`
- `steps_pl`

Reguly poprawnosci:

| Regula | Poziom |
| --- | --- |
| `id` musi byc niepuste i unikalne | `ERROR` |
| `title_pl` musi byc niepuste | `ERROR` |
| `category` musi nalezec do slownika kategorii posilku | `ERROR` |
| `dish_type` powinien nalezec do slownika typow dan | `WARNING` |
| `time_min` musi byc liczba dodatnia | `ERROR` |
| `servings` musi byc liczba dodatnia | `ERROR` |
| `ingredients_data` musi byc lista obiektow | `ERROR` |
| kazdy skladnik przepisu musi miec `concept_id` i `grams` | `ERROR` |
| kazdy `concept_id` w przepisie musi istniec w `ingredients` | `ERROR` |
| `grams` musi byc liczba dodatnia | `ERROR` |
| `steps_pl` musi byc niepusta lista tekstow | `ERROR` |
| deklarowana dieta przepisu, jesli zostanie dodana, musi wynikac ze skladnikow | `ERROR` |
| przepis powinien miec kompletne makro obliczalne z `nutrients` lub SKU | `ERROR` |
| czas przygotowania powinien miescic sie w sensownym zakresie, np. 1-240 min | `WARNING` |
