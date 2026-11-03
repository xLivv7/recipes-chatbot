# Rozdzielona ewaluacja routingu

Status: narzedzia pomiarowe wdrozone 2026-10-15; bez nowego live pomiaru.

## Dwa tryby
`evals/run_routing_eval.py --mode raw` mierzy model bez preflight, ale z
produkcyjnym promptem, schematem, temperatura 0.1, auto i parallel_tool_calls=false.
`--mode application` wywoluje rzeczywiste main.chat_with_bot: preflight,
interpretacje, walidacje i dispatch. Wylacznie run_recommendation_tool jest
zastepowany stubem zapisujacym argumenty i zwracajacym puste recommendations.
Nie jest to test rekomendacji ani pelny end-to-end na danych bazy.
Import aplikacji nadal laduje katalog i wymaga dostepu do lokalnej bazy,
ale samo oceniane wyszukiwanie jest zastapione; przepisy/SKU nie sa wysylane.

## Zestaw
Domyslnie oba tryby czytaja te same 76 przypadkow: 64 intencje, 6 routingowych
i 6 application_routing_cases. Cztery nowe to nieobslugiwane wykluczenia,
dwa to znane false positives preflight z oczekiwana semantycznie obsluga.
Nie zmieniono expected istniejacych przypadkow. To zestaw regresyjny,
nie holdout. Zatrzymanie prosby obslugiwanej semantycznie jest bledem
uzytecznosci preflight nawet wtedy, gdy wynika z jego ostroznej polityki.
Pozwala to mierzyc koszt ochrony bez podnoszenia wyniku przez zmiane etykiet.

## Diagnostyka i mianowniki
- model_action: czy model zwrocil jakikolwiek tool call; wiele calli nadal
  oznacza decyzje tool, ale jest osobnym bledem protokolu.
- tool_call_count i raw_tool_calls: liczba oraz nazwy/surowy JSON wszystkich
  calli, takze tych odrzuconych. Brak odpowiedzi/model nieoceniony daje null.
- protocol_valid: dostepne choices i zero lub jedno wywolanie znanego toola.
- arguments_valid: parser JSON, wymagane pola, typy, enumy i sprzecznosci.
  Tylko poprawne pojedyncze wywolanie podlega tej ocenie.
- semantics_correct i field_results: zgodnosc z expected, tylko dla
  wymaganych i zwroconych poprawnych argumentow. Inne przypadki maja null,
  a nie siedem sztucznych bledow pol.
- effective_action: faktyczne tool/no_tool lub error; blad API/protokolu
  nie jest zaliczany jako poprawna odmowa.
- model_decision_correct: model oceniany tylko, gdy zaobserwowano decyzje.
  Poprawne zablokowanie przed API nie trafia do jego mianownika.
- decision_correct: skuteczna decyzja routingu; dla error brak oceny decyzji.
- failure_stage: api, protocol, arguments, decision, semantics lub preflight;
  null dla poprawnego przypadku. Bledne zatrzymanie przez ochrone to preflight.

Raport pokazuje wynik calosci passed/total, aby warunkowe metryki nie
ukrywaly odmow/awarii. Kazda metryka ma passed, total, accuracy; przy braku
ocenialnych przypadkow accuracy=null, nie 100% ani 0%.
API bledy zapisuja tylko klase wyjatku, nie jego tresc. Nieoczekiwane bledy
programistyczne przerywaja runner zamiast stawac sie bledami modelu.

## Uruchomienie
Dry-run nie tworzy klienta i nie wykonuje API:

```powershell
venv\Scripts\python.exe evals\run_routing_eval.py --mode raw --dry-run
venv\Scripts\python.exe evals\run_routing_eval.py --mode application --dry-run
```

Live (platne, uruchamiane osobno):

```powershell
venv\Scripts\python.exe evals\run_routing_eval.py --mode raw
venv\Scripts\python.exe evals\run_routing_eval.py --mode application
```

Domyslne raporty, ignorowane przez Git: evals/raw_routing_eval_report.json
i evals/application_routing_eval_report.json. Kazdy kolejny przebieg danego
trybu nadpisuje jego raport; --output pozwala zapisac nowy plik, np. w
ignorowanym folderze dokumentacja pracy. Stary llm_eval_report.json pozostaje
bez zmian. Stary runner jest zgodnosciowym pomiarem intencji i nie
ma nowej szczegolowej diagnostyki; do nowych porownan uzywac nowego runnera.

W obu trybach mozna podmienic --cases, --routing-cases i --guard-cases
lub ograniczyc dodatnim --limit. Model aplikacji pozostaje gpt-4o-mini;
tryb application odrzuca inny --model, zamiast niejawnie mierzyc inny model.

## Koszt, odtwarzalnosc i granice
Dry-run: 76 zaplanowanych calli raw, 66 application (10 blokad preflight).
To plan wywolan SDK, nie rozliczenie kosztu: SDK moze wewnetrznie ponawiac
zadania. Uruchomienie obu trybow wykonuje niezalezne probki modelu, nie
porownanie tej samej odpowiedzi. Nie wyciagac wnioskow przyczynowych z roznicy
jednego przebiegu; potrzebne powtorzenia i holdout w nastepnym etapie.
Raport zapisuje UTC, prompt, schemat, parametry oraz hashe zrodel/datasetow.
Nieocenione modele przy blokadzie nie dostaja sukcesu. Zachowane sa zarowno
poprawne blokady, jak i koszty false positives. Surowy JSON pochodzi z
kontrolowanych przypadkow; nie nalezy bez osobnej decyzji uzywac realnych
rozmow zawierajacych dane osobowe w tym logowaniu.
Renderer, jakosc katalogu i poprawne wykonanie SQL wymagaja osobnych testow.

Weryfikacja implementacji: 201 testow OK, w tym 12 nowych testow diagnostyki,
obu trybow i mianownikow; baza 0 ERROR, 20 WARNING, 9 INFO. Bez live wywolan.
Referencja: https://developers.openai.com/api/docs/guides/evaluation-best-practices
