# Ewaluacja obecnego MVP

Katalog zawiera zbiory przypadków i programy weryfikujące interpretację
zapytań, routing oraz lokalny renderer. Polecenia uruchamiaj w katalogu
głównym projektu, z przygotowanym środowiskiem `venv`. Runner routingu
importuje aplikację i wymaga dostępu do lokalnego katalogu PostgreSQL,
również przy `--dry-run`. Wyjątkiem jest opisany poniżej program
`prepare_routing_v5.py`: działa bez SDK, bazy i klucza.

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

## V5 / T021 — przygotowanie całkowicie offline

```powershell
venv\Scripts\python.exe evals\prepare_routing_v5.py --check
venv\Scripts\python.exe evals\prepare_routing_v5.py --output "dokumentacja pracy\NOWE_PRZYGOTOWANIE_V5"
```

Program sprawdza zakres zmian V4/V5, 18 demonstracji, argumenty, kontrasty
i odrębne zapytania diagnostyczne. `--output` wymaga nowego katalogu;
zapisuje prompty, schemat, przypadki, diff, kopie źródeł, hashe i plan.
Nie importuje aplikacji, SDK ani bazy i nie korzysta z kluczy lub sieci.
Nie ma `--execute` i nie wykonuje pomiaru jakości modelu.

