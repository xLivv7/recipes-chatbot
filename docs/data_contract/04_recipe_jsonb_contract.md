# Kontrakt JSONB przepisow

[Powrot do indeksu](../data_contract.md)

## `recipes.ingredients_data`

Minimalny poprawny ksztalt:

```json
[
  {
    "concept_id": "C001",
    "grams": 80
  }
]
```

Reguly:

- lista nie moze byc pusta,
- kazdy element musi byc obiektem,
- `concept_id` musi byc tekstem i wskazywac istniejacy koncept,
- `grams` musi byc liczba dodatnia,
- wartosci gramatury dotycza calego przepisu, nie jednej porcji.

## `recipes.steps_pl`

Minimalny poprawny ksztalt:

```json
[
  "Pokroj warzywa.",
  "Wymieszaj skladniki.",
  "Podawaj od razu."
]
```

Reguly:

- lista nie moze byc pusta,
- kazdy krok musi byc niepustym tekstem,
- kroki nie powinny odnosic sie do skladnikow, ktorych nie ma w `ingredients_data`,
- kroki nie powinny zawierac nazw SKU, jezeli brandyfikacja ma byc dynamiczna.

## Kryteria blokujace dla walidatora

Walidator powinien zwracac `ERROR`, gdy:

- `ingredients_data` nie jest lista,
- `ingredients_data` jest pusta,
- element listy nie jest obiektem,
- brakuje `concept_id`,
- brakuje `grams`,
- `grams` nie jest liczba,
- `grams <= 0`,
- `concept_id` nie istnieje w `ingredients`,
- `steps_pl` nie jest lista,
- `steps_pl` jest pusta,
- krok przepisu jest pusty albo nie jest tekstem.
