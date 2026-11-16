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

T015 jest odrębnym zadaniem po T014.4. Kolejność realizacji:

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

### Zamrożony protokół do przygotowania w T015

Hipoteza i scenariusze RSC-09–RSC-12 są w specyfikacji. Porównanie V0/V4
sprawdza cały wariant względem aktywnej konfiguracji; nie izoluje nowego
akapitu względem V3. Ten sam podzbiór 20 przypadków i expected, bez holdoutu.
Trzy rundy V0/V4, V4/V0, V0/V4; w każdym wariancie raw, potem application.
240 ocen / 216 planowanych wywołań przy obecnych czterech blokadach preflight.
Model gpt-4o-mini, temperatura 0,1, auto, parallel_tool_calls=false,
limit odpowiedzi 512, retry 0, timeout 30 s; lokalny próg rezerw 0,50 USD.
Kosztorys przeliczyć dla V4; nie uruchamiać API w T015.

Reguła kandydata **T015-v1**, ustalona przed nowym pomiarem:

1. Pełne 240 ocen, niezmienione etykiety i wejścia, bez błędów API i ucięć,
   jeden resolved model dla odpowiedzi z rzeczywistym wywołaniem.
2. V4: wszystkie 18 no_tool poprawne osobno w raw i application.
3. Każdy z `intent_004/010/032` poprawny 3/3 osobno w obu trybach.
4. V4 lepszy łączny wynik od równocześnie zmierzonego V0 w obu trybach;
   liczba przypadków stabilnych nie mniejsza od V0 osobno w obu trybach.
5. Application V4: co najmniej 90% wszystkich ocen, 90% obsługiwanych
   i 85% przypadków stabilnych. Porównywać ułamki, nie zaokrąglone procenty.
   To warunek małego porównania, bez zaliczania ACC na regresji lub holdoucie.
6. **Brak jakiegokolwiek pogorszenia per-case** względem V0: kandydat nie może
   mieć mniej poprawnych prób dla żadnego ID, osobno w raw i application.
   Dotyczy także 3/3 → 2/3 i pogorszeń już niestabilnego przypadku.
7. **Zero wywołań backendu z błędną semantyką** dla obsługiwanych próśb V4
   w application. Raportować takie wywołania także dla V0. Brak wywołania
   pozostaje błędem wyniku ogólnego, a nie sukcesem naprawy semantyki.

V4 kwalifikuje się wyłącznie przy spełnieniu wszystkich warunków. W przeciwnym
razie wybór pozostawia V0 i pokazuje przyczyny. Kwalifikacja nie wdraża promptu:
wymagany jest przegląd raportu oraz jawna decyzja. Reguła T014.3 pozostaje
historycznie bez zmian; nie przeliczać jej według T015-v1.

T016 jest odrębnym zadaniem pomiaru V0/V4 i przeglądu kandydata. Przygotowanie
T015 nie upoważnia do jego kosztu; przed startem przedstawić konkretny manifest,
payload i kosztorys do zatwierdzenia. Zachować raport niepełny i zatrzymać się
po błędzie API, bez selektywnego wznawiania lub zmiany expected.

T015 zakończono offline 2026-11-03: V4 dodaje do V3 jeden akapit, zachowując
pięć przykładów. Profil `t015` w `run_routing_pilot.py` przygotowuje V0/V4
i stosuje T015-v1; T014 nadal korzysta ze swojej pierwotnej reguły.
Wykonano 11 nowych testów i pełną regresję 265/265 bez pominięć.
Manifest, kosztorys i dowody są w sekcji T015 `verification.md`.
W samym T015 nie wykonano pomiaru jakości V4 ani zmiany aktywnego promptu.

T016 wykonano 2026-11-03 na polecenie autorki: 240 ocen, 216 wywołań,
bez błędów API i ucięć. V4 poprawił wynik do 58/60 raw i 57/60 application,
ale nie przeszedł T015-v1. `intent_032` dostał niezamówione fish:
regresja raw 3/3 → 1/3, application 3/3 → 0/3 i trzy błędne wywołania
atrapy backendu. Docelowe `intent_004/010` przeszły poprawnie 3/3 w obu trybach.
DEC-08 pozostawia V0, bez zmiany reguły lub expected po wynikach.
[Raport i przegląd](../../docs/reports/t016_routing_2026-11-03.md).

## 9. T017 — diagnoza relacji diet/protein i specyfikacja poprawki

