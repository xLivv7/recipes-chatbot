# Dokumentacja techniczna i dowody

**Pracę zaczynaj od [specyfikacji](../specs/001-mvp-stabilization/spec.md)
i [zadań](../specs/001-mvp-stabilization/tasks.md).** Ten katalog nie jest backlogiem.

| Miejsce | Rola | Punkt wejścia |
| --- | --- | --- |
| `architecture.md` | Aktualny przepływ i odpowiedzialności. | [Architektura](architecture.md) |
| `reference/data-contract/` | Model danych i reguły walidacji. | [Kontrakt danych](reference/data-contract/README.md) |
| `reference/contracts/` | Granice obsługi zapytań. | [Alergie](reference/contracts/allergy_request_boundary.md), [wykluczenia](reference/contracts/unsupported_exclusions_contract.md) |
| `reference/evaluation/` | Metodyka narzędzi pomiarowych. | [Routing](reference/evaluation/separated_routing_evaluation.md), [uruchamianie](../evals/README.md) |
| `reports/` | Wyniki i analizy dla konkretnych wersji. | [Baseline](reports/baseline_2026-10-22.md), [przegląd luk](reports/stabilization_review_2026-10-22.md) |
| `archive/` | Historyczny stan, dawne plany i protokoły. | [Stan przed SDD](archive/baseline/current_state_2026-10-22.md), [dawny projekt renderera](archive/design/response_protection_design.md) |

## Zasady

- Wymagania, decyzje, plan i zadania aktualizujemy w `specs/`.
- Opis techniczny aktualizujemy w istniejącym pliku `reference/` lub architekturze.
- Nowy raport tworzymy dla wykonanego pomiaru lub analizy z datą i wersją.
- Archiwalne „następne kroki” nie zastępują aktualnego `tasks.md`.
- Identyfikatory MVP/ACC/ST/DEC zachowują znaczenie po przeniesieniu plików.

Surowe raporty, snapshoty i materiały pracy pozostają w ignorowanym
`dokumentacja pracy/`; decyzje klasyfikacyjne w `curation/`, testy w `tests/`,
a przypadki i programy ewaluacyjne w `evals/`. Te obszary pozostają na miejscu.
Stare dokumenty z `docs/` przeniesiono do kategorii i poprawiono odsyłacze
w utrzymywanych materiałach.
