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

**Zakończone 2026-11-17, jako projekt.** Rezultat: NTO-01–08, tabela
decyzja → wykonanie → komunikat, MSG-01–08 i NTC-01–18 w `spec.md`.
Podstawa: DEC-10 / INS-03 i ukończony T017. Nie wdrożono zmian aplikacji.

Wybrano prosty kontrakt: brak narzędzia bez nowego pola lub narzędzia
przyczyny. content modelu nie jest przekazywany użytkownikowi i nie
stanowi uzasadnienia. Wiadomo tylko, na którym etapie zatrzymała się
aplikacja; preflight daje nazwę reguły, a nie pewny opis intencji lub
stanu zdrowia. Dla zwykłego no_tool wystarczy stały MSG-01. Doprecyzowanie
oznacza nowe samodzielne zapytanie, bez nowego dialogu w MVP.

### Stan kodu a kontrakt docelowy

Przejrzano `main.chat_with_bot`, parser, preflight, renderer i rozdzielony
runner ewaluacji. Dodatkowo wykonano 12 obserwacji offline na funkcji
wyodrębnionej z AST, z podstawionymi odpowiedziami i atrapą lookup.

| Obecne zachowanie | Decyzja projektowa |
| --- | --- |
| Content bez narzędzia jest ignorowany, również JSON; brak wyników ma osobny komunikat. Błędy API/argumentów nie uruchamiają lookup. | Zachować, powiązać z NTO-02/04/05/06. |
| NO_TOOL_RESPONSE jest stały, ale prosi o doprecyzowanie kategorii i wymienia wyłącznie alergię na mleko/białka. | W T022 zastosować MSG-01 bez sugerowania brakującego pola i z ogólną granicą braku doboru dla alergii. |
| Nieznane narzędzie ma inny ogólny komunikat niż pozostałe błędy protokołu. | W T022 ujednolicić do MSG-06; zachować brak dispatch. |
| length i content_filter/refusal bez wywołania trafiają do NO_TOOL_RESPONSE. Przy poprawnym call i length obecny kod uruchamia lookup. | W T022 zatrzymać znane sygnały niepełnej/odfiltrowanej odpowiedzi przed dispatch i spójnie oznaczyć błąd w raw/application. To luka względem NTO-06, nie poprawne biznesowe no_tool. |
| Preflight blokuje także semantycznie obsługiwane guard_005/006 i DP-02/03/22. | Zachować expected=tool i błąd preflight. T019 nie zmienia gramatyki ani nie zalicza jej fałszywych blokad. |

Obserwacje potwierdzają ścieżki kodu, nie interpretację języka przez model
ani działanie SDK/dostawcy. Przechwycono 10 wywołań lokalnej atrapy klienta
i 2 wywołania atrapy lookup; rzeczywiste API=0, baza=0. Materiały są w sekcji
T019 `verification.md`; kod i historyczne wejścia zachowano bez zmian.

### Plan weryfikacji implementacji

1. Dla NTC-01–09/18: podstawione odpowiedzi z content=null/pustym/tekstowym
   i JSON-em; sprawdzić brak dispatch, jeden komunikat aplikacji oraz
   zachowanie wszystkich domyślnych argumentów przy poprawnym call.
   Tekst lub JSON bez narzędzia dla expected=tool ma pozostać błędem decyzji,
   bez wymyślonych ocen brakujących pól. Punkty zaczepienia:
   `test_chat_response_protection.py`, `test_no_tool_diagnostics.py`,
   `test_separated_routing_eval.py` i `test_current_evaluation.py`.
2. Dla NTC-03/16/17: istniejące etykiety i priorytet preflight, brak
   klienta/lookup dla blokady oraz osobny wynik raw. Fałszywy guard nie jest
   sukcesem aplikacji; brak odpowiedzi modelu nie jest jego sukcesem ani
   porażką. Użyć również `test_request_safety.py` i `test_unsupported_exclusions.py`.