**Zakończone 2026-11-16, offline.** Rezultat: ROU-12–17, macierz zgodności
i DP-01–28 w `spec.md`, poniższa diagnoza, hipoteza i protokół. Podstawa:
DEC-08/09, audyt INS-01–08 oraz istniejące rozwojowe expected. Nie wdrożono
zmiany instrukcji i nie wykonano pomiaru modelu.

### Diagnoza i ograniczenia dowodów

| Obserwacja | Wniosek i granica |
| --- | --- |
| T016: intent_032, V4, jedno narzędzie i top_n=4 we wszystkich 6 próbach; fish zamiast none w 2/3 raw i 3/3 application. | To niezamówione zawężenie źródła białka, a nie brak obsługi czterech propozycji. Poprawne raw/application: odpowiednio 1/3 i 0/3. |
| Trzy błędne próby application dotarły do atrapy backendu. | Parser nie wykrywa rozbieżności z tekstem prośby. Nie badano wyniku rzeczywistego katalogu; nie twierdzić, że baza zwróciła konkretne błędne dania. |
| Pescetarian/fish jest legalne, gdy użytkownik jawnie chce rybę. | Nie blokować tej kombinacji w parserze i nie przepisywać fish na none po odpowiedzi modelu. |
| V4 i opis protein_preference zabraniają wyprowadzania fish z diety. Pięć demonstracji ma wyłącznie protein=none, bez pescetarian i kontrastów. | Brak demonstracji jest kandydatem na przyczynę; zgodność samych reguł nie gwarantuje ich przestrzegania. Audyt nie ustala przyczynowości. |
| INS-02: dwie ogólne reguły V4 mówią „bez mięsa → vegetarian”, a intent_020 dopuszcza ryby. | Potrzebna reguła pierwszeństwa DEC-09. To odrębna luka; intent_032 nie zawiera „bez mięsa”. |
| INS-01 poprawiono już w T018. | Nowy pakiet wejściowy różni się od T016. Dawny wynik V4 nie może być kontrolą nowego V5. |

### Mapa kontrastów i scenariuszy

| Grupa | Istniejące ujawnione przypadki / expected | Nowe scenariusze kontraktu | Sprawdzana reguła |
| --- | --- | --- | --- |
| Dopuszczenie ryb | intent_011/020/032/050: pescetarian/none. | DP-02/05/08/28. | ROU-12/14/15; dieta lub zgoda nie żąda fish. |
| Jawna ryba | intent_010/016/029/045/060: none/fish. | DP-03/06/07/21. | ROU-12/14; zachować fish, a pescetarian dodać tylko z odrębnej przesłanki. |
| Domyślne vegetarian i jawne diety | intent_004/014/027/028/035; kontrola vegan intent_025/062. | DP-01/04/14/25/26. | ROU-12/13; nie wnioskować z kategorii ani osłabiać jawnej diety. |
| Mięso a cel białkowy | intent_012/023/037/043: none/meat; intent_003/018/026/033/057: protein=none. | DP-09/10/11/27. | ROU-14; cel nie wybiera źródła, dopuszczenie nie wymaga obecności. |
| Negacje | Brak osobnych kontrastów diet/protein we wskazanej grupie; nie przypisywać im wyników. | DP-12/13/22/23/28. | ROU-15; cofnięcie wymogu różni się od zakazu. |
| Sprzeczność lub nieobsługiwane wykluczenie | routing_006 oraz routing_001–004, guard_001–004 pozostają no_tool. | DP-15–19/24. | ROU-07/11/13/15/16; bez pominięcia wymagania i bez dispatch. |
| Pozostałe pola i kanał | intent_032: top_n=4; intent_004/010: utrzymać naprawione zachowanie; intent_059: liczba/czas/ograniczenie. | DP-20/21. | ROU-17; zmienia się tylko jawnie dopowiedziane źródło, reszta argumentów stała. |

To mapa istniejących etykiet i planowanych kontroli. Poza 20 przypadkami
T016 nie przypisano starych wyników V4 innym ID. DP-01–28 mają 22 prośby
tool i 6 no_tool. Nie są demonstracjami V5 ani nowym końcowym holdoutem.
INS-06 pozostaje osobnym problemem: fałszywe blokady guard_005/006 są
błędami application, nawet gdy odpowiedź raw byłaby poprawna.
Kontrola nowych DP wykazała kolejne fałszywe blokady: DP-02/03/22,
z powodu ogona po przecinku w gramatyce wykluczeń. Dla nich API nie
jest wywoływane; expected tool pozostaje bez zmian. Naprawa preflight
wymaga osobnej specyfikacji i implementacji, poza T017 i przygotowaniem V5.

