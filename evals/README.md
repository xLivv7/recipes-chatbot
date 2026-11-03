# Ewaluacja obecnego MVP

Katalog zawiera zbiory przypadków i programy weryfikujące interpretację
zapytań, routing oraz lokalny renderer. Polecenia uruchamiaj w katalogu
głównym projektu, z przygotowanym środowiskiem `venv`. Runner routingu
importuje aplikację i wymaga dostępu do lokalnego katalogu PostgreSQL,
również przy `--dry-run`.

## Ustalenia i dokumentacja

- [Kryteria akceptacji MVP](../specs/001-mvp-stabilization/acceptance.md) — obowiązujące progi i warunki zaliczenia.
- [Mapa weryfikacji](../specs/001-mvp-stabilization/verification.md) — powiązania kryteriów z dowodami i pozostałe luki.
- [Zadania stabilizacyjne](../specs/001-mvp-stabilization/tasks.md) — bieżąca praca.
- [Metodyka rozdzielonej ewaluacji](../docs/reference/evaluation/separated_routing_evaluation.md) — zakres, metryki i ograniczenia.
- [Kontrola bazowa z 2026-10-22](../docs/reports/baseline_2026-10-22.md) — punkt odniesienia przed poprawkami.
- [Historia ewaluacji](../docs/archive/evaluation/evaluation_history.md) — wcześniejsze konfiguracje i wyniki.

## Renderer — kontrola offline

```powershell
venv\Scripts\python.exe evals\run_renderer_eval.py --output "dokumentacja pracy\NAZWA_PRZEBIEGU\renderer.json"
```

Kontrola nie wywołuje API. Porównuje wynik renderera z oczekiwaną treścią
lub odrzuceniem kontrolowanego payloadu. Nie potwierdza poprawności danych
katalogu, jakości modelu ani czytelności odpowiedzi dla użytkownika.
Przed uruchomieniem zastąp `NAZWA_PRZEBIEGU` nową, jednoznaczną nazwą.

## Routing — przygotowanie bez wywołań API

```powershell
venv\Scripts\python.exe evals\run_routing_eval.py --mode raw --repeats 3 --dry-run
venv\Scripts\python.exe evals\run_routing_eval.py --mode application --repeats 3 --dry-run
```

`--dry-run` sprawdza wczytanie zbiorów i pokazuje planowaną liczbę ocen
oraz wywołań API. Nie wykonuje pomiaru jakości i nie zapisuje raportu.

- `raw` mierzy model bez ochrony preflight, z produkcyjnym promptem,
  schematem i walidacją argumentów.
- `application` mierzy rzeczywisty routing aplikacji wraz z preflight,
  walidacją i dispatch. Wyszukiwanie jest zastąpione kontrolowanym wynikiem.

Żaden z trybów nie mierzy poprawności rekomendacji na danych bazy ani
pełnego przepływu od zapytania do rzeczywistego wyniku. Zatrzymania przez
preflight nie są sukcesami interpretacji modelu.

## Płatne pomiary i zachowanie raportów

### Kontrolowane porównanie T009

`run_routing_experiment.py` obsługuje zamrożone warianty V0/V1/V2,
rotację trzech rund i oddzielne raw/application. Nie zmienia aktywnego
promptu aplikacji ani danych. Protokół jest w sekcji 5
[plan.md](../specs/001-mvp-stabilization/plan.md).

```powershell
venv\Scripts\python.exe evals\run_routing_experiment.py --dry-run --output "dokumentacja pracy\NOWA_KAMPANIA"
```

Dry-run tworzy nowy katalog, pełne prompty, manifest, hashe i oszacowanie
kosztu; nie wywołuje API. Nie nadpisuje istniejącej kampanii. Późniejsze
`--execute --output` dla tego samego katalogu weryfikuje zamrożone wejścia
i rozpoczyna płatne wywołania według protokołu. Błąd API zatrzymuje kampanię
z niepełnym checkpointem; selektywne wznowienie jest zablokowane.
Wynik porównania i wybór kandydata nie podmieniają promptu produkcyjnego.

Uruchomienia routingu bez `--dry-run` wykonują płatne wywołania API.
Wymagają osobnego planu kampanii: ustalonych zbiorów i etykiet, wersji
kodu i promptu, konfiguracji modelu, liczby powtórzeń, progów oraz miejsc
zapisu raportów. Niniejsza instrukcja nie rozpoczyna takiej kampanii.

Każdy pomiar zapisuj przez `--output` do nowej ścieżki, np.
`"dokumentacja pracy\NAZWA_PRZEBIEGU\application.json"`. Runner nadpisuje
wskazany plik; nie używaj ścieżek wcześniejszych raportów ani domyślnego
raportu jako trwałego archiwum. Zachowuj również niepełne przebiegi i błędy
API, opisując przyczynę powtórzenia. Surowe lokalne raporty są ignorowane
przez Git; ich lokalizację i wersję dokumentuj w raporcie kampanii.

Holdout v1 jest ujawniony i służy historii lub regresji. Końcowa niezależna
ocena wymaga nowego, zamrożonego zbioru zgodnie z kryteriami akceptacji.
`run_llm_eval.py` pozostaje narzędziem zgodnościowym;
`run_final_answer_eval.py` dotyczy historycznej architektury z drugim
wywołaniem LLM i bez `--dry-run` także generuje płatne wywołania API.