Plan ma 20 zachowanych przypadków starego pilota i 12 nowych: 32 przypadki,
384 oceny / 354 wywołania, wykonane później w porównaniu V4/V5 w T023.
Osobny audyt offline pokazuje pięć znanych fałszywych blokad preflight
z expected=tool; nie zalicza ich jako sukcesów modelu ani aplikacji.
Mapa przykładów, metryki, kosztorys i ograniczenia są w
[planie T021](../specs/001-mvp-stabilization/plan.md#13-t021--przygotowanie-v5-dla-punktów-4-i-5-audytu),
a lokalne dowody w [mapie weryfikacji](../specs/001-mvp-stabilization/verification.md#t021--przygotowanie-v5-offline-zakończone).

Oryginalny pakiet T021 opisuje stan aplikacji sprzed T022. Nowe przygotowanie
zbiera bieżące hashe i deklarowany status T022. T023 dostarczyło instrumentację,
nowe zamrożenie po zmianach, potwierdzenie modelu/cennika oraz osobno
zatwierdzony pomiar. Ponowny pomiar wymaga nowego planu i zgody na jego
payload oraz koszt; zakończone T023 nie jest poleceniem powtórzenia. Stare profile poniżej
nie wykonują porównania V4/V5. Aktywny prompt pozostaje V0.

## Walidacja odpowiedzi po T022

Aplikacja i oba tryby runnera korzystają ze wspólnej kontroli odpowiedzi.
Brak choices, length, content_filter oraz niepuste pole refusal zatrzymują
lookup, także gdy odpowiedź zawiera poprawnie wyglądające argumenty.
Runner oznacza je jako błąd protokołu, z technicznym response_failure_reason
i bez punktu za decyzję modelu lub wartości parametrów. Ślad narzędzi
i metadane pozostają dostępne diagnostycznie.

Nowe raporty i wiersze mają response_validation_version=T022-v1; źródła
zamrożenia obejmują `core/llm_response_validation.py`. Zwykłe no_tool
nadal jest oceniane względem expected, a fałszywe blokady preflight są błędami
aplikacji. Starych raportów i przygotowania T021 nie przeliczano. Po zmianie
aplikacji/runnera trzeba utworzyć nowy manifest; starego pakietu T021 nie
wykonywać na nowym kodzie. [Dowody T022](../specs/001-mvp-stabilization/verification.md#t022--wdrożenie-no_tool-zakończone).

## Kandydat IR-1 po T026 — przygotowanie offline

`prepare_interpretation_v1.py` zamraża lokalne źródła, prompt IR1, schemat,
konfigurację klienta/modelu i szablon żądania w nowym katalogu:

```powershell
venv\Scripts\python.exe evals\prepare_interpretation_v1.py --output "dokumentacja pracy\NOWY_KANDYDAT_IR1"
```

Polecenie nie importuje SDK, aplikacji ani katalogu, nie wymaga klucza API
i nie wykonuje sieci. Istniejącego katalogu nie nadpisuje. Manifest zawiera
hashe źródeł i artefaktów, wersje runtime, commit oraz stan zmian. Funkcja
`validate_preparation` sprawdza kompletność i zgodność hashy kopii oraz
bieżących źródeł. Pakiet ma `execution_enabled=false`, nie jest planem
płatnej kampanii i nie ma trybu `--execute`.

Kandydat jest dostępny wewnętrznie jako
`chat_with_bot(..., interpretation_mode="facts_v1", interpretation_client=fake, diagnostics=trace)`.
W T026 klient jest atrapą; bez niej jawny wybór facts_v1 użyłby prawdziwego
SDK. Domyślny tryb aplikacji nadal wynosi legacy/V0. Diagnostyka odróżnia
żądania SDK, calls interpretacyjne i wywołania backendu. Jedna interpretacja
może zakończyć się no_search i zerem dispatch; wymuszony call nie dowodzi
poprawności semantycznej. Przykłady T025 i testy nie są pomiarem LLM.

Wyniki 347/347, zamrożony kandydat i pokrycie IRC:
[T026](../specs/001-mvp-stabilization/verification.md#t026--implementacja-ir-1-offline-zakończona).
Istniejące runnery V4/V5 nie wykonują trybu IR-1. T027 ma osobnego
wykonawcę i świeży plan V4/IR-1 z przeglądem adnotacji, payloadami oraz
kosztorysem, opisany poniżej. Płatny pomiar wymaga zgody na ten plan.

## T027 — diagnostyka V4/IR-1

**T027 zakończone 2026-11-18:** 72/72 SDK po osobnej zgodzie, IR-1 nie
kwalifikuje się według IR1-D1 (DEC-16). Raw 22/36 wobec V4 26/36,
replay 25/36 wobec 29/36; koszt referencyjny bez cache 0,026496 USD.
Domyślny legacy/V0 pozostaje. [Raport](../docs/reports/t027_interpretation_2026-11-18.md).
[Protokół i reguła IR1-D1](../specs/001-mvp-stabilization/plan.md#19-t027--diagnostyka-v4ir-1),
[dowody](../specs/001-mvp-stabilization/verification.md#t027--diagnostyka-zakończona).
Nowy wykonawca zachowuje T026 i historyczne runnery. Poniższe polecenia
opisują procedurę dla nowego katalogu; nie wznawiają wcześniejszych pomiarów.

```powershell
venv\Scripts\python.exe evals\run_interpretation_diagnostic.py --check-model --output "dokumentacja pracy\NOWE_T027_model_access.json"
venv\Scripts\python.exe evals\run_interpretation_diagnostic.py --prepare --model-access "dokumentacja pracy\NOWE_T027_model_access.json" --output "dokumentacja pracy\NOWE_T027"
```

check-model wykonuje jeden GET metadanych, bez generacji. Prepare działa
offline i wymaga potwierdzenia widoczności młodszego niż 24 godziny.
Zapisuje 24 pełne payloady, 12 przypadków z adnotacjami po przeglądzie,
harmonogram 72 SDK, źródła/runtime i kosztorys. Nie nadpisuje katalogu.
Rezerwa wykonanego planu wynosiła 0,1637217 USD, zatwierdzony lokalny próg 0,50 USD;
jest to kontrola szacunku, nie gwarancja rachunku. Brak zgody na koszt
w prepared. Zakończonego pakietu nie wznawiać; T009/T012 nadal są wstrzymane.

Dopiero po zatwierdzeniu konkretnego planu, payloadów i progu:

```powershell
venv\Scripts\python.exe evals\run_interpretation_diagnostic.py --execute --output "dokumentacja pracy\NOWE_T027" --approved-plan-sha256 PELNY_ZATWIERDZONY_HASH --approved-budget-usd 0.50
```

Wykonawca sprawdza hashe/semantykę/runtime przed klientem i rezerwuje koszt
przed każdym żądaniem. Wspólne gpt-4o-mini, 1024 tokeny, retry=0, timeout=30 s.
Jedna odpowiedź daje raw ocenę i zależny application_replay bez drugiego
SDK lub katalogu. Symulowany dispatch jest opisany jako simulated_backend_calls;
actual_backend_calls=0. Raport zachowuje provider_response i przelicza oceny,
odróżnia fakty, kanał, decyzję i parametry. Pierwsza awaria API/metadanych
lub zmiana resolved model przerywa przebieg; zwykłe błędy interpretacji
pozostają oceną i nie są ponawiane. Brak selective resume.

Symulacja ma execution_kind=mock, is_model_measurement=false i
actual_model_requests=0. Nawet kwalifikujący wynik diagnostyczny nie włącza
IR-1, nie zmienia aktywnego V0 i nie zalicza ACC. T027 kończy się raportem
i decyzją także przy wyniku negatywnym; pełna kwalifikacja to T010/T013.

## Płatne pomiary i zachowanie raportów

Po T024 gramatyka preflight przepuszcza pięć dawnych fałszywych blokad.
Audyt V4/V5 porównuje stan ochrony z zamrożonym `preflight_blocked`:
blokada ma błąd preflight, a przepuszczenie bez próby modelu ma
`preflight_passed=true`, `passed=null`, `model_decision_correct=null`
i `evaluation_scope=preflight_only`. Nie zalicza to interpretacji modelu.
Każda rozbieżność ze snapshotem zatrzymuje wykonawcę przed klientem płatnym.
Historycznych raportów T021/T023 i dawnych etykiet nie przeliczono.

Świeży dry-run 76 przypadków przewiduje teraz 68 żądań application
(wcześniej 66), dla trzech powtórzeń 204 (wcześniej 198), a plan trzech
wariantów T009 1296 (wcześniej 1278). To przeliczenie przyszłego planu,
bez wywołań API i bez wznowienia wstrzymanej kampanii. Podzbiór V4/V5
32 przypadków nadal ma 384 oceny / 354 planowane wywołania. Zmiana kodu
unieważnia stare zgody/hashe dla nowego wykonania; wymaga nowego protokołu
i osobnego zatwierdzenia przyszłego pomiaru.

### T023 — porównanie V4/V5 po T022

**Zakończone 2026-11-17:** po osobnej zgodzie wykonano cały przebieg 02,
384 oceny / 354 wywołania, bez błędów technicznych. V5 nie kwalifikuje się
według T017-v1 (DEC-13); aktywny V0 pozostaje. Wyniki i koszty obu prób:
[raport](../docs/reports/t023_routing_2026-11-17.md).
Poniższe komendy opisują procedurę, nie polecenie ponownego pomiaru.

Pierwszy zatwierdzony przebieg przerwał błąd zapisu checkpointu Windows;
zachowano 262 oceny i 242 odpowiedzi API. [Raport](../docs/reports/t023_routing_2026-11-17.md).
Nie wznawiać go ani nie łączyć wyników z nowym pełnym przebiegiem.
Poprawiony zapis ponawia tylko lokalne zastąpienie pliku po PermissionError
(pięć oczekiwań, do 1,55 s); trwała awaria nadal przerywa kampanię.
Retry SDK pozostaje 0. Nowy pakiet wymaga osobnej zgody.

```powershell
venv\Scripts\python.exe evals\run_routing_v5.py --prepare --model-access "dokumentacja pracy\2026-11-17_t023\model_access.json" --output "dokumentacja pracy\NOWE_T023"
```

Przygotowanie korzysta z potwierdzenia metadanych GET modelu, bez generacji.
Nowy katalog zawiera `plan.json`, payloady, harmonogram, źródła z hashami
i `state.json` z zerowym licznikiem. Plan obejmuje 384 oceny / maksymalnie
354 wywołania, szacunkową rezerwę ok. 0,87 USD i proponowany lokalny próg
rezerw 1,00 USD. Szczegóły i reguła T017-v1: sekcja 15
[planu](../specs/001-mvp-stabilization/plan.md#15-t023--przygotowanie-wykonania-i-porównanie-v4v5).

Dopiero po osobnym zatwierdzeniu konkretnego planu można wykonać:

```powershell
venv\Scripts\python.exe evals\run_routing_v5.py --execute --output "dokumentacja pracy\NOWE_T023" --approved-plan-sha256 PELNY_ZATWIERDZONY_HASH --approved-budget-usd 1.00
```

Wykonanie sprawdza hashe i runtime przed klientem, narzuca dokładny payload,
limit 354 żądań, 512 tokenów odpowiedzi i retry=0. Rezerwa jest zapisywana
przed żądaniem. To kontrola szacunku, nie gwarancja rachunku; podatki i inne
użycie konta są poza nią. Pierwsza awaria API lub błąd metadanych przerywa
kampanię z checkpointem, bez selektywnego wznowienia. Zwykłe błędy decyzji
są raportowane dla całego zestawu. Lookup pozostaje atrapą; brak zmiany V0.
Symulacje mają execution_kind=mock i is_model_measurement=false.

### Kontrolowane porównanie T009

Pełna kampania jest wstrzymana. Mniejszy pilotaż V0/V2 ma osobny runner:

```powershell
venv\Scripts\python.exe evals\run_routing_pilot.py --dry-run --output "dokumentacja pracy\NOWY_PILOTAZ"
```

20 przypadków, dwa warianty, trzy próby, tylko raw: 120 wywołań. Dry-run
nie wywołuje API. Późniejsze `--execute` jest etapem płatnym wymagającym
potwierdzenia. Odpowiedzi mają limit 512 tokenów, retry jest wyłączone,
a szacowany koszt rezerwowany przed każdym żądaniem podlega kontroli 0,50 USD.
To lokalna ochrona szacunku, nie limit rachunku dostawcy. Podzbiór celowany
nie stanowi końcowej oceny generalizacji ani jakości pełnych rekomendacji.

### Przygotowanie iteracji T014

T009P zakończono; następna iteracja korzysta z osobnego profilu tego runnera:

```powershell
venv\Scripts\python.exe evals\run_routing_pilot.py --profile t014 --dry-run --output "dokumentacja pracy\NOWE_T014"
```

Profil `t014` zamraża V0/V3, te same 20 przypadków i etykiety, trzy rundy
raw/application: 240 ocen i 216 planowanych wywołań (cztery blokady preflight
na każdą grupę application). Obowiązują limity 512 tokenów, retry 0 i lokalna
kontrola rezerw 0,50 USD. `--profile` wybiera przygotowanie; późniejsze
wykonanie odczytuje profil z manifestu i wymaga odrębnej zgody na koszt
oraz payload. Nie uruchamia pełnego T009 ani nie wdraża V3.
Reguła kandydata: sekcja 7 [planu](../specs/001-mvp-stabilization/plan.md).
Stan i dowody: [mapa weryfikacji](../specs/001-mvp-stabilization/verification.md#t0142--przygotowanie-offline-zakończone).

### Przygotowanie V4 w T015

```powershell
venv\Scripts\python.exe evals\run_routing_pilot.py --profile t015 --dry-run --output "dokumentacja pracy\NOWE_T016"
```

Profil `t015` przygotowuje V0/V4: te same 20 przypadków i etykiety, trzy
rundy raw/application, 240 ocen / 216 planowanych wywołań. Limit 512 tokenów,
retry 0 i lokalny próg rezerw 0,50 USD pozostają bez zmian. V3 jest źródłem
V4, ale jego historyczny wynik nie jest kontrolą nowego pomiaru.

Reguła `T015-v1` wymaga m.in. poprawy trzech problematycznych przypadków,
braku nawet pojedynczego pogorszenia per-case i braku dispatch z błędnymi
argumentami semantycznymi. Pełna reguła jest w sekcji 8
[planu](../specs/001-mvp-stabilization/plan.md); wynik nie zalicza MVP.
Przygotowanie nie wywołuje API ani nie zmienia aktywnego V0. Przyszłe
wykonanie jest T016 i wymaga zgody na konkretny payload oraz kosztorys.

### Pełna kampania T009 — wstrzymana

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

### Końcowe zestawy T010

Regresja obejmuje 76 dotychczasowych przypadków. Flaga `--holdout` zachowuje
historyczny v1. Flaga `--holdout-v2` wybiera wyłącznie 40 nowych przypadków.
Plan trzech powtórzeń można sprawdzić lokalnie z katalogu projektu.

```powershell
venv\Scripts\python.exe evals\run_routing_eval.py --holdout-v2 --mode raw --repeats 3 --dry-run
venv\Scripts\python.exe evals\run_routing_eval.py --holdout-v2 --mode application --repeats 3 --dry-run
```

W każdym trybie wypada 120 ocen holdoutu. Regresja ma osobne 228 ocen
w każdym trybie. Stan przeglądu etykiet i identyfikatory wersji są
w [mapie weryfikacji](../specs/001-mvp-stabilization/verification.md#t010--przygotowanie-zestawów).
[Tabela przeglądowa i 12 scenariuszy ręcznych](../specs/001-mvp-stabilization/final-evaluation-cases.md).

`run_llm_eval.py` pozostaje narzędziem zgodnościowym;
`run_final_answer_eval.py` dotyczy historycznej architektury z drugim
wywołaniem LLM i bez `--dry-run` także generuje płatne wywołania API.
