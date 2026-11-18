# Zadania — stabilizacja MVP

Aktualizujemy ten plik, zamiast dopisywać kolejne dokumenty „następne kroki”.
Zakres: [spec.md](spec.md). Kolejność: [plan.md](plan.md).
Dowody i luki: [verification.md](verification.md).

`[x]` oznacza wykonane zadanie, nie automatyczne zaliczenie kryterium ACC.
Pozostałe stany: **gotowe do rozpoczęcia**, **w toku**, **oczekuje na zależność**,
**wstrzymane przez autorkę**.

## Wykonane

- [x] **T001 — zakres i decyzje.** Ustalono brak nowych funkcji, jedną markę,
  samodzielne zapytania oraz DEC-01–03. Szczegóły wymagają rozwinięcia przed kodowaniem.
- [x] **T002 — kryteria i progi.** Zapisano ACC-01–14, zaakceptowane progi
  90%/85% i pełne przejście uzgodnionych testów. Zbiory nie są jeszcze zamrożone.
- [x] **T003 — punkt odniesienia.** Zapisano środowisko, kopię danych i
  [raport bazowy](../../docs/reports/baseline_2026-10-22.md): 216 testów,
  brak pominięć, renderer 6/6, walidator 0 ERROR / 20 WARNING / 9 INFO.
- [x] **T004 — organizacja SDD.** Rozdzielono aktywne specyfikacje, materiały
  techniczne, raporty i archiwum; dodano indeksy i poprawiono referencje.
- [x] **T005 — wymagania integralności i błędów.** Wykonano 2026-11-03.
  W `spec.md` zapisano INT-01–INT-04, ERR-01–ERR-05 i SC-01–SC-12,
  powiązania ACC oraz granice zmian w `plan.md`. Mapa weryfikacji rozdziela
  istniejące dowody i planowane scenariusze. Bez zmian kodu i danych.
- [x] **T006 — testy i poprawki DEC-02/03.** Wykonano 2026-11-03.
  Wdrożono INT/ERR, dodano scenariusze SC. Końcowa regresja: 230 testów,
  0 błędów i pominięć; renderer 6/6, walidator 0 ERROR / 20 WARNING / 9 INFO.
  [Raport i dowody](../../docs/reports/t006_2026-11-03.md). Dane i pięć SKU bez zmian.
- [x] **T008 — specyfikacja eksperymentu routingu.** Wykonano 2026-11-03.
  ROU-01–ROU-06, RSC-01–RSC-08, warianty V0/V1/V2 i protokół wyboru
  opisano w `spec.md` i `plan.md`. Offline sprawdzono 76 przypadków
  i planowane liczebności. Prompt, kod i zbiory bez zmian; 0 wywołań API.
- [x] **T009P — mały pilotaż V0/V2.** Wykonano 2026-11-03 po jednoznacznej zgodzie.
  120 wywołań raw, 0 błędów API i ucięć, jedna wersja modelu. Raport i decyzja
  zapisane; V2 nie przeszedł granic no_tool, aktywny prompt bez zmiany.
  Obliczenie kosztu z usage bez cache: 0,0452325 USD, rezerwa 0,2255679 USD.
  Nie zalicza końcowej akceptacji ani pełnej kampanii T009.

- [x] **T014 — poprawa routingu bez utraty granic obsługi.** Zakończono 2026-11-03.
  Zakres: ROU-07–ROU-10; zależność: zakończony T009P.
  Raport porównania, przegląd regresji i decyzja DEC-07 zapisane.
  V3 jest kandydatem, aktywny V0 pozostaje; zakończenie iteracji nie zalicza ACC.
  - [x] **T014.1 — specyfikacja i plan.** Zapisano wymagania, zależności,
    regułę oceny i granice zmian. Bez kodu, danych i wywołań API.
  - [x] **T014.2 — V3 i przygotowanie offline.** Wykonano 2026-11-03.
    Jeden akapit różnicy V2/V3, izolowana instrumentacja raw/application,
    10 nowych testów; pełna regresja 254/254 bez pominięć. Manifest i kosztorys
    według sekcji 7 planu; 0 rzeczywistych wywołań, aktywny V0 bez zmian.
    Dowody w sekcji T014.2 `verification.md`.
  - [x] **T014.3 — małe porównanie raw/application.** Wykonano 2026-11-03
    po poleceniu autorki. Zamrożone dane i reguła, 240 ocen / 216 wywołań,
    osobne wyniki i audyt; 0 błędów API/ucięć, bez holdoutu i ponawiania porażek.
    Kandydat V3; aktywny V0 bez zmian. Koszt z usage bez cache: 0,0845499 USD.
    [Raport](../../docs/reports/t014_3_routing_2026-11-03.md).
  - [x] **T014.4 — przegląd i decyzja o wdrożeniu.** Wykonano 2026-11-03.
    Potwierdzono kwalifikację V3 i integralność 26 plików dowodowych;
    przejrzano dispatch błędnej diety, odmowy i niestabilną regresję.
    DEC-07: pozostawić V0; potrzebna kolejna hipoteza. Kod bez zmian,
    0 nowych wywołań API; bez akceptacji MVP. Dowody w `verification.md`.

