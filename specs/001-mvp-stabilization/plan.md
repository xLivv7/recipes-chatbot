# Plan — stabilizacja istniejącego MVP

Status: T005, T006 i T008 wykonane 2026-11-03. Następne: przygotowanie T009.
Zakres i decyzje: [spec.md](spec.md). Warunki ukończenia: [acceptance.md](acceptance.md).
Szczegółowe zadania i ich stan: [tasks.md](tasks.md).

## 1. Podejście

Zachowujemy obecny przepływ LLM → walidacja → backend → renderer i jedną
markę demonstracyjną. Wprowadzamy małe zmiany wynikające z wymagań,
bez dodawania funkcji użytkowych. Wynik kontroli sprzed zmian pozostaje
[punktem odniesienia](../../docs/reports/baseline_2026-10-22.md).

## 2. Kolejność

| Etap | Rezultat |
| --- | --- |
| Punkt wyjścia — wykonany | Zakres, progi, zapis stanu zastanego, mapa dowodów i kontrola bazowa. |
| Organizacja — wykonana | Jeden aktywny pakiet specyfikacji i indeksy dokumentacji. |
| Integralność i błędy — wykonane | INT/ERR wdrożone i sprawdzone; [raport T006](../../docs/reports/t006_2026-11-03.md). |
| Routing — protokół gotowy | ROU-01–ROU-06 i warianty V0/V1/V2 opisane; przygotowanie i pomiar oczekują w T009. |
| Ocena i odtwarzalność | Zestaw ręczny, instrukcja odtworzenia i niezależna ocena po zamrożeniu wariantu. |

Przegląd źródeł pięciu SKU i decyzja o ich podstawie makro są wstrzymane.
Nie podejmujemy zależnych zmian tych produktów. Pozostałe obszary mogą
postępować, ale ACC-03 nie jest przez to uznane za spełnione.

## 3. Zrealizowana zmiana T006: integralność i błędy

Poniższy opis jest planem wykonanej zmiany; nie stanowi polecenia jej
ponownego wdrażania. Wyniki są w raporcie T006, a otwarte zadania w `tasks.md`.

