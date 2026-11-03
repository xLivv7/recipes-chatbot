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

## Najbliższe zadanie

- [ ] **T005 — doprecyzować wymagania integralności i błędów.**
  Stan: **gotowe do rozpoczęcia**. Zakres: DEC-02/03, ACC-01/07/08,
  ST-03/04. Rozwinąć w `spec.md` scenariusze i oczekiwane wyniki: brak polityki,
  niezgodność z filtrem, błąd danych, błąd programistyczny i zwykły brak wyników.
  Gotowe, gdy każdy scenariusz ma wymaganie z ID i sposób weryfikacji,
  a plan wskazuje granice zmian. Nie zmieniać przy tym kodu ani danych.

## Kolejne zadania

- [ ] **T006 — testy i poprawki DEC-02/03.** Stan: **oczekuje na T005**.
  Uzupełnić istotne luki testów, poprawić domyślne dopuszczenie braku polityki
  i maskowanie błędów. Gotowe po weryfikacji wymagań i aktualizacji mapy.
  Bez zmiany danych pięciu SKU.
- [ ] **T007 — przegląd używanych konceptów z ostrzeżeniami kcal.**
  Stan: **gotowe do rozpoczęcia**. Sprawdzić źródła C012/C338/C357/C367;
  zapisać uzasadnioną akceptację albo propozycję korekty. Nie zmieniać kcal
  automatycznie według 4/9/4. Zadanie nie obejmuje pięciu SKU.
- [ ] **T008 — specyfikacja eksperymentu routingu.** Stan: **gotowe do rozpoczęcia**.
  Opisać poprawny kanał wywołania i mierzone błędy. Zaplanować porównanie
  na regresji, bez użycia holdoutu do strojenia. Sam plan nie uruchamia API.
- [ ] **T009 — eksperyment routingu.** Stan: **oczekuje na T008**.
  Zachować porównywalne konfiguracje i odrębne raporty; wybrać wariant
  przed niezależnym pomiarem. Nie wykonywać tekstowego JSON-a jako fallbacku.
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
