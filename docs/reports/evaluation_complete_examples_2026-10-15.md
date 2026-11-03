# Pomiar po pelnych przykladach tool calla

Wersja promptu: commit 6e73a65. Pomiar rzeczywisty, po 3 proby raw/application
na tych samych 76 przypadkach regresyjnych. Bez holdoutu i bez zmian expected.
426 wywolan SDK, 456 ocen; 0 bledow API. Resolved model:
gpt-4o-mini-2024-07-18. Backend stubowany, nie eksportowano wynikow bazy.

| Tryb | Proby | Lacznie | Stabilne cases |
| --- | --- | --- | --- |
| raw | 46/76, 50/76, 49/76 | 145/228 (63.6%) | 46/76 |
| application | 46/76, 47/76, 48/76 | 141/228 (61.8%) | 45/76 |

## Ocena
intent_015 i intent_025 przeszly 3/3 w obu trybach, zamiast dotychczasowych
0/3. Wszystkie zwrocone calle sa poprawne strukturalnie: raw 120/120,
application 117/117. Nie oznacza to poprawnosci wszystkich zapytan:
model znacznie czesciej nie wywoluje narzedzia dla obslugiwanych prosb.
Raw ma 78 bledow decyzji i 5 semantyki; application 75 decyzji, 6 semantyki
i 6 false positives preflight. Brak bledow protokolu lub argumentow.
Przyklady stalego no_tool: intent_003 (bialko na obiad), 004 (deser bez
miesa), 010 (rybna kolacja), 013 (deser), 031 (obiad), 051 (bez laktozy).

Poprzednie application: 199/228 (87.3%), w tym 5 API errors. Obecne 61.8%
bez awarii oznacza obserwowany spadek o 25.4 pp. Poprzednie raw mialo
149/228 z 49 awariami, wiec nie wolno uznac podobnych procentow ogolnych
za stabilna jakosc. Warunkowo bez API w poprzednim raw bylo 149/179 (83.2%).
Probki modelu sa niezalezne; nie jest to dowod mechanizmu przyczynowego.

**Nie uznajemy korekty promptu za zaakceptowana poprawke calego przeplywu.**
Lokalna naprawa kompletowania pola nie rekompensuje globalnej regresji decyzji.
Nie cofano kodu ani nie strojono go podczas pomiaru. Stan pozostaje odtwarzalny.
Runner nie zapisuje tekstu no_tool; nie ustalono, czy model odmawia,
dopytuje, czy generuje JSON poza narzedziem. Nastepny krok to diagnoza
tego zachowania na kontrolowanych danych i porownanie wariantow promptu,
bez wymuszania toola dla wszystkich wypowiedzi i bez napraw argumentow w backendzie.

Raporty ignorowane przez Git, zachowane bez nadpisywania poprzednich:
- dokumentacja pracy/2026-10-15_post_complete_raw_3x.json
- dokumentacja pracy/2026-10-15_post_complete_application_3x.json
Oba complete=true; hashe zrodel i zbiorow zweryfikowane bez rozbieznosci.
211 testow OK; validate_db: 0 ERROR, 20 WARNING, 9 INFO.
