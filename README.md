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

### Odtworzenie backendu z kopii katalogu (T011)

1. Przygotuj Git, Python 3.14.0, PostgreSQL 18.3 i prywatne pliki z próby
   T011. Ścieżkę do archiwum i jego SHA-256 podaje [mapa weryfikacji](specs/001-mvp-stabilization/verification.md#t011--odtworzenie-backendu).
   W PowerShellu ustaw `$raport` na pełną ścieżkę folderu z archiwum.
   Sprawdź `Get-FileHash "$raport\catalog.dump" -Algorithm SHA256`.
2. W pgAdminie utwórz nową, pustą bazę na koncie używanym przez aplikację.
   Kliknij tę bazę i wybierz **Restore…**, format **Custom or tar** i plik
   `catalog.dump`. Poczekaj na potwierdzenie powodzenia.
3. Z katalogu głównego repozytorium wykonaj w PowerShellu poniższe polecenia
   z nową nazwą katalogu docelowego.

   ```powershell
   git clone --no-checkout . ..\Recipes_Chatbot_T011
   Set-Location ..\Recipes_Chatbot_T011
   git checkout --detach 27ed9dac9572a6552e3e25ff5ed0a06390a10580
   py -3.14 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt -c "$raport\requirements-frozen.txt"
   .\.venv\Scripts\python.exe -m pip check
   ```

4. W kopii kodu utwórz lokalny plik `.env` z `DATABASE_URL` wskazującym
   na nową bazę. Jeśli terminal ma już ustawioną zmienną `DATABASE_URL`,
   ma ona pierwszeństwo przed plikiem. Sprawdź faktyczną nazwę bazy,
   następnie uruchom walidator i porównaj pięć lunchów z zapisanym wynikiem.
   Ta próba korzysta wyłącznie z backendu i PostgreSQL.

   ```powershell
   $python = '.\.venv\Scripts\python.exe'
   & $python -c "from core.database import engine; from sqlalchemy import text; c=engine.connect(); print(c.scalar(text('SELECT current_database()'))); c.close()"
   & $python validate_db.py
   & $python -c "import json, sys; from pathlib import Path; from core.recommendations import get_recommendations; expected=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); actual=get_recommendations(category='lunch', top_n=5); sys.exit(0 if len(actual['recommendations']) == 5 and actual == expected else 1)" "$raport\M01_przed.json"
   $LASTEXITCODE
   ```

   Walidator i porównanie powinny zakończyć się kodem `0`.

## Sposób pracy

Wymagania → plan → zadania → implementacja → weryfikacja.
Aktywne ustalenia są w `specs/`, opis techniczny i dowody w `docs/`.
[Zasady SDD](specs/README.md) określają role plików.
Decyzje dla pięciu SKU i sposób obliczania makro opisuje [raport T012/T030](docs/reports/t012_sku_nutrition_basis.md).
