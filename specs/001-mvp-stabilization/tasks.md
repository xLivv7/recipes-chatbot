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

## Najbliższe zadanie

**T009P — mały pilotaż diagnostyczny:** przygotowano kod V0/V2, 20 przypadków,
kontrolę budżetu i limit odpowiedzi. Wyniki testów offline są w mapie
weryfikacji. Przed płatnym uruchomieniem przedstawiamy manifest i koszt
do potwierdzenia; dotychczas brak rzeczywistych wywołań pilotażu.

T009: instrumentacja, testy i manifest przygotowane. Płatna kampania
jest **wstrzymana na decyzję autorki z 2026-11-03: tylko przygotowanie offline**.
Nie uruchamiać API ani ponawiać prośby bez wznowienia etapu przez autorkę.
Wyniki offline i szacunek kosztu:
[raport przygotowania](../../docs/reports/t009_preparation_2026-11-03.md).
T007 i T011 także pozostają gotowe do rozpoczęcia. Końcowa akceptacja
nadal wymaga zamknięcia pozostałych luk; T012 jest wstrzymane.

## Kolejne zadania

- [ ] **T009P — mały pilotaż V0/V2.** Stan: **offline przygotowane; wykonanie wymaga potwierdzenia konkretnego kosztu i payloadu**.
  20 przypadków × 2 warianty × 3 próby, tylko raw; max_completion_tokens=512,
  max_retries=0, lokalny budżet ochronny 0,50 USD. Gotowe po kompletnej kampanii,
  raporcie i decyzji o kandydacie; nie zalicza końcowej akceptacji.
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
