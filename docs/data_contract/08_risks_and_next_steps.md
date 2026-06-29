# Ryzyka i nastepne kroki

[Powrot do indeksu](../data_contract.md)

## Znane ryzyka obecnego stanu

1. Dane zrodlowe sa czesciowo generowane lub uzupelniane przez AI, wiec wymagaja audytu.
2. `sku_selection_rules` zawiera wartosci `no_sugar` i `spicy`, ktore nie sa zgodne z obecnymi enumami tool calling.
3. `choose_sku` nie jest jeszcze zakreslone przez `client_id`, co blokuje prawdziwa wieloklienckosc.
4. `ingredients` w bazie nie przechowuje jeszcze kategorii, synonimow i alergenow, mimo ze sa w CSV.
5. `client_skus` w bazie nie przechowuje `nutrition_basis`, wiec moze mieszac wartosci `per 100 g` i `per 100 ml`.
6. Brak pelnego walidatora powoduje, ze bledy w JSONB moga ujawnic sie dopiero w runtime.
7. Brak testow automatycznych utrudnia bezpieczna refaktoryzacje `main.py`.
8. LLM moze ladnie sformulowac odpowiedz, ale bez walidacji system nie udowodni, ze odpowiedz jest oparta na prawdziwych danych.

## Kryteria zakonczenia etapu 1

Etap 1 jest zakonczony, gdy:

- istnieje dokument kontraktu danych,
- zdefiniowano slowniki kontrolowane,
- opisano kontrakt kazdej tabeli,
- opisano ksztalt JSONB dla przepisow,
- opisano reguly brandyfikacji,
- opisano minimalna macierz walidatorow,
- wskazano znane ryzyka obecnego stanu.

## Nastepny krok: etap 2

Nastepny etap to implementacja walidatora calej bazy.

Rekomendowana kolejnosc:

1. Rozszerzyc `validate_db.py` z jednego walidatora przepisow do raportu calej bazy.
2. Dodac klasyfikacje problemow na `ERROR`, `WARNING`, `INFO`.
3. Najpierw zaimplementowac walidatory relacyjne i JSONB.
4. Potem dodac walidatory slownikow, diet i wartosci odzywczych.
5. Na koncu dodac raport pokrycia brandyfikacji dla klienta.

Minimalny etap 2 powinien wykrywac:

- nieistniejace `concept_id`,
- braki w `nutrients`,
- niepoprawne struktury `ingredients_data`,
- niepoprawne `grams`,
- reguly SKU wskazujace nieistniejace SKU,
- SKU przypisane do innego klienta niz regula,
- wartosci `condition_value` spoza slownikow.