Scenariusze i oczekiwane wyniki są w [spec.md](spec.md#scenariusze-weryfikacji-do-implementacji-w-t006).
W T006 sprawdzić istniejące asercje i dodać testy istotnych luk. Poprawka
ma uniemożliwić zgadywanie zgodności oraz ukrywanie awarii jako pustego wyniku.
Nie powinna zmieniać reguł poprawnych rekomendacji ani otwierać nowych funkcji.
Po zmianie uruchomić zależne kontrole; rozszerzać weryfikację tylko w razie
nowych niepewności.

### Granice techniczne T006

- `core/recommendations.py`: jawna kontrola polityk kandydatów i przygotowania,
  odrębny rozpoznawalny błąd danych zamiast szerokiego `except Exception`.
- Wspólny typ błędu danych w małym module bez importowania bazy lub `main`,
  aby nie tworzyć zależności cyklicznych. Nazwa typu jest wyborem implementacyjnym.
- `main.py`: przechwytywać wyłącznie rozpoznany błąd domenowy przy backendzie,
  zwrócić ERR-02 i zapisać ERR-05. Nie maskować nieoczekiwanych wyjątków.
- `core/validation/validators_diet.py`: brak polityki używanego konceptu
  podnieść z WARNING do ERROR. Legalne NULL laktozy pozostaje bez zmiany.
- Testy: kontrolowane katalogi, niezależne oczekiwania i mock granicy LLM;
  brak modyfikacji rzeczywistej bazy w celu wywołania awarii.
- Bez zmiany schematu bazy, promptu, reguł SKU, statusów laktozy,
  wartości makro, pięciu SKU oraz progów i etykiet ewaluacyjnych.
- Najpierw sprawdzić INT/ERR i regresję zależnych ścieżek; kontrola pełnego
  istniejącego zestawu i walidatora kończy weryfikację poprawki. Zapisać
  pominięcia i wersję danych. Nie ma potrzeby płatnej ewaluacji LLM.

## 4. Eksperymenty i dowody

- Rozdzielić testy deterministyczne, ocenę LLM i przegląd czytelności.
- Wybrać wariant promptu na regresji; holdout służy końcowej ocenie.
- Zamrozić konfigurację, przypadki i progi przed kampanią.
- Nowe raporty zapisywać osobno, z commitem i wersją danych.
- Nie przenosić historycznych wyników na zmienioną wersję kandydującą.

W etapie reorganizacji nie wykonujemy płatnych pomiarów ani zmian bazy.

## 5. Protokół eksperymentu routingu T009

### Dane i konfiguracja

- Punkt wyjścia kodu: `97638cf`. V0 z tego commita zachowuje się jako kontrola
  nawet po dodaniu instrumentacji wariantów. Wszystkie warianty używają
  tej samej instrumentacji, a nie różnych implementacji runnera.
- Dane rozwojowe: `intent_cases.json` + `routing_cases.json` +
  `application_routing_cases.json` w `evals/`: 76 przypadków, w tym
  66 tool i 10 no_tool. Bez `--limit`, bez holdoutu i zmiany etykiet.
- Kontrola preflight offline: 10 blokad, z czego `guard_005` i `guard_006`
  to znane false positives. Pozostają błędami. Zmiana ochrony wymagałaby
  osobnego eksperymentu i nie należy do tego porównania.
- Model `gpt-4o-mini`, temperatura 0.1, `tool_choice=auto`,
  `parallel_tool_calls=false`, marka Winiary, ten sam schemat i parser.
  Zapisać resolved model z odpowiedzi. Nie wnioskować o porównywalności,
  jeśli w kampanii zmieni się rzeczywista wersja modelu.
- Każdy wariant: 3 pełne powtórzenia raw i 3 application, te same ID
  i kolejność przypadków. W rundzie 1 kolejność wariantów V0/V1/V2,
  w rundzie 2 V1/V2/V0, w rundzie 3 V2/V0/V1; w wariancie raw przed application.
  Rotacja ogranicza zależność od pory pomiaru, nie usuwa zmienności modelu.
- Wyszukiwanie jest stubowane jak w obecnym runnerze. Do API nie trafiają
  przepisy, SKU ani prywatne rozmowy. Nie mierzymy jakości SQL lub renderera.

Offline potwierdzono liczebności i zapisano hashe wejść w
[plan_inputs.json](../../dokumentacja%20pracy/2026-11-03_t008/plan_inputs.json).
To identyfikacja punktu wyjścia, nie raport jakości ani zamrożenie niegotowych promptów.

### Przygotowanie offline przed kampanią

1. Dodać izolowany wybór wariantu w warstwie eksperymentalnej, bez zmiany
   aktywnego promptu aplikacji. Obecny runner nie ma flagi wyboru promptu:
   nie wystarczy wydać istniejącego polecenia z wymyślonym parametrem.
2. Raw i application muszą korzystać z tego samego wybranego promptu.
   Przy application podstawiać tylko konstrukcję promptu i klienta pomiarowego;
   ochrona, walidacja i dispatch nadal wykonują rzeczywisty kod aplikacji.
   Raw korzysta dziś z lokalnego importu `build_system_prompt` w
   `evals/run_llm_eval.py`: samo podstawienie funkcji w `main` nie zmieni
   tego aliasu. Test musi potwierdzić treść faktycznie wysłaną w obu trybach.
3. Sprawdzić, że V0 jest identyczny z bazą, V1/V2 zmieniają tylko ustalone
   fragmenty, a wszystkie przykłady mają te same pełne argumenty. Istniejące
   testy dopasowujące ramki Markdown pozostają kontrolą V0; nie narzucać
   ramek V2 ani nie usuwać kontroli kompletności jego pól.
4. Testami z mockami zweryfikować routing tool/no_tool, tekstowy JSON,
   wiele calli, błędne argumenty, API error, zapis wariantu i pełnego raportu,
   kolejność rund oraz brak wywołań przy dry-run. Nie wymaga to żywego modelu.
5. Przygotować wyliczenia metryk podzbiorów opisanych poniżej. Obecny raport
   ma wyniki per-case, lecz nie wszystkie wymagane agregaty podzbiorów.
6. Zamrozić commit instrumentacji, pełne prompty, hash schematu i trzech
   zbiorów, wersje środowiska, konfigurację i tę wersję protokołu.

### Rozmiar i zapis kampanii

Dla 3 wariantów: **1368 ocen i planowo 1278 wywołań SDK**:
na wariant 228 raw + 228 application ocen, 228 + 198 wywołań.
To nie jest liczba żądań wewnętrznych retry ani koszt pieniężny. Budżet
tokenów/kosztów trzeba oszacować z gotowych promptów przed kampanią.
Niniejszy etap nie uruchamia tych wywołań.

Każda runda/tryb/wariant otrzymuje odrębny raport i identyfikator kampanii.
Agregator wymaga dokładnie jednej oceny dla każdego ID w każdej z trzech
rund i wariantów; nie wolno złączyć checkpointu z jego ukończoną wersją.
Raport zachowuje prompt, hashe, ustawienia, request IDs, wyniki per-case,
finish_reason, tekst no_tool i etap błędu. To kontrolowane wypowiedzi testowe;
nie wprowadzamy logowania treści rzeczywistych użytkowników do aplikacji.

Niepełny przebieg lub błąd API zachować z opisem. Nie usuwać porażek i nie
ponawiać selektywnie przypadków. Do porównania potrzebne są pełne grupy
bez błędów API; ewentualne powtórzenie ma nowy identyfikator całej kampanii
i osobne raporty. Zmiana wariantu lub etykiety w trakcie unieważnia porównanie.

### Metryki

W każdym wariancie i trybie pokazać dokładne liczniki/mianowniki:

- `passed/228` oraz `passed/198` dla 66 obsługiwanych próśb × 3;
- przypadki stabilne `stable/76` i pomocniczo `stable/66` obsługiwanych;
- decyzja no_tool `correct/30`, a dla ACC-11 także oddzielne grupy
  nieobsługiwanych wykluczeń/alergii/sprzeczności: łącznie 9 przypadków
  ACC-11 × 3 = 27 ocen (grupy RSC-03/04 w specyfikacji);
- fałszywe blokady preflight i poprawne blokady aplikacji;
- błędy API, protokołu, walidacji, decyzji oraz semantyki;
- warunkowa poprawność pól z mianownikami; brak wywołania pozostaje
  niepowodzeniem ogólnym, a nie znika z oceny;
- diagnostycznie: liczba JSON-ów w no_tool_content, które po odczycie samym
  parserem odpowiadają expected. Nie używać eval, nie wykonywać takiego JSON-a
  i nie zaliczać go jako sukcesu. Raportować tylko na podzbiorze wymagającym toola.

### Reguła wyboru przed poznaniem wyników

1. Wariant kwalifikuje się na regresji, jeśli application spełnia co najmniej
   90% wszystkich ocen, 90% obsługiwanych próśb, 85% przypadków stabilnych
   i wszystkie ustalone przypadki ACC-11 bez wyszukiwania. To te same progi
   co w `acceptance.md`; nadal wymagają osobnej oceny na nowym holdoucie.
2. Wśród kwalifikujących się wybieramy największą liczbę poprawnych ocen
   application, następnie najwięcej stabilnych przypadków. Remis rozstrzyga
   preferencja prostszej zmiany: V0, potem V1, potem V2. Nie wybieramy
   najlepszego pojedynczego przebiegu ani korzystniejszej metryki raw.
3. Jeżeli zwycięża V0, pozostaje bez zmian. Jeżeli żaden wariant nie spełnia
   progów, nie deklarujemy naprawy; zachowujemy V0 i raportujemy luki.
   Kolejna hipoteza wymaga nowej wersji planu przed kolejnym pomiarem.
4. Pokazać nowe i utrwalone błędy względem V0 per-case, także wtedy, gdy
   średnia wzrosła. Niezależne próbki nie dają dowodu istotności lub przyczyny.
5. Wybór kandydata nie oznacza automatycznej podmiany promptu w aplikacji.
   Najpierw raport i przegląd regresji; potem niezależna ocena w T010/T013.

Podstawę i scenariusze ROU utrzymujemy w `spec.md`. Realizacja tego protokołu
jest T009, nie częścią zakończonego T008.
