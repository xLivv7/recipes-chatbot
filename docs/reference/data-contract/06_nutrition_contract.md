# Kontrakt wartosci odzywczych

[Powrot do indeksu](README.md)

## Zrodlo wartosci

Dla kazdego skladnika:

- jezeli zostal wybrany SKU, uzywane sa wartosci odzywcze SKU,
- jezeli nie zostal wybrany SKU, uzywane sa wartosci odzywcze generycznego konceptu,
- ilość z wybranego wariantu receptury dzielimy przez 100 i mnożymy przez wartości na 100 g lub 100 ml odpowiedniej postaci produktu,
- suma przepisu jest dzielona przez `servings`, aby uzyskac wartosc na porcje.

## Reguly

Dla C012, C338, C357 i C367 pole `carbs_g_100g` zawiera wartość
„Węglowodany” z Fitatu, bez dodatkowego odejmowania błonnika. Dla C367
wynosi 60,6 g na 100 g. [Decyzja i źródła T007](../../reports/t007_nutrition_2026-11-18.md).

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

## Warianty receptur w gramach i mililitrach

CSV SKU zawiera `nutrition_basis`. W PostgreSQL liczby SKU są zapisane w polach `*_100`.
Majonez Dekoracyjny 400 ml jest rozliczany na 100 g. Dla czterech produktów z tabelą na 100 ml
ilość dla całej receptury określa opcjonalne pole `sku_ml` w `ingredients_data`.
Pole `grams` opisuje osobny wariant masowy. Wybór jednostki zależy od ostatecznie dobranego produktu.
Gdy starsza receptura ma tylko `grams`, aplikacja pomija produkt objętościowy
i sprawdza zgodność wariantu generycznego. Warunki diety i ograniczeń obowiązują przed podaniem przepisu.

W odpowiedzi ilość składnika ma jedną parę pól, `grams_total` i `grams_per_serving`
albo `ml_total` i `ml_per_serving`. Lista składników pokazuje ilość łączną.
Kcal i B/T/W na porcję wynikają z podzielenia sumy przez liczbę porcji.
Dla SKU bulionu lista składników nazywa gotowy wywar, a pierwszy krok poleca
przygotowanie według instrukcji na opakowaniu i odmierzenie objętości z receptury.
[Decyzja katalogowa i sprawdzenie](../../docs/reports/t012_sku_nutrition_basis.md).
