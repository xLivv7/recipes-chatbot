# Branded Recipe Chatbot

Prototyp asystenta kulinarnego dla marki spożywczej, rozwijany w ramach pracy
inżynierskiej. Obecny etap to stabilizacja istniejących funkcji dla Winiary:
niezawodność, poprawność rekomendacji i jakość odpowiedzi. SaaS i widget
pozostają kierunkiem dalszego rozwoju.

## Od czego zacząć

| Potrzeba | Dokument |
| --- | --- |
| Co budujemy i jakie decyzje obowiązują? | [Specyfikacja MVP](specs/001-mvp-stabilization/spec.md) |
| Po czym poznamy gotowość MVP? | [Kryteria akceptacji](specs/001-mvp-stabilization/acceptance.md) |
| W jakiej kolejności pracujemy? | [Plan](specs/001-mvp-stabilization/plan.md) |
| Co zrobiono, co dalej, co wstrzymano? | [Zadania](specs/001-mvp-stabilization/tasks.md) |
| Jakie są testy i luki? | [Mapa weryfikacji](specs/001-mvp-stabilization/verification.md) |
| Jak działa kod i gdzie są materiały techniczne? | [Dokumentacja](docs/README.md) |

## Obecna architektura

Zapytanie po polsku → lokalna kontrola zakresu → LLM wybierający narzędzie
i argumenty → lokalna walidacja → deterministyczne rekomendacje i SKU
→ obliczenie makro → lokalny renderer.

Backend korzysta z Python, SQLAlchemy i PostgreSQL. Model interpretuje
zapytanie; nie redaguje końcowych przepisów. Nie ma drugiego wywołania LLM
z wynikami bazy ani wyszukiwania wektorowego. Szczegóły:
[architektura](docs/architecture.md).

## Uruchomienie lokalne

Potrzebne są środowisko Python, istniejąca baza PostgreSQL i konfiguracja
`DATABASE_URL` oraz `OPENAI_API_KEY` w lokalnym `.env`. Nie zapisuj sekretów
w repozytorium. Dane są poza Git; sam klon nie odtworzy katalogu.

```powershell
venv\Scripts\python.exe main.py
```

Uruchomienie wysyła zapytanie przykładowe do API i może naliczyć koszt.
Przykład jest zapisany w `main.py`; nie jest to interaktywna konsola.
Stan bazowy opisuje [raport](docs/reports/baseline_2026-10-22.md).
Instrukcja przygotowania od zera i próba odtworzenia pozostają zadaniem.

## Sposób pracy

Wymagania → plan → zadania → implementacja → weryfikacja.
Aktywne ustalenia są w `specs/`, opis techniczny i dowody w `docs/`.
[Zasady SDD](specs/README.md) określają role plików.
Analiza pięciu SKU jest wstrzymana na prośbę autorki. Pozostałe prace
mogą postępować, ale luka makro nie jest uznana za zamkniętą.
