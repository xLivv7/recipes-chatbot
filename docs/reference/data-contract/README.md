# Kontrakt danych - indeks

Wersja: 0.2<br>
Status: techniczny material odniesienia; zakres i zadania sa utrzymywane w specs/<br>
Zakres: Branded Recipe Chatbot SaaS, etap stabilizacji danych

Ten katalog opisuje kontrakt danych dla projektu. Dokument zostal podzielony tak, aby:

- latwiej robic atomowe commity,
- szybciej znajdowac kryteria walidacji podczas pracy nad `validate_db.py`,
- oddzielic decyzje domenowe od checklist implementacyjnych.

## Kolejnosc czytania

1. [Zasady i MVP](01_principles_and_mvp.md)
2. [Slowniki kontrolowane](02_controlled_vocabularies.md)
3. [Kontrakty tabel](03_table_contracts.md)
4. [Kontrakt JSONB przepisow](04_recipe_jsonb_contract.md)
5. [Kontrakt brandyfikacji](05_branding_contract.md)
6. [Kontrakt wartosci odzywczych](06_nutrition_contract.md)
7. [Kryteria walidatorow](07_validator_criteria.md)
Historyczne ryzyka i dawne plany przeniesiono do
[archiwum](../../archive/design/data_contract_risks_before_sdd.md).
Aktualna praca: [specyfikacja](../../../specs/001-mvp-stabilization/spec.md)
i [zadania](../../../specs/001-mvp-stabilization/tasks.md).

> Baza i backend sa zrodlem faktow. LLM interpretuje zapytanie, a lokalny
> renderer przedstawia wynik. Model nie redaguje koncowych przepisow.
