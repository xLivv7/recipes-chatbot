# Plan — stabilizacja istniejącego MVP

Status: T005, T006, T008 i część offline T009 wykonane.
Płatny etap T009 wstrzymany na decyzję autorki z 2026-11-03.
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

**Bieżący stan:** protokół pozostaje projektem ewentualnego późniejszego
pomiaru. Autorka wybrała tylko przygotowanie offline. Nie uruchamiać
kampanii API ani nie traktować poniższych kroków jako bieżącego polecenia.
Przed ewentualnym wznowieniem trzeba zweryfikować aktualność wejść i kosztu;
zmienione pliki wymagają nowego zamrożenia, nie obchodzenia kontroli hashy.

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

## 6. Mały pilotaż T009P — osobno od wstrzymanej pełnej kampanii

Status: wykonano po zgodzie autorki; [raport](../../docs/reports/routing_pilot_2026-11-03.md).
Reguła wyboru zachowała V0; V2 nie spełnił warunku granic no_tool.
Poniższe etapy opisują wykonany proces, nie zgodę na kolejny pomiar.

Autorka uzgodniła kierunek małego eksperymentu przed przyszłą pełną oceną.
Protokół i reguła wyboru są w sekcji pilotażu `spec.md`. Kod:
`evals/run_routing_pilot.py`; 20 zamrożonych przypadków w
`evals/routing_pilot_cases.json`, V0/V2, raw, trzy próby, 120 wywołań.

Etapy: specyfikacja → instrumentacja i testy offline → manifest i kosztorys
→ potwierdzenie konkretnego payloadu/kosztu → wykonanie → raport i rekomendacja.
Nie uruchamiać starej pełnej kampanii zamiast pilotażu. Nie zmieniać aktywnego
promptu na podstawie samej wygranej na małym zbiorze.

Po ewentualnym wyborze kandydata: szersza regresja routingu i niezależny
holdout, osobno testy backendu i katalogu, ocena renderera i czytelności,
a na końcu scenariusze całego przepływu. To rozwinięcie obecnej mapy ACC,
nie nowa funkcjonalność ani obietnica wykazania poprawy. Mniejszy pilotaż
ma inne limity generacji i retry niż pełny plan, więc wymaga własnego raportu.

## 7. T014 — następna iteracja poprawy routingu

1. **T014.1 — wymagania:** zapisane ROU-07–ROU-10 w specyfikacji. Wyniki
   T009P pozostają bez zmian. Doprecyzowanie dotyczy instrukcji modelu,
   nie dodania obsługi alergii ani zmiany reguł aplikacji.
2. **T014.2 — przygotowanie offline:** zaprojektować V3 jako ograniczony diff
   względem V2, ujednoznaczniający priorytet no_tool. Zachować te same przykłady,
   słowniki i znaczenie argumentów. Dodać izolowaną obsługę V3 w ewaluacji,
   testy treści i wspólnego promptu w obu trybach, kosztorys i dry-run.
   Nie zmieniać aktywnego `main.build_system_prompt`, preflight ani danych.
3. **T014.3 — porównanie:** zakres potwierdzony offline w T014.2:
   V0/V3, te same 20 przypadków rozwojowych, 3 rundy, raw i application.
   To 240 ocen i planowo 216 wywołań API przy obecnych 4 blokadach
   preflight w tym podzbiorze. Limit odpowiedzi 512, retry 0, timeout 30 s,
   temperatura 0,1; lokalna kontrola rezerw do 0,50 USD. Wykonanie dopiero po
   przedstawieniu i zatwierdzeniu konkretnego manifestu, payloadu i kosztu.
4. **T014.4 — decyzja:** przejrzeć wyniki i regresję; dopiero wtedy rozważyć
   zastąpienie V0. Dla wdrożenia potrzebna jest odrębna jawna decyzja,
   testy aplikacji z nowym promptem i zapis wersji. Sam pomiar nie wdraża V3.

