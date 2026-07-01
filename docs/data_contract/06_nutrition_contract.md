# Kontrakt wartosci odzywczych

[Powrot do indeksu](../data_contract.md)

## Zrodlo wartosci

Dla kazdego skladnika:

- jezeli zostal wybrany SKU, uzywane sa wartosci odzywcze SKU,
- jezeli nie zostal wybrany SKU, uzywane sa wartosci odzywcze generycznego konceptu,
- wartosci sa liczone proporcjonalnie do `grams / 100`,
- suma przepisu jest dzielona przez `servings`, aby uzyskac wartosc na porcje.

## Reguly

| Regula | Poziom |
| --- | --- |
| kazdy skladnik musi miec zrodlo kcal i makro | `ERROR` |
| `servings` nie moze byc zerowe | `ERROR` |
| kcal i makro na porcje nie moga byc ujemne | `ERROR` |
| kcal na porcje powinny miescic sie w sensownym zakresie, np. 20-2000 | `WARNING` |
| dla `nutrition_goal = keto` obecny kod odrzuca przepisy powyzej 15 g weglowodanow na porcje | `INFO` |

## Sanity checks

Walidator powinien raportowac `WARNING`, gdy:

- `energy_kcal_100g` jest poza zakresem 0-950 kcal,
- suma makro przekracza ok. 100 g na 100 g produktu,
- kcal sa mocno niespojne z makro liczonym jako `4*protein + 9*fat + 4*carbs`,
- kcal na porcje sa bardzo niskie albo bardzo wysokie.

Ostrzezenie o niespojnosci kcal z makro nie oznacza automatycznie bledu danych. Formula `4/9/4` jest sanity checkiem, ale moze zawyzac kcal dla skladnikow bogatych w blonnik, przypraw, kakao albo slodzikow poliolowych, np. ksylitolu i erytrytolu. Takie rekordy trzeba przejrzec recznie przed poprawianiem danych.

## Znane uproszczenie MVP

W CSV SKU wystepuje `nutrition_basis`, np. `per 100 g` lub `per 100 ml`, ale obecny model zapisuje wartosci do pol `*_100`. Dla precyzyjnego systemu trzeba rozroznic jednostke bazowa albo jawnie przyjac uproszczenie MVP.