### Hipoteza i granice następnej zmiany

H-T017 ocenia cały wariant V5: kontrastowe demonstracje plus minimalne
ujednoznacznienie INS-02 powinny ograniczyć dodawanie fish bez żądania,
zachowując jawne fish, diety, kanał i granice no_tool. Nie izoluje wpływu
pojedynczej demonstracji ani poprawki zdania; do tego potrzebny byłby
osobny eksperyment. Reguł nie dodajemy kolejny raz bez zmiany demonstracji.

T021 przygotuje V5 w formacie V4. Dopuszczone poza demonstracjami są tylko:
uzgodnienie dwóch bezwarunkowych sformułowań „bez mięsa” z ROU-12/13
oraz neutralne wprowadzenie obejmujące wywołania i no_tool według T019.
To jawne uszczegółowienie wcześniejszego warunku zachowania tekstu V4,
aby nowy wariant nie przeczył własnym przykładom. Pozostałe instrukcje,
schemat po T018, parser, preflight, backend i renderer pozostają stałe.
Nie podmieniać aktywnego V0, historycznych V0–V4 ani expected. T020
nie jest zależnością; wiele celów nie wchodzi do tego wariantu.

### Protokół przyszłej weryfikacji T017-v1

1. **Przed pomiarem:** T019 ustala no_tool, T021 przygotowuje V5 i mały
   zestaw diagnostyczny z pokryciem powyższych grup. Zachować historyczny
   podzbiór 20 przypadków jako regresję, wskazać wybrane dodatkowe ID,
   pełne expected, role demonstracja/diagnostyka i mapę pokrycia. Zapytania
   diagnostyczne muszą różnić się od demonstracji; nie używać końcowego
   holdoutu. Zamrozić hashe wszystkich wejść i dokładne liczebności.
2. **Kontrola offline:** sprawdzić argumenty parserem, wszystkie 12 par
   macierzy, zgodność przykładu z kontraktem i ograniczony diff V4/V5.
   Testy z atrapą sprawdzają kanał i dispatch, nie rozumienie języka.
   Preflight raportować osobno; nie zmieniać expected, aby ukryć blokadę.
3. **Dopiero osobno zlecony pomiar:** świeże V4/V5, wspólny schemat po
   T018 i identyczne ustawienia: gpt-4o-mini, temperatura 0,1, auto,
   parallel_tool_calls=false, limit 512, retry=0, timeout=30 s.
   Trzy rundy w kolejności V4/V5, V5/V4, V4/V5; dla każdego wariantu raw,
   potem application. Lookup zastąpić atrapą. Jawnie zapisać różnicę wobec
   konfiguracji produkcyjnej. Koszt, rezerwę i liczbę wywołań ustalić
   przed startem; T017/T021 nie uruchamiają API i nie wznawiają T009/T012.
4. **Metryki:** osobno decyzja tool/no_tool, kanał, poprawność parsera,
   pełna semantyka, pomyłki diet/protein, niezamówione fish, utracone jawne
   fish, stabilność 3/3 i każdy błędny dispatch. Poprawny JSON w content
   pozostaje błędem kanału; brak wywołania dla prośby tool jest porażką.
   Wynik application obejmuje preflight, a wynik raw samą interpretację.
5. **Warunki kandydata:** pełny uzgodniony pomiar, niezmienione wejścia,
   jeden resolved model, bez błędów API i ucięć; wszystkie no_tool poprawne
   w obu trybach; intent_004/010/032 i wybrane diagnostyczne kontrasty
   diet/protein poprawne 3/3 w obu trybach; zero błędnych semantycznie
   dispatch V5. W application co najmniej 90% wszystkich ocen, 90% tool
   i 85% przypadków stabilnych. Żaden ID nie może mieć mniej sukcesów
   niż równocześnie mierzony V4, osobno raw/application. Porównywać ułamki.
   Znane fałszywe blokady zachować w raporcie. Jeśli uniemożliwią spełnienie
   warunków dla wybranego zestawu, kandydat nie kwalifikuje się; nie usuwać
   ich po wynikach ani nie deklarować naprawy całej aplikacji samym promptem.