3. Dla NTC-10–15: kontrolowane błędy API, protokołu i argumentów; metadane
   length/content_filter/refusal zarówno bez call, jak z poprawnie wyglądającym
   call; wyjątki przygotowania i payloadu. Sprawdzić liczbę lookup, rozdzielenie
   MSG-01/04/05/06/07/08 i brak treści wyjątków. Uzgodnić obserwacje runnera
   z decyzją aplikacji, bez zaliczania błędów jako no_tool. Uzupełnić istniejące
   testy walidacji, diagnostyki oraz ochrony błędów; nie testować tylko brzmienia
   stałych zamiast skutków wykonania.
4. Zmiany aplikacji i instrumentacji wykonać w T022, z regresją odpowiednią
   do zmienionych granic. Zachować stare raporty i etykiety; wskazać nową
   wersję klasyfikacji. Kontrole z atrapami nie zaliczają ACC-09/11.
   Interpretacja nowych zapytań wymaga osobno zaplanowanego pomiaru modelu.

Warunek ukończenia T019 został spełniony przez kontrakt, tabelę, granice
i plan kontroli ACC-05/06/07/09/11. T021 może przygotować V5; T022 nie
blokuje przygotowania offline. Przed przyszłym porównaniem V4/V5 zamrozić
jedną wersję aplikacji i runnera dla obu wariantów oraz zapisać, czy T022
jest wdrożone. Zmiany ochrony, komunikatów i klasyfikacji nie są wpływem
promptu V5. Nie uruchamiać API w T019 i nie wznawiać T009 ani T012.

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
z zachowaniem formatu i zmianą zestawu przykładów. **Wykonano offline
2026-11-17**, po T017/T019. Rezultat jest kandydatem do późniejszej oceny.
W chwili przygotowania T021 T022 nie było wdrożone; nie podmieniono
`main.build_system_prompt`. Późniejsze wdrożenie T022 opisuje sekcja 14.

### Zakres różnicy i mapa demonstracji

Zastąpiono pięć przykładów V4 osiemnastoma demonstracjami. Poza nimi zmiany
ograniczają się do dwóch sformułowań „bez mięsa” i wprowadzenia obejmującego
brak wywołania. Format pozostaje `Zapytanie / Narzędzie / Argumenty`.
Odmowa ma `Narzędzie: brak wywołania` i `Argumenty: nie dotyczy`, bez
fikcyjnego narzędzia lub argumentów powodu. Nie dodano historii assistant/tool.
Walidator odrzuca inne zmiany instrukcji oraz błędne argumenty i kontrasty.

| ID / pozycja w V5 | Rozróżnienie / oczekiwane znaczenie | Reguły |
| --- | --- | --- |
| D5-01 | Cztery obiady bez mięsa: vegetarian/none. | ROU-12/17 |
| D5-02 | Te same obiady z dopuszczeniem ryb: pescetarian/none. | ROU-12/14 |
| D5-03 | Te same obiady z żądaniem ryby: pescetarian/fish. | ROU-12/14 |
| D5-04 | Dwie wegańskie przekąski bez mięsa: vegan/none. | ROU-13/17 |
| D5-05 | Jeden rybny lunch: none/fish. | ROU-14 |
| D5-06 | Jeden mięsny lunch: none/meat. | ROU-14 |
| D5-07 | Wysokobiałkowy obiad pescetariański nie wymaga fish. | ROU-14 |
| D5-08 | Niskokaloryczny deser bez laktozy, bez limitu czasu. | ROU-17 |
| D5-09 | Ten sam deser z jawnym time_max=18. | ROU-17 |
| D5-10 | Bezglutenowy obiad na szybko: standard, time_max=30. | ROU-17 |
| D5-11 | Ten sam obiad, jawne 40 minut zastępuje domyślne 30. | ROU-17 |
| D5-12 | Śniadanie keto nie ustanawia limitu czasu. | ROU-17 |
| D5-13 | Bez laktozy i bez glutenu razem; bez dodatkowej diety/celu. | ROU-17 |
| D5-14 | Zamiast bez laktozy: bez mleka — brak wywołania. | ROU-07; NTO-01 |
| D5-15 | Dobór lunchu dla alergii — brak wywołania. | NTO-01/03 |
| D5-16 | Jawne vegetarian z prawdziwą rybą — sprzeczność, brak wywołania. | ROU-13/16; NTO-01 |
| D5-17 | Pytanie poza przepisami — brak wywołania. | NTO-01 |
| D5-18 | Ogólna prośba o przepis korzysta z wartości domyślnych. | NTO-01/08 |

