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

## Najbliższe zadanie

**T019 — kontrakt odpowiedzi no_tool.** Stan: **gotowe do rozpoczęcia**.
T017 zakończyło diagnozę i specyfikację diet/protein; naprawa zachowania
modelu pozostaje do sprawdzenia. T019 ma określić odpowiedzialność modelu
i aplikacji, komunikat i źródło przyczyny, respektując ROU-12–17.
Następnie **T021 — przygotowanie V5**, ze scenariuszami i protokołem T017-v1.
Pozostała zależność T021 to T019. **T020 — projekt wielu celów żywieniowych**
można prowadzić niezależnie. Aktywny V0 pozostaje; bez automatycznego API.
T007 i T011 także są niezależne.

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

- [ ] **T019 — kontrakt odpowiedzi no_tool.**
  Stan: **gotowe do rozpoczęcia**; podstawa: DEC-10 / INS-03.
  Określić warunki braku narzędzia dla próśb poza zakresem, sprzeczności
  i braku wystarczającej informacji, respektując obsługiwane wartości domyślne.
  Rozdzielić brak wyszukiwania, pusty
  wynik, błąd API i niepoprawne wywołanie. Ustalić odpowiedzialność modelu
  i aplikacji, rolę content oraz pochodzenie powodu odmowy; nie zakładać,
  że sam brak tool_calls taki powód przekazuje. Zdefiniować komunikaty,
  brak dispatch i ocenę błędnej odmowy dla obsługiwanej prośby.
  Gotowe po tabeli decyzja → zachowanie → komunikat, granicach zmian
  i scenariuszach przypisanych do ACC-05/06/07/09/11. Na tym etapie
  dokumentacja kontraktu i plan testów, bez implementacji lub API.
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
- [ ] **T021 — przygotowanie V5: format V4 i kontrastowe przykłady.**
  Stan: **oczekuje na zależność** — T019; T017 ukończone. Podstawa: DEC-12,
  INS-04/05, ACC-06/09/11. Plik docelowy: `evals/routing_prompts/V5.txt`.
  Utworzyć nowego kandydata na bazie V4; zachować format „Zapytanie /
  Narzędzie / Argumenty”, zastępując dotychczasowy zestaw kontrastami.
  Po T017 dopuszczone są minimalne korekty dwóch zdań „bez mięsa” do
  ROU-12/13 oraz wprowadzenia obejmującego także no_tool; inne instrukcje
  zachować. Pokryć dietę a jawną preferencję białka,
  regułę „bez mięsa”, obsługiwane i nieobsługiwane wymagania, niezależność
  celu od czasu, różne top_n oraz no_tool zgodne z T019. Każdy przykład
  wymaga pełnych poprawnych argumentów albo jawnego braku wywołania;
  wskazać regułę, którą ilustruje. Nie dopisywać narzędzia o nazwie no_tool.
  Przygotować odrębne zapytania diagnostyczne i uszczegółowić T017-v1:
  porównanie V4/V5 z tym samym schematem po T018, modelem i ustawieniami.
  Gotowe po utworzeniu V5, mapie pokrycia, kontroli argumentów i diffu,
  przejściu odpowiednich testów offline oraz zapisaniu protokołu pomiaru.
  Przygotowanie nie oznacza potwierdzenia skuteczności. Bez płatnego API,
  wdrożenia do main.py, zmian backendu i nadpisywania V0–V4/expected.
  T020 nie blokuje zadania; nowe kombinacje wielu celów wymagają osobno
  ukończonego projektu i implementacji przed użyciem ich w przykładach.
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

Przygotowanie wariantu jest T021, po ukończonym T017 i przyszłym T019. Tabela
interpretacji i scenariusze testowe nie są automatycznie przykładami promptu:
dobór demonstracji i odrębnych zapytań diagnostycznych należy udokumentować.
Płatny pomiar i decyzja wdrożeniowa otrzymają odrębny zakres po przygotowaniu V5.

Nowa istotna czynność otrzymuje ID i warunek ukończenia. Wykonane zadanie
wskazuje dowód. Wznowienie T012 wymaga decyzji autorki; nie wynika
z odczytu starego raportu.