Reguła kandydata, do sprawdzenia przed kampanią: komplet ocen bez błędów
API, jeden resolved model, brak ucięć; wszystkie 18 prób no_tool poprawne
osobno w raw i application; wynik raw V3 lepszy od równocześnie mierzonego
V0, liczba stabilnych przypadków raw nie mniejsza oraz wynik application
nie gorszy. Brak nowego stałego niepowodzenia przypadku poprawnego 3/3
w kontroli. Jeśli warunki nie są spełnione, pozostaje V0; nie zmieniać
reguły ani etykiet po obejrzeniu wyników. Progi końcowej akceptacji ACC
pozostają bez zmian — ta reguła dotyczy tylko kandydata w małej iteracji.

Zestaw był już ujawniony i służy rozwojowi V3, więc nie jest holdoutem.
Raport ma pokazać per-case również błąd raw zatrzymany przez preflight,
bez zaliczania ochrony jako sukcesu modelu. Pełna niezależna ocena nadal
należy do późniejszych zadań; T014 nie uruchamia wstrzymanej kampanii T009.

Przygotowanie T014.2 zakończono 2026-11-03: V3 dodaje do V2 jeden akapit
`PRIORYTET ZAKRESU` przed parametrami; pozostały tekst, w tym pięć pełnych
przykładów, jest identyczny. `run_routing_pilot.py --profile t014 --dry-run`
przygotowuje V0/V3. Domyślny profil nadal opisuje wcześniejsze V0/V2.
Kolejność wariantów w rundach: V0/V3, V3/V0, V0/V3; dla każdego wariantu
najpierw raw, potem application. Wyszukiwanie jest atrapą, a preflight,
walidacja i dispatch pochodzą z aplikacji. To nie pomiar jakości rekomendacji
na rzeczywistych danych. Kosztorys i dowody są w `verification.md`.

T014.3 wykonano 2026-11-03 na polecenie autorki, po commicie instrumentacji
`261a04f`. Wszystkie 240 ocen i 216 wywołań są kompletne; 0 błędów API
i ucięć. Uzgodniona reguła wskazała kandydata V3: raw 55/60 wobec 43/60 V0,
application 53/60 wobec 42/60, no_tool 18/18 w każdej grupie.
[Raport](../../docs/reports/t014_3_routing_2026-11-03.md) pokazuje także
pozostałe błędy i niestabilną regresję `intent_032`. Nie zmieniono progów
ani reguły po wynikach.

T014.4 zakończono 2026-11-03 decyzją DEC-07: **pozostawić V0; potrzebna
kolejna hipoteza**. Kwalifikacja V3 w T014.3 pozostaje ważna. Przegląd
wdrożeniowy wskazał pominięcie diety w trzech wywołaniach atrapy backendu,
utrwalone błędne odmowy i niestabilną regresję. 88,33% application oraz
83,33% obsługiwanych próśb nie dowodzą gotowości MVP. Nie wprowadzono
dodatkowego warunku do zakończonego wyboru kandydata i nie wdrożono V3.
[Dowody przeglądu](verification.md#t0144--przegląd-i-decyzja-zakończone).
Testy wdrożenia nowego promptu nie mają zastosowania, ponieważ nie nastąpiła
podmiana; przegląd wykonano offline na zapisanych odpowiedziach.

## 8. T015 — przygotowanie kolejnej hipotezy routingu

Zadanie planowane, nie realizacja w ramach T014.4. Kolejność:

1. Opisać hipotezę i ograniczony zakres kolejnego wariantu na podstawie
   `intent_004/010/032`; odróżnić brak wywołania od wywołania z błędną dietą.
   Powiązać wymagania i scenariusze z ROU, bez nowych funkcji ani zmiany expected.
2. Ustalić regułę porównania przed nowym pomiarem. Jawnie oceniać także
   niestabilne regresje i przekazanie błędnych wymagań do backendu.
   Nie zmieniać wstecznie reguły lub wyników T014.3.
3. Dopiero potem przygotować wariant eksperymentalny i kontrole offline:
   prompt wspólny dla raw/application, dotychczasowe przykłady, kontrasty
   obsługiwanych próśb i granic no_tool, walidacja, dispatch i brak fallbacku JSON.
4. Zamrozić wejścia i przygotować dry-run oraz kosztorys kolejnego pomiaru.
   V0 pozostaje aktywny. Płatny etap wymaga osobnej decyzji dotyczącej
   konkretnego zakresu; T015 go nie obejmuje i nie wznawia T009 ani T012.