Pełne argumenty są w [V5](../../evals/routing_prompts/V5.txt), a mapa jest
również zapisywana w `checks.json`. Wybór różnorodnych par wejście → wynik
jest zgodny z podejściem few-shot opisanym w [OpenAI Docs](https://developers.openai.com/api/docs/guides/prompt-engineering#few-shot-learning).
Jest to uzasadnienie projektu przykładów, nie dowód ich skuteczności.
Wiele celów żywieniowych nie wchodzi do V5 przed odrębną implementacją.

### Rozdzielenie demonstracji, diagnostyki i audytu ochrony

Zachowano dokładnie 20 przypadków starego pilota: 14 tool i 6 no_tool.
Program porównuje każdy z jego źródłem w istniejącej regresji. Dodano
[12 przypadków](../../evals/routing_v5_cases.json), 11 tool i 1 no_tool:

| ID v5_diag_… | Znaczenie diagnostyczne |
| --- | --- |
| 001/002 | Dwa obiady pescetariańskie bez wymaganej ryby / z rybą. |
| 003/004 | Bez mięsa z dopuszczeniem / żądaniem ryby. |
| 005 | Jawne vegan z „bez mięsa”, pięć propozycji. |
| 006 | Cel wysokobiałkowy i zanegowane żądanie ryby nie dodają fish. |
| 007 | Jawne mięso i bez laktozy, bez zmiany diety. |
| 008/009 | Fit lunch bez glutenu bez czasu / z limitem 22 minut. |
| 010 | Bezlaktozowe szybkie śniadanie z jawnym limitem 50 minut. |
| 011 | Domyślne parametry przy samodzielnej ogólnej prośbie. |
| 012 | Nieobsługiwane wykluczenie mleka przy obsługiwanym rodzaju dania. |

To łącznie **32 przypadki: 25 tool i 7 no_tool**. Nowe zapytania opracowano
w T021 z pomocą asystenta na podstawie ROU/NTO; nie są niezależnym holdoutem
ani etykietami po zewnętrznym przeglądzie. Walidacja sprawdza ich argumenty,
ID i rozdzielenie od demonstracji także po normalizacji liter, odstępów
i interpunkcji. Nie korzystano z zapytań holdoutu do projektowania.

Osobny **audyt offline** obejmuje guard_005/006 i DP-02/03/22. Zachowuje
expected=tool oraz pięć obecnych fałszywych blokad. Wybrano ten podział przed
pomiarem: diagnoza modelu nie wymaga płacenia za prośby zatrzymane przed API.
Audyt ma być widoczny w każdym przyszłym raporcie obok porównania modelu.
Nie wchodzi do mianownika małego porównania 32 przypadków i nie staje się
sukcesem no_tool. Pełna regresja i akceptacja aplikacji nadal mają tę lukę;
nie wolno przenosić wyniku małego porównania na ACC.

### Zamrożony plan małego porównania

Obowiązuje T017-v1, uszczegółowione przed wykonaniem:

- świeże V4/V5, ten sam schemat po T018; wyniki T016 nie są kontrolą;
- model gpt-4o-mini, temperatura 0,1, auto, parallel_tool_calls=false,
  max_completion_tokens=512, retry=0, timeout=30 s; po jednym system/user,
  bez etykiet expected w wiadomościach;
- trzy rundy V4/V5, V5/V4, V4/V5; dla każdego wariantu raw, potem application,
  z atrapą lookup; każda zmiana aplikacji/runnera wymaga nowego zamrożenia
  i jednej wspólnej wersji dla obu wariantów;
- **384 oceny**: 32 × 2 warianty × 3 rundy × 2 tryby. Przewidywane
  **354 wywołania**: 192 raw i 162 application; 30 ocen application kończy
  się na pięciu poprawnych blokadach preflight w każdej grupie;
- cele wymagające 3/3 w obu trybach: intent_004/010/032 i v5_diag_001–007.
  Pozostałe ID również podlegają warunkowi braku pogorszenia per-case;
- V5: 21/21 no_tool osobno w każdym trybie; brak błędnego
  semantycznie dispatch. W application V5 co najmniej 87/96 ocen,
  68/75 obsługiwanych prób i 28/32 przypadków stabilnych; to dokładne
  progi 90%/90%/85% dla tej liczebności, bez zmiany T017-v1;
- porównanie kompletne, jeden resolved model, bez API errors i ucięć.
  Oddzielnie raportować kanał, argumenty, semantykę, niezamówione fish,
  utratę jawnego fish, preflight i każdy błędny dispatch;
- wsparcie H-T017 wymaga mniej niezamówionych fish niż świeże V4 w obu
  trybach, bez utraty jawnych fish i spełnienia pozostałych warunków.
  Remis lub brak błędu V4 nie dowodzi poprawy; nie wdrażać V5 automatycznie.

Powyższy warunek 21/21 jest warunkiem granic V5; V4 jest kontrolą i jego
ewentualne błędy są raportowane, nie unieważniają przez samą liczbę
poprawnych no_tool porównania. W obu wariantach zachować komplet ocen.

Szacunkowa rezerwa całego planu: **0,86790195 USD** przy proxy wejścia
`liczba bajtów UTF-8 żądania + 2000` i rezerwie 512 tokenów wyjścia.
To nie tokenizer ani gwarancja rachunku. Przyjęto stawki standardowe
0,15/0,60 USD za milion tokenów wejścia/wyjścia, bez cache, podatków
i innych wywołań konta; sprawdzono 2026-11-17 w [OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-4o-mini).
Ta sama strona oznacza model jako deprecated; nie sprawdzano dostępności
konta przez API i nie zmieniano modelu. Przed przyszłym pomiarem ponownie
sprawdzić dostępność i cennik oraz uzyskać zgodę na konkretny zakres/koszt.
Dotychczasowy limit 0,50 USD dawnych profili nie upoważnia do tego planu.

### Przygotowanie i granica wykonania

[prepare_routing_v5.py](../../evals/prepare_routing_v5.py) działa bez
SDK, main, bazy, klucza i dostępu do sieci. `--check` kontroluje wejścia;
`--output NOWY_KATALOG` zapisuje manifest, pełne prompty, wspólny schemat,
przypadki, audyt guard, diff i kopie źródeł z hashami. Nie nadpisuje katalogu.
Manifest ma execution_enabled=false, actual_api_calls=0 i brak zatwierdzonego
budżetu. Program nie posiada `--execute`; stare profile runnerów zachowano.

T021 kończy przygotowanie i kontrole, nie pomiar jakości. Wykonanie ma
odrębne T023 po T022, z odświeżeniem manifestu i instrumentacją zgodną
z T017-v1. Mapa dowodów zawiera lokalizację przygotowania i wyniki offline.

## 14. T022 — wdrożenie kontraktu no_tool w aplikacji i diagnostyce

**Wykonano 2026-11-17.** W `main.chat_with_bot` zastosowano MSG-01 oraz
wspólny MSG-06 dla nieznanej funkcji. Dodano czystą wspólną kontrolę
odpowiedzi w `core/llm_response_validation.py`, używaną przez aplikację
i `observe_response` w obu trybach. Nie wymaga SDK, bazy ani nowego pola
modelu. Odrzuca znane sygnały braku pełnej odpowiedzi przed parserem i lookup.

Znaczenie finish_reason/refusal sprawdzono w [OpenAI Docs](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).
Decyzja o zatrzymaniu zapytania jest regułą projektu NTO-06. Brak opcjonalnych
metadanych w starszych atrapach nie ustanawia nowego wymogu ich obecności;
tekst content nigdy nie zastępuje metadanych ani wywołania.

| Zaobserwowany sygnał | response_failure_reason | Zachowanie |
| --- | --- | --- |
| Brak choices | empty_choices | MSG-06, brak dispatch, błąd protokołu. |
| finish_reason=length | truncated_response | MSG-06 przed odczytaniem argumentów, także dla poprawnego JSON-a. |
| finish_reason=content_filter | filtered_response | MSG-06, bez wnioskowania o zakresie katalogu. |
| Niepuste pole refusal | provider_refusal | MSG-06, treść odmowy nie trafia do użytkownika. |
| Brak powyższych sygnałów i brak tool_calls | brak błędu odpowiedzi | MSG-01; poprawność decyzji zależy od expected w teście. |

Runner ma wersję `response_validation_version=T022-v1` na poziomie raportu
i wiersza. Przy błędzie odpowiedzi zachowuje metadane i ślad wywołań, ale
nie przyznaje model_decision_correct ani ocen pól; effective_action=error,
failure_stage=protocol. Pole response_refusal obejmuje metadane również
przy obecnym call. Dawne no_tool_content/no_tool_refusal zachowano dla
diagnostyki braku wywołania. Nie przeliczano historycznych raportów.

Pełna regresja: **283 testy, 0 błędów, 0 niepowodzeń i 0 pominięć**.
Dziewięć nowych testów i istniejące kontrole pokrywają NTC-01–18; szczegółowa
mapa jest w `verification.md`. Kontrolowane odpowiedzi obejmują także
24 kombinacje sygnału błędu, obecności narzędzia, expected i raw/application.
Sprawdzono brak parsera/lookup dla błędnych metadanych i zachowanie jednego
lookup dla poprawnej prośby z domyślnymi argumentami.

Import istniejącej aplikacji wymaga lokalnego PostgreSQL. Harness blokował
rzeczywiste żądania SDK i zapisy do katalogu; obserwował 35 SELECT PostgreSQL.
Pozwalał na izolowaną SQLite w pamięci używaną przez istniejące testy curation.
Początkowe dwa niepowodzenia pełnego przebiegu wynikały z blokady tworzenia
tej SQLite w osłonie testów; po jej doprecyzowaniu pełna regresja przeszła.
Nie zmieniano kodu curation ani danych katalogu. API modelu: 0 wywołań.

W nowych manifestach uwzględniono hash wspólnej walidacji: w preparerze V5,
źródłach runnera raw/application i wspólnej liście źródeł dawnych profili.
Nie zmieniono ich harmonogramów ani reguł wyboru. Nie nadpisano historycznego
przygotowania T021, promptów V0–V5 i expected. Nowy manifest po T022 jest
obowiązkową częścią T023; starego pakietu T021 nie wykonywać na nowym kodzie.
Preflight i pięć fałszywych blokad pozostają bez zmian. Aktywny prompt to V0.

## 15. T023 — przygotowanie wykonania i porównanie V4/V5

**Zakończono 2026-11-17.** Instrumentacja, kompletny zatwierdzony pomiar 02,
audyt i decyzja DEC-13: V5 nie kwalifikuje się, pozostaje aktywny V0.
Application: V4 86/96, V5 78/96; poprawa fish nie równoważy sześciu regresji
i 13 błędnych dispatch V5. [Raport](../../docs/reports/t023_routing_2026-11-17.md).
Pierwszy pomiar przerwał błąd zapisu Windows po 262 ocenach / 242
odpowiedziach. Zachowano go bez wznowienia, poprawiono zapis i uzyskano
osobną zgodę na cały 02. Nie zmieniono T017-v1, przypadków, promptów,
schematu ani historycznej reguły T015. Poniżej zachowano protokół i zakres.

### T023.1 — instrumentacja i zamrożenie

[run_routing_v5.py](../../evals/run_routing_v5.py) korzysta z przygotowania
T021 oraz `evaluate_case` w wersji T022-v1. Przygotowanie jest oddzielone
od płatnego wykonania; SDK/aplikacja są importowane dopiero przy wykonaniu
lub lokalnym audycie. Nowy pakiet jest w
[katalogu nowej kampanii 02](../../dokumentacja%20pracy/2026-11-17_t023/campaign_02/plan.json).
Pierwotny pakiet 01 i jego niepełne wyniki zachowano; szczegóły są w
[raporcie wykonania](../../docs/reports/t023_routing_2026-11-17.md).

- `plan.json`: niezmienny plan i hash do zatwierdzenia; konfiguracja,
  kryteria, źródła z kopiami, wersje Python/SDK/SQLAlchemy/httpx, hashe
  artefaktów, limit żądań, kosztorys i lokalny próg rezerwy;
- `payloads.json`: 64 dokładne payloady (V4/V5 × 32 zapytania), bez expected,
  reguł przypadków, danych katalogu lub rzeczywistych rozmów;
- `schedule.json`: 384 zaplanowane oceny; 354 wymagają żądania modelu,
  pozostałe 30 to poprawne blokady application;
- `state.json`: zmienny stan wykonania, rezerwacje i zgoda na konkretny
  hash/budżet; przygotowanie ma actual_api_calls=0 i status prepared;
- raporty grup i wyników powstają dopiero po rozpoczęciu. Pięć znanych
  fałszywych blokad ma osobny audyt application z klientem zabraniającym
  generacji. W raporcie pozostają błędami preflight, poza mianownikiem 32.

Odczytem `GET /v1/models/gpt-4o-mini` potwierdzono widoczność modelu na
koncie przed rozpoczęciem generacji. [OpenAI Docs](https://developers.openai.com/api/reference/python/resources/models/methods/retrieve)
opisuje ten odczyt jako metadane modelu; nie weryfikuje on salda ani sukcesu
generacji. [Cennik modelu](https://developers.openai.com/api/docs/models/gpt-4o-mini)
sprawdzony 2026-11-17 nadal podaje 0,15/0,60 USD za milion tokenów.
[Ogłoszony termin wyłączenia](https://developers.openai.com/api/docs/deprecations)
to 2027-01-14; modelu nie zmieniono.

Plan zachowuje **354 maksymalne wywołania gpt-4o-mini, 384 oceny**, limit
odpowiedzi 512, retry=0, timeout=30 s, endpoint api.openai.com/v1 i trzy
rundy z sekcji 13. Szacunkowa rezerwa wynosi **0,86790195 USD**, a proponowany
lokalny próg sumy rezerw **1,00 USD**. To kontrola szacunku wejścia/wyjścia,
nie limit rachunku dostawcy; cache, podatki i inne użycie konta nie są
uwzględnione. Dawne zgody i próg 0,50 USD innych profili nie są zgodą
na tę kampanię. Plan hashuje dokładne payloady i nie przejmuje starego
manifestu T021 po zmianach kodu.

19 nowych testów obejmuje pełną symulację, zgodność payloadów i przywrócenie
aktywnego promptu, brak klienta przed zgodą, manipulacje plikiem, hashem,
regułą lub etykietą, brak nadpisania/wznowienia, checkpoint przed błędem,
próg żądań/rezerw, remis, pojedynczą regresję, utratę fish, błędny dispatch,
niekompletne obserwacje, mieszane modele i błędy techniczne. Pełna regresja:
**302/302** po poprawce zapisu, bez pominięć; wszystkie generacje w testach
były atrapami. Symulacja
nie jest pomiarem modelu i jest oznaczona execution_kind=mock.
Trzy dodatkowe kontrole dotyczą chwilowej/trwałej blokady pliku Windows
i zakazu wysłania żądania przy nieudanym utrwaleniu rezerwy. Atomowe
zastąpienie pliku ma najwyżej pięć lokalnych oczekiwań (łącznie 1,55 s).
Trwała blokada nadal kończy przebieg; to nie retry SDK.

### T023.2 — wykonanie po zgodzie

**Wykonano:** osobna zgoda na plan 02, 384 oceny / 354 wywołania,
0 błędów API i metadanych, jeden resolved model. Rezerwa 0,86790195 USD;
koszt referencyjny z usage bez cache 0,19128450 USD. Dane 01 i 02 osobno.

Etap płatny wymaga osobnej zgody na tę konkretną kampanię.
Zgoda na pakiet 01 została wykorzystana: 242 odpowiedzi, koszt referencyjny
bez cache 0,13034625 USD. Licznik rezerwacji 243 obejmuje jeden niewysłany
slot. Pakiet 02 jest nowym, pełnym porównaniem; nie łączyć z nim obserwacji
01 ani nie uzupełniać trzeciej rundy wybiórczo. Powtórzenie wynika z awarii
zapisu, bez zmian kryteriów lub promptów po obejrzeniu odpowiedzi.
Zgoda ma dotyczyć hasha planu, przesyłanych 32 kontrolowanych zapytań,
promptów V4/V5 i wspólnego schematu get_recommendations, maksymalnej liczby
354 żądań oraz lokalnego progu rezerwy 1,00 USD. Sekrety służą wyłącznie
uwierzytelnieniu do właściwego API; nie są treścią promptów. Nie wysyłać
danych katalogu ani rzeczywistych rozmów. Nie wznawiać T009/T012.

Przed utworzeniem klienta sprawdzić komplet hashy, konfigurację, runtime
i zatwierdzony hash/proponowany budżet. SDK ma retry=0. Wykonawca rezerwuje
koszt i zapisuje stan przed każdym żądaniem oraz odrzuca payload spoza
harmonogramu. Checkpointy zachowują obserwacje; nie ma selektywnego wznowienia.
Przerwać po pierwszym błędzie API lub response_failure_reason (w tym brak
choices, length, content_filter i refusal), zachowując niepełny raport.
Przy zwykłych błędach decyzji/argumentów kontynuować ocenę wszystkich ID.
To reguła zatrzymania zapisana przed pomiarem, bez zmiany progów kwalifikacji.

### T023.3 — raport i przegląd

**Wykonano:** raport, kompletne surowe obserwacje, audyt i DEC-13.
V5 ma 21/21 no_tool i spadek niezamówionych fish 4 → 0 w obu trybach,
lecz intent_004 i diag_004 pozostają 0/3, sześć ID pogorszyło się w każdym
trybie, application 78/96, obsługiwane 57/75, stabilne 25/32 oraz 13 błędnych
dispatch. Cztery z dziesięciu warunków T017-v1 spełnione; brak kandydata.
Zakończenie eksperymentu nie zalicza ACC ani nie kończy poprawy routingu.

Raport pokazuje cele 3/3, kanał, pola i semantykę, fish bez żądania oraz
utracone jawne fish, per-case regresje, błędne dispatch, użycie tokenów
i koszt referencyjny bez cache. Zachować oddzielnie raw/application oraz
audyt ochrony. V5 kwalifikuje się wyłącznie po wszystkich warunkach T017-v1,
w tym spadku niezamówionych fish w obu trybach. Remis lub brak błędów V4
nie dowodzi poprawy. Aktywny V0 pozostaje bez automatycznej podmiany.

T023 jest gotowe po kompletnym raporcie, audycie i jawnej decyzji. Negatywny
wynik również kończy eksperyment; nie zmieniać kryteriów po wynikach,
nie ponawiać wybiórczo porażek i nie przeliczać historycznych raportów.
