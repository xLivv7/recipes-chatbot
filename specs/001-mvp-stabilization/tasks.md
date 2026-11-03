# Zadania — stabilizacja MVP

Aktualizujemy ten plik, zamiast dopisywać kolejne dokumenty „następne kroki”.
Zakres: [spec.md](spec.md). Kolejność: [plan.md](plan.md).
Dowody i luki: [verification.md](verification.md).

`[x]` oznacza wykonane zadanie, nie automatyczne zaliczenie kryterium ACC.
Pozostałe stany: **gotowe do rozpoczęcia**, **oczekuje na zależność**,
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

## Najbliższe zadanie

**T017 — diagnoza relacji diet/protein i specyfikacja poprawki offline.**
T016 zakończono DEC-08: V4 nie zakwalifikował się mimo 95% application.
Pozostał błąd `intent_032`: dieta pescetarian została potraktowana jak jawne
żądanie ryby. Najpierw analiza kontrastów i hipoteza, potem osobno implementacja.
[Raport i decyzja](../../docs/reports/t016_routing_2026-11-03.md).
Aktywny V0 pozostaje; bez automatycznego API. T007 i T011 są niezależne.

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

- [ ] **T017 — diagnoza relacji diet/protein i specyfikacja poprawki.**
  Stan: **gotowe do rozpoczęcia**; zależność: DEC-08 / wykonane T016.
  Offline przejrzeć `intent_032` i kontrasty jawnej preferencji ryby wobec
  diety dopuszczającej ryby. Zapisać diagnozę, ograniczoną hipotezę, granice
  zmian, scenariusze i regułę weryfikacji według sekcji 9 planu.
  Gotowe po aktualizacji specyfikacji i planu; bez implementacji, API,
  zmiany expected, wdrożenia lub wznowienia T009/T012.
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

Nowa istotna czynność otrzymuje ID i warunek ukończenia. Wykonane zadanie
wskazuje dowód. Wznowienie T012 wymaga decyzji autorki; nie wynika
z odczytu starego raportu.