6. **Ocena hipotezy i decyzja:** potrzebny jest spadek liczby niezamówionych
   fish względem świeżego V4, osobno w obu trybach, bez utraty jawnych fish
   i warunków z punktu 5. Gdy V4 nie popełni tego błędu lub będzie remis,
   brak podstaw do twierdzenia o poprawie i wyboru V5 z tej hipotezy.
   Wynik negatywny również kończy eksperyment raportem; nie zmieniać
   kryteriów po wynikach. Kwalifikacja nie oznacza wdrożenia ani zaliczenia
   ACC na danych rozwojowych. Aktywny V0 wymaga odrębnej decyzji wdrożenia.

T017-v1 jest planem nowego porównania, nie zmianą historycznego T015-v1.
Dokładny zestaw, manifest i kosztorys zostaną zapisane w T021 przed API;
sam T017 kończy diagnozę i specyfikację. Kontrole i hashe: sekcja T017
w `verification.md`.

## 10. T018 — usunięcie konfliktu INS-01

Zakres zlecony przez autorkę 2026-11-16: ROU-11, wyłącznie opis wspólnego
narzędzia `get_recommendations`. Zastąpić bezwarunkowe „użyj zawsze”
warunkiem zgodności wszystkich wymagań z zakresem i jawnymi wyjątkami
no_tool. Następnie sprawdzić, że różnica dotyczy tylko opisu funkcji,
oraz uruchomić istniejącą regresję offline z blokadą rzeczywistego API.

Zmiana jest widoczna w aktywnej aplikacji i we wszystkich runnerach
korzystających z RECIPE_TOOLS. Prompt systemowy pozostaje V0, ale pakiet
instrukcji ma nowy opis funkcji. Historyczne wyniki i kopie źródeł zachować;
nowy pomiar wymaga zamrożenia aktualnego opisu, bez przypisywania mu
wyników uzyskanych ze starszym schematem. W chwili wykonania T018 T017
pozostawało w toku; jego późniejsze ukończenie opisuje sekcja 9.

Wykonano 2026-11-16: różnica obiektów RECIPE_TOOLS obejmuje tylko
`function.description`. Istniejąca regresja offline 265/265, bez błędów
i pominięć. Dowody w sekcji T018 `verification.md`. Nie wykonano nowego
pomiaru jakości modelu ani nie przypisano poprawce wyników T016.

## 11. T019 — kontrakt odpowiedzi no_tool

Zadanie projektowe na podstawie DEC-10 / INS-03. Można rozpocząć równolegle
z T017; granice sprzecznych preferencji muszą być zgodne z jego kontraktem.

1. Opracować tabelę sytuacja → oczekiwana decyzja → działanie backendu
   → komunikat. Ująć brak wyszukiwania, brak wyników po wyszukiwaniu,
   awarię API i niepoprawne wywołanie jako odrębne sytuacje.
2. Określić odpowiedzialność modelu i aplikacji: brak tool_calls, znaczenie
   content, pochodzenie przyczyny oraz komunikat ogólny przy braku pewnego
   powodu. Uwzględnić istniejące komunikaty preflight i dozwolone domyślne
   parametry. Projekt nie może zakładać, że każdy brak wywołania oznacza
   poprawną odmowę lub świadome rozpoznanie nieobsługiwanego wymagania.
3. Zapisać kontrakt, granice przyszłej zmiany i scenariusze offline:
   poprawne no_tool, błędna odmowa obsługiwanej prośby, JSON w content,
   brak dispatch oraz komunikat bez twierdzenia, że przeszukano pustą bazę.

Warunek ukończenia: kontrakt i tabela decyzji w specyfikacji oraz plan
weryfikacji powiązany z ACC-05/06/07/09/11. Implementacja, ewentualny nowy
sygnał powodu odmowy i pomiar dostaną osobne zadania po określeniu rozwiązania.
T019 nie wprowadza wieloturowego dialogu i nie uruchamia API.

## 12. T020 — projekt wielu celów żywieniowych

Zadanie projektowe na podstawie DEC-11 / INS-07, obejmujące istniejące cele
low_kcal, high_protein i keto. Nie rozszerza automatycznie kategorii, diet
lub pozostałych pól do list. Prace projektowe można rozpocząć niezależnie;
zachowanie braku obsługi/spełnienia zestawu uzgodnić z T019.

