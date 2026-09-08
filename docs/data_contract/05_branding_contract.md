# Kontrakt brandyfikacji

[Powrot do indeksu](../data_contract.md)

## Wejscie do brandyfikacji

Minimalne wejscie:

- `client_id`
- `recipe_id`
- `diet`
- `protein_preference`
- `restrictions`
- `nutrition_goal`

Obecny kod nie przyjmuje jeszcze `client_id` w funkcji `orchestrate_recipe`, ale dla docelowego SaaS jest to wymagane.

## Regula wyboru SKU

Dla kazdego skladnika przepisu:

1. System sprawdza, czy `concept_id` ma dostepne SKU dla danego klienta.
2. System pobiera reguly `sku_selection_rules` dla pary `client_id + concept_id`.
3. Reguly sa analizowane rosnaco po `rule_order`.
4. Regula pasuje, jezeli:
   - `condition_type = diet` i `condition_value` odpowiada diecie przekazanej do runtime,
   - albo `condition_type = protein_preference` i `condition_value` odpowiada oczekiwanemu zrodlu bialka,
   - albo `condition_type = restriction` i `condition_value` znajduje sie na liscie ograniczen,
   - albo `condition_type = nutrition_goal` i `condition_value` odpowiada celowi przekazanemu do runtime,
   - albo `condition_type = default` i `condition_value = any`.
5. Wybrane SKU musi:
   - nalezec do danego klienta,
   - mapowac sie na ten sam koncept,
   - miec kompletne wartosci odzywcze,
   - nie naruszac preferencji dietetycznej,
   - miec `is_gluten_free = 1`, jezeli aktywne jest ograniczenie `gluten_free`.

Jezeli pierwsza pasujaca regula wskazuje SKU niedozwolone przez aktywne ograniczenie, runtime przechodzi do kolejnej reguly. Gdy nie istnieje zgodny produkt, skladnik pozostaje generyczny.

## Fallback

Jesli nie znaleziono poprawnego SKU:

- skladnik pozostaje generyczny,
- wartosci odzywcze sa liczone z `nutrients`,
- wynik powinien zawierac brak SKU dla tego skladnika,
- walidator powinien raportowac brak brandyfikacji jako `WARNING`, nie jako blad blokujacy.

Wyjatek:

- jezeli skladnik nie ma ani SKU, ani danych w `nutrients`, system nie moze policzyc makro. To jest `ERROR`.

## Zakazy

System nie moze:

- wybrac SKU spoza klienta,
- wybrac SKU spoza mapowanego konceptu,
- wybrac SKU sprzecznego z dieta,
- wybrac SKU bez jawnej zgodnosci z aktywnym ograniczeniem,
- dopisac SKU tylko dlatego, ze nazwa brzmi podobnie,
- zmienic gramatury skladnika bez jawnej reguly.

## Kryteria blokujace dla walidatora

Walidator powinien zwracac `ERROR`, gdy:

- regula wskazuje nieistniejace SKU,
- regula wskazuje SKU innego klienta,
- regula wskazuje SKU mapowane na inny koncept niz `rule.concept_id`,
- SKU z reguly nie ma kompletnych wartosci odzywczych,
- regula `diet = vegan` wskazuje produkt jawnie nieweganski,
- `condition_type` nie nalezy do dozwolonego slownika,
- `condition_value` jest puste albo dla reguly `default` ma wartosc inna niz `any`.
