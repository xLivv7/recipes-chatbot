# Kontrakt danych - indeks

Wersja: 0.2  
Status: dokumentacja podzielona na mniejsze czesci  
Zakres: Branded Recipe Chatbot SaaS, etap stabilizacji danych

Ten katalog opisuje kontrakt danych dla projektu. Dokument zostal podzielony tak, aby:

- latwiej robic atomowe commity,
- szybciej znajdowac kryteria walidacji podczas pracy nad `validate_db.py`,
- oddzielic decyzje domenowe od checklist implementacyjnych.

## Kolejnosc czytania

1. [Zasady i MVP](data_contract/01_principles_and_mvp.md)
2. [Slowniki kontrolowane](data_contract/02_controlled_vocabularies.md)
3. [Kontrakty tabel](data_contract/03_table_contracts.md)
4. [Kontrakt JSONB przepisow](data_contract/04_recipe_jsonb_contract.md)
5. [Kontrakt brandyfikacji](data_contract/05_branding_contract.md)
6. [Kontrakt wartosci odzywczych](data_contract/06_nutrition_contract.md)
7. [Kryteria walidatorow](data_contract/07_validator_criteria.md)
8. [Ryzyka i nastepne kroki](data_contract/08_risks_and_next_steps.md)

## Proponowane atomowe commity

1. `docs: add data contract principles and mvp scope`
2. `docs: add controlled vocabularies`
3. `docs: add database table contracts`
4. `docs: add recipe jsonb contract`
5. `docs: add branding and nutrition contracts`
6. `docs: add validator criteria`
7. `docs: document data risks and next steps`

## Zasada nadrzedna

> Baza danych jest zrodlem prawdy. LLM moze interpretowac zapytanie uzytkownika i redagowac odpowiedz, ale nie moze wymyslac przepisow, produktow, skladnikow ani wartosci odzywczych.

## Najblizszy krok techniczny

Nastepny etap to przebudowa `validate_db.py` w walidator calej bazy, najlepiej wedlug checklisty z pliku [Kryteria walidatorow](data_contract/07_validator_criteria.md).