1. Zdefiniować semantykę kombinacji: wymagania jednoczesne, preferencje,
   priorytety, duplikaty i stan bez celu. Rozróżnić filtr od rankingu.
   Dla low_kcal + keto określić znaczenie „niskokaloryczne”: dzisiejszy
   kod preferuje niższą kaloryczność, ale nie egzekwuje limitu kcal.
   Wybrać i uzasadnić semantykę pozostałych połączeń oraz brak wyniku
   bez cichego usuwania wymagań. Nie zakładać z góry, że lista rozwiązuje logikę.
2. Zaproponować kontrakt danych, wartości domyślne i zgodność pojedynczych
   celów; przeanalizować wpływ na opis narzędzia, parser, dobór SKU,
   obliczenia dla finalnych składników, filtrowanie, ranking, normalizację,
   renderer i format wyników ewaluacji. Oceniać wartości po doborze SKU.
3. Przygotować scenariusze dla pojedynczych celów, par i pełnego zestawu,
   duplikatów, pustego wyboru, niepoprawnych danych i braku wyników.
   Wskazać potrzebne aktualizacje ACC, ocenę zakresu MVP, sposób migracji
   i podział przyszłej implementacji na zadania. Nie zmieniać ocen historycznych.

Warunek ukończenia: projekt semantyki, danych i rankingu, scenariusze,
analiza wpływu oraz plan migracji/implementacji. Obecny kontrakt jednego
nutrition_goal i granica Z-04 pozostają obowiązujące dla działającej wersji.
To zlecenie projektu; implementacja i zmiana zakresu wykonywanej wersji
zostaną opisane osobno. T020 nie modyfikuje danych katalogu ani nie uruchamia API.

## 13. T021 — przygotowanie V5 dla punktów 4 i 5 audytu

DEC-12: przygotować `evals/routing_prompts/V5.txt` na podstawie V4,
z zachowaniem formatu i zmianą zestawu przykładów. Kontrakt T017 jest
ukończony; pozostała zależność to T019. T020 nie blokuje pracy nad aktualnym
interfejsem. Obowiązują wyjątki redakcyjne i protokół T017-v1 z sekcji 9.

1. Zdefiniować ograniczony zestaw demonstracji i mapę przykład → reguła
   kontraktu. Uwzględnić kontrasty zgody na ryby i żądania ryby, domyślne
   vegetarian, jawne diety, ograniczenia/no_tool, cel a czas i liczbę propozycji.
2. Utworzyć V5. Poza blokiem przykładów zachować instrukcje V4 z wyjątkiem
   dwóch reguł „bez mięsa” wymagających zgodności z ROU-12/13 oraz
   wprowadzenia do przykładów obejmującego także no_tool. Przykłady
   obsługiwanych próśb mają wskazywać narzędzie i pełne argumenty zgodne
   ze schematem, a odmowy brak wywołania zgodnie z T019. Nie wprowadzać
   nowego formatu wiadomości assistant/tool ani wykonywania JSON-a z content.
3. Sprawdzić mapowania względem T017/T019, poprawność argumentów parserem,
   diff V4/V5 rozdzielający wyjątki redakcyjne i przykłady oraz odpowiednie
   istniejące testy offline.
   Nie zmieniać historycznych promptów lub etykiet, aby zaliczyć kontrolę.
4. Zaprojektować odrębny zestaw diagnostyczny: inne sformułowania tych samych
   reguł i kontrole regresji; nie używać końcowego holdoutu do strojenia.
   Uszczegółowić protokół T017-v1 przed pomiarem, ze wspólnym aktualnym
   opisem narzędzia po T018, konfiguracją i metrykami kanału, semantyki,
   granic odmowy oraz regresji. Wariant V4 trzeba mierzyć ponownie;
   historyczny T016 używał starszego opisu i nie jest kontrolą nowej kampanii.

Warunek ukończenia: plik V5, mapa pokrycia, kontrole offline i protokół
diagnostyki. Sprawdzamy przyszły wpływ całego nowego zestawu przykładów;
nie przypisujemy wyniku jednej demonstracji. Skuteczność i wdrożenie wymagają
późniejszych etapów. T021 nie uruchamia płatnego pomiaru i nie podmienia
`main.build_system_prompt`. Wiele celów żywieniowych nie wchodzi do przykładów
przed osobnym wdrożeniem ich kontraktu.

Zalecana kolejność przygotowania V5: ukończone T017 → T019 → T021. Projekt T020
można prowadzić niezależnie. Samo zaplanowanie zadania nie oznacza jego realizacji.