- [x] **T015 — kolejna iteracja routingu: specyfikacja i przygotowanie offline.**
  Wykonano 2026-11-03. Zapisano H-T015, RSC-09–RSC-12 i regułę T015-v1,
  następnie przygotowano V4 (jeden akapit ponad V3), profil porównania i testy.
  11 nowych testów, pełna regresja 265/265 bez błędów i pominięć;
  historyczny agregat T014 identyczny. Manifest 240 ocen / 216 wywołań,
  rezerwa 0,4310442 USD; 0 rzeczywistych wywołań. Aktywny V0 bez zmian.
  [Dowody](verification.md#t015--przygotowanie-v4-offline-zakończone).

- [x] **T016 — pomiar V0/V4 i przegląd kandydata.** Wykonano 2026-11-03
  po poleceniu autorki. 240 ocen / 216 wywołań, 0 błędów API i ucięć;
  kompletne wyniki, audyt i przegląd T015-v1. V4 raw 58/60, application 57/60,
  no_tool 18/18 w obu trybach, lecz regresja `intent_032` i trzy wywołania
  backendu z błędnym fish. DEC-08: V4 nie kwalifikuje się, pozostaje V0.
  Koszt z usage bez cache: 0,0888609 USD; ACC bez zmian.
  [Raport](../../docs/reports/t016_routing_2026-11-03.md).

- [x] **T017 — diagnoza relacji diet/protein i specyfikacja poprawki.**
  Zakończono 2026-11-16 offline. Zapisano diagnozę intent_032 bez
  przypisywania przyczynowości, ROU-12–17, macierz 12 kombinacji,
  28 scenariuszy DP, mapę istniejących kontrastów, H-T017 i T017-v1.
  Rozróżniono dopuszczenie od żądania, negacje i sprzeczności. Plan T021
  doprecyzowano o minimalną korektę INS-02 i wprowadzenia do przykładów.
  Kontrola parsera i niezmienności źródeł nie jest pomiarem modelu.
  Kod, prompty, dane i expected bez zmian; 0 wywołań API.
  [Kontrakt](spec.md#t017--kontrakt-interpretacji-diety-i-źródła-białka),
  [dowody i ograniczenia](verification.md#t017--diagnoza-i-kontrakt-zakończone).

- [x] **T018 — usunięcie konfliktu INS-01 w opisie narzędzia.** Wykonano
  2026-11-16 na polecenie autorki. ROU-11: wywołanie tylko dla obsługiwanej
  prośby, jawne wyjątki no_tool i pierwszeństwo nieobsługiwanego wymagania.
  Zmieniono wyłącznie opis funkcji; pola i struktura schematu identyczne.
  Pełna regresja 265/265 bez błędów i pominięć, API zablokowane.
  [Dowody](verification.md#t018--usunięcie-ins-01-zakończone).

- [x] **T019 — kontrakt odpowiedzi no_tool.** Zakończono 2026-11-17
  jako projekt: NTO-01–08, tabela decyzja → wykonanie → komunikat,
  MSG-01–08, 18 scenariuszy NTC i plan kontroli ACC-05/06/07/09/11.
  Wybrano brak nowego pola powodu: treść modelu jest ignorowana,
  a aplikacja zna tylko lokalny etap wykonania. Zachowano domyślne
  argumenty i rozróżnienie błędnej odmowy, blokady, awarii oraz pustego wyniku.
  W 12 kontrolach obecnej funkcji z atrapami potwierdzono również luki
  obsługi metadanych odpowiedzi; wdrożenie kontraktu otrzymało T022.
  Bez zmian kodu/promptów/expected i bez rzeczywistego API lub bazy.
  [Kontrakt](spec.md#t019--kontrakt-odpowiedzi-no_tool),
  [dowody i ograniczenia](verification.md#t019--kontrakt-no_tool-zakończony).

- [x] **T021 — przygotowanie V5: format V4 i kontrastowe przykłady.**
  Wykonano 2026-11-17 offline: V5 z 18 demonstracjami (14 tool, 4 no_tool),
  mapa D5-01–18, 12 odrębnych nowych przypadków i 20 zachowanych z pilota.
  Kontrola diffu, argumentów, kontrastów i rozdzielenia zapytań; 9 testów
  przygotowania. Osobny audyt zachowuje pięć fałszywych blokad z expected=tool.
  Manifest przewiduje 384 oceny / 354 wywołania, ale ma wykonanie wyłączone;
  rzeczywiste API=0, baza=0. Stan aplikacji T022 i ograniczenia są jawne.
  Kod aplikacji, schemat, V0–V4 i stare expected pozostały bez zmian.
  [Plik V5](../../evals/routing_prompts/V5.txt),
  [plan i mapa](plan.md#13-t021--przygotowanie-v5-dla-punktów-4-i-5-audytu),
  [dowody](verification.md#t021--przygotowanie-v5-offline-zakończone).

- [x] **T022 — wdrożenie kontraktu no_tool w aplikacji i diagnostyce.**
  Wykonano 2026-11-17: MSG-01, wspólny MSG-06 dla nieznanej funkcji,
  kontrola length/content_filter/refusal przed parserem i lookup oraz
  zgodna klasyfikacja raw/application w wersji T022-v1.
  Pełna regresja 283/283, bez pominięć; rzeczywiste żądania OpenAI i zapisy
  do katalogu zablokowane. Kontrole korzystały z odczytów PostgreSQL
  oraz izolowanej SQLite w pamięci. Pięć fałszywych blokad nadal jest błędami.
  V0–V5, schemat, parser preferencji, dane i expected bez zmian.
  Nowe manifesty zawierają hash walidacji; przygotowania T021 nie nadpisano.
  [Dowody i pokrycie NTC](verification.md#t022--wdrożenie-no_tool-zakończone).

- [x] **T023 — przygotowanie wykonania i porównanie V4/V5.**
  Zakończono 2026-11-17: instrumentacja, kompletny pomiar 02, audyt i DEC-13.
  V5 nie kwalifikuje się; aktywny V0 pozostaje, bez zaliczenia ACC.
  [Raport](../../docs/reports/t023_routing_2026-11-17.md),
  [dowody](verification.md#t023--porównanie-v4v5-zakończone).
  - [x] **T023.1 — instrumentacja, kontrole i plan.** 19 nowych testów,
    pełna regresja 302/302 bez pominięć, zamrożone źródła po T022,
    dokładne payloady, rezerwy i obsługa chwilowej blokady zapisu Windows.
    Generacje testowe na atrapach; brak zapisów do katalogu.
  - [x] **T023.2 — płatny pomiar po osobnej zgodzie.** Przerwany 01:
    262 oceny / 242 odpowiedzi API, zachowany bez wznowienia. Po poprawce
    i nowej zgodzie pełny 02: 384 oceny / 354 wywołania, 0 błędów technicznych,
    jeden resolved model. Koszt referencyjny obu prób bez cache 0,32163075 USD;
    wyniki jakości wyłącznie z 02, bez łączenia obserwacji.
  - [x] **T023.3 — raport i decyzja.** T017-v1 przeliczona niezależnie;
    V5 application 78/96 wobec V4 86/96, sześć regresji per-case i 13
    błędnych dispatch. Niezamówione fish 4 → 0 w obu trybach, ale intent_004
    i diag_004 nadal 0/3. DEC-13: pozostawić V0. Pięć fałszywych blokad
    pozostaje błędami osobnego audytu. T009/T012 nadal wstrzymane.

- [x] **T024 — poprawa fałszywych blokad preflight.** Zakończono 2026-11-17.
  PFL-01–07 i DEC-14: pięć znanych przypadków przechodzi preflight,
  zachowano dodatnie nieobsługiwane wykluczenia i pierwszeństwo alergii.
  12 nowych testów; pełna regresja 314/314 bez pominięć, SDK generacji
  i zapisy katalogu zablokowane. Przy poprawnej odpowiedzi podstawionej
  jeden dispatch; błędne no_tool nadal jest błędem decyzji. Audyt bez
  LLM nie zalicza modelu. Dawne etykiety i wyniki T021/T023 zachowano.
  [Dowody](verification.md#t024--poprawa-preflight-zakończona).

- [x] **T025 — projekt kontraktu interpretacji i podziału odpowiedzialności.**
  Zakończono 2026-11-18 jako projekt IR-1 (DEC-15). Wybrano wymuszone
  narzędzie przekazujące fakty bez katalogu, lokalną walidację i kompilator
  reguł. Opisano migrację legacy NTO, 20 scenariuszy IRC, schemat,
  fixture'y i ograniczenia kompletności rozpoznania. H-IR1 i IR1-D1
  oceniają całą warstwę względem świeżego V4, z semantyką jako priorytetem.
  Bez implementacji, promptu V6, zmiany modelu, SDK i bazy.
  [Projekt](interpretation-contract.md),
  [dowody](verification.md#t025--projekt-ir-1-zakończony).

- [x] **T026 — implementacja IR-1 offline.** Zakończono 2026-11-18.
  Walidator korzysta ze schematu T025; czysty kompilator przenosi reguły
  i defaulty do aplikacji, a adapter wymaga jednego calla interpretacyjnego.
  Wewnętrzny facts_v1 zachowuje preflight, parser, backend i renderer.
  33 nowe metody testowe, IRC-01–20, pełna regresja 347/347 bez pominięć;
  0 rzeczywistych żądań modelu, brak zapisów do katalogu. Zamrożono prompt,
  konfigurację i źródła kandydata. Domyślny legacy/V0 pozostaje; jakość
  rozpoznania przez model jest niezmierzona. [Dowody](verification.md#t026--implementacja-ir-1-offline-zakończona).

- [x] **T027 — mała diagnostyka warstwy IR-1.** Zakończono 2026-11-18.
  - [x] **T027.1 — przygotowanie.** 19 nowych metod, pełna regresja 366/366,
    przegląd adnotacji, payloady, runtime i kosztorys.
  - [x] **T027.2 — pomiar po osobnej zgodzie.** 72/72 SDK, 0 błędów
    API/metadanych, jeden resolved model, bez retry/resume.
  - [x] **T027.3 — raport i decyzja.** IR-1 raw 22/36 wobec V4 26/36,
    fakty 19/36, pięć regresji i 11 błędnych symulowanych dispatch w replay.
    DEC-16: brak kwalifikacji IR1-D1, pozostawić legacy/V0. Koszt
    referencyjny bez cache 0,026496 USD. [Raport](../../docs/reports/t027_interpretation_2026-11-18.md),
    [dowody](verification.md#t027--diagnostyka-zakończona).

- [x] **T028 — projekt kompletności ekstrakcji.** Zakończono 2026-11-18.
  DEC-17 wybiera CMP-1: ograniczoną kontrolę sygnałów przed dispatch,
  bez dopisywania faktów i zmiany wire IR-1. Porównano listę faktów,
  jawne grupy pól oraz reguły domenowe. Określono stany, lokalne operatory,
  defaulty, MSG-06 i diagnostykę coverage. 35 kontrastów z trzema znanymi
  ograniczeniami, CMP-01–12 i plan T029. Bez runtime, promptu, SDK i bazy.
  [Projekt](interpretation-completeness.md),
  [dowody](verification.md#t028--projekt-cmp-1-zakończony).

- [x] **T029 — implementacja CMP-1 i replay offline.**
  Tryb wewnętrzny `facts_checked_v1` zatrzymał 14 błędnych propozycji wyszukania,
  w tym 11 przechodzących przez preflight. Zero nowych blokad poprawnych
  wyników na 36 zapisanych odpowiedziach. Pełna regresja 372/372.
  [Raport T029](../../docs/reports/t029_completeness_2026-11-18.md).

## Najbliższe zadanie

**T020 — projekt obsługi wielu celów żywieniowych.** T007 i T011 również są gotowe do rozpoczęcia.

**T009P zakończone po zatwierdzeniu płatnego pilotażu przez autorkę.**
V2: 57/60, ale 15/18 poprawnych no_tool; V0: 42/60 i 18/18 no_tool.
Zgodnie z regułą pozostaje V0. [Raport](../../docs/reports/routing_pilot_2026-11-03.md).
Nie uruchamiamy automatycznie kolejnego pomiaru. T007 i T011 są niezależnymi
zadaniami gotowymi do rozpoczęcia; pełna kampania nadal jest wstrzymana.

T009: instrumentacja, testy i manifest przygotowane. Płatna kampania
jest **wstrzymana na decyzję autorki z 2026-11-03: tylko przygotowanie offline**.
Nie uruchamiać pełnej kampanii API ani ponawiać prośby bez wznowienia jej przez autorkę.
Wyniki offline i szacunek kosztu:
[raport przygotowania](../../docs/reports/t009_preparation_2026-11-03.md).
T007 i T011 także pozostają gotowe do rozpoczęcia. Końcowa akceptacja
nadal wymaga zamknięcia pozostałych luk; T012 jest wstrzymane.

## Kolejne zadania

- [ ] **T020 — projekt obsługi wielu celów żywieniowych.**
  Stan: **gotowe do rozpoczęcia**; podstawa: DEC-11 / INS-07.
  Zaprojektować m.in. low_kcal + keto: znaczenie łącznego spełnienia,
  warunki obowiązkowe, preferencje i ranking. Rozstrzygnąć, czy low_kcal
  oznacza próg czy preferencję; ocenić pozostałe kombinacje istniejących
  celów, duplikaty, brak celów i niemożność spełnienia zestawu.
  Zaproponować kontrakt danych oraz zgodność pojedynczych celów, wpływ
  na parser, backend, dobór SKU, normalizację, renderer i ewaluację.
  Gotowe po projekcie semantyki, kontraktu, rankingu, scenariuszy oraz
  ocenie zmiany zakresu MVP i planie migracji. Zachowanie odmowy uzgodnić
  z T019. Bez implementacji, zmian katalogu, API ani automatycznego
  rozszerzania innych pól (np. kategorii) do wielu wartości.
- [ ] **T007 — przegląd używanych konceptów z ostrzeżeniami kcal.**
  Stan: **gotowe do rozpoczęcia**. Sprawdzić źródła C012/C338/C357/C367;
  zapisać uzasadnioną akceptację albo propozycję korekty. Nie zmieniać kcal
  automatycznie według 4/9/4. Zadanie nie obejmuje pięciu SKU.
- [ ] **T009 — eksperyment routingu.** Stan: **offline gotowe; płatny etap wstrzymany przez autorkę**.
  Instrumentacja w `a1f7583`; 240 testów bez błędów i pominięć. Manifest
  kampanii `_01` przygotowany, 0 faktycznych wywołań API. Uruchomienie
  odrzucone przez automatyczną kontrolę; następnie autorka wybrała wyłącznie
  przygotowanie offline. Nie uruchamiać kampanii. Dopiero po jawnym wznowieniu,
  ponownej walidacji lub zamrożeniu aktualnych wejść:
  3 rundy raw/application na regresji,
  odrębne raporty i wybór według ustalonej reguły. Nie używać holdoutu
  ani nie wykonywać tekstowego JSON-a jako fallbacku. Gotowe po raporcie
  porównania i decyzji; sama instrumentacja nie kończy T009.
- [ ] **T010 — końcowe zestawy oceny.** Stan: **oczekuje na specyfikacje ocenianych
  zachowań**. Holdout i scenariusze ręczne według `acceptance.md`, z przeglądem
  etykiet przez autorkę. Zawartość zamrozić przed kampanią.
- [ ] **T011 — odtworzenie i instrukcja.** Stan: **gotowe do rozpoczęcia**.
  Uzupełnić przygotowanie środowiska i katalogu. Odtworzenie sprawdzić
  w odrębnym środowisku i bazie, bez nadpisywania bieżącej. Zapisać wynik.
- [ ] **T012 — podstawa makro pięciu SKU, DEC-04.** Stan: **wstrzymane przez autorkę**.
  Nie sprawdzać źródeł, nie korygować danych i nie wyłączać SKU, dopóki
  autorka nie wznowi zadania. Luka ACC-03 pozostaje otwarta.
- [ ] **T013 — finalna ocena ACC-01–14.** Stan: **oczekuje na wymagane poprawki,
  zestawy oceny i zamknięcie luk, w tym T012**. Jedna wersja kandydująca,
  jawne wyniki kryteriów, ograniczenia i decyzja o gotowości MVP.

## Aktualizacja

### Ustalenia audytu dotyczące przykładów

- **Punkt 4 / INS-04:** dla nowego kandydata zachować format V4.
- **Punkt 5 / INS-05:** wymienić zestaw na przykłady kontrastowe w V5.

T021 wykonało przygotowanie po T017/T019: demonstracje są oddzielone od
diagnostyki, a znane fałszywe blokady mają osobny audyt. T023 zakończyło
pomiar i przegląd: DEC-13 odrzuca V5 według T017-v1, pozostawiając V0.
Wynik nie zamyka problemów routingu; kolejna iteracja wymaga osobnego zadania.

Nowa istotna czynność otrzymuje ID i warunek ukończenia. Wykonane zadanie
wskazuje dowód. Wznowienie T012 wymaga decyzji autorki; nie wynika
z odczytu starego raportu.
