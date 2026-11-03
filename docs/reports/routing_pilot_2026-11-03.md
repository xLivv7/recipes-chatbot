# Mały pilotaż V0/V2 — wynik z 2026-11-03

Status: kompletny pomiar diagnostyczny, 120 wywołań API. Aktywny prompt bez zmian.
Instrumentacja i protokół: commit `33bde4e`. Autorka jednoznacznie zatwierdziła
20 kontrolowanych zapytań, V0/V2, OpenAI API, 120 wywołań i opisany koszt.
Duża kampania T009 oraz przegląd pięciu SKU pozostają wstrzymane.

## Warunki

- Celowany zbiór rozwojowy: 20 przypadków, w tym 14 próśb tool i 6 no_tool.
- 2 warianty × 3 próby × 20 przypadków = 120 wywołań, bez retry.
- Raw: bez preflight i rzeczywistego wyszukiwania. Model otrzymał wyłącznie
  kontrolowane zapytania, prompt i schemat. Dane bazy nie były payloadem API.
- `gpt-4o-mini`, resolved model `gpt-4o-mini-2024-07-18` we wszystkich próbach.
- Temperatura 0.1, auto, parallel_tool_calls=false, max_completion_tokens=512.
- 0 błędów API, 0 odpowiedzi uciętych przez limit. Wszystkie próby wykonane.
- Przed pomiarem 244 testy instrumentacji i regresji przeszły bez błędów i pominięć.

## Wyniki

| Metryka | V0 — obecny prompt | V2 — instrukcja kanału i zmiana formy przykładów |
| --- | --- | --- |
| Poprawne oceny | 42/60 (70%) | 57/60 (95%) |
| Obsługiwane prośby | 24/42 | 42/42 |
| Prawidłowe no_tool | 18/18 | 15/18 |
| Przypadki poprawne we wszystkich 3 próbach | 14/20 | 19/20 |
| Poprawny JSON w złym kanale, nadal porażka | 18 | 0 |

V0 we wszystkich trzech próbach nie wywołał narzędzia dla sześciu znanych
przypadków: intent_003/004/010/013/031/051. Zamiast wywołania zwracał
poprawne argumenty jako tekst JSON. V2 poprawnie obsłużył te przypadki,
ale trzykrotnie wywołał narzędzie dla `routing_004`:
„Mam alergię na orzechy, podaj bezpieczny lunch.” Oczekiwano no_tool;
model podał parametry zwykłego lunchu, pomijając nieobsługiwane wymaganie.

## Decyzja zgodna z regułą ustaloną przed pomiarem

Warunkiem wyboru kandydata było poprawne no_tool we wszystkich 18 próbach.
**V2 nie spełnia tego warunku. Pozostaje V0.** Nie zmieniono reguły po
obejrzeniu 95% wyniku ogólnego ani nie zmieniono etykiety `routing_004`.

V2 jest obiecujący pod względem kanału narzędzia, ale nie został dopuszczony
przez protokół tego pilotażu. To nie dowodzi ogólnej poprawności V0:
jego znany problem routingu nadal pozostaje otwarty.

W obecnej aplikacji lokalna funkcja `mentions_unsupported_allergy` blokuje
dosłowną wypowiedź `routing_004` przed modelem — potwierdzono to osobną
kontrolą offline. Pilotaż raw celowo pomijał tę ochronę. Porażka V2 jest
więc błędem decyzji modelu; nie dowodem, że aplikacja w tym zapytaniu
rzeczywiście wykonała wyszukiwanie. Oceny application nie przeprowadzano.

## Koszt

Raportowane usage: **282 858 tokenów wejściowych i 4673 wyjściowych**.
Przy [standardowych stawkach modelu](https://developers.openai.com/api/docs/models/gpt-4o-mini)
0,15 USD/milion wejścia i 0,60 USD/milion wyjścia daje to **0,0452325 USD**
(około 4,5 centa), bez zniżki cache i podatków. To obliczenie z usage,
nie odczyt faktury lub salda konta. Faktyczne rozliczenie może uwzględniać cache.

Konserwatywna lokalna rezerwa wyniosła 0,2255679 USD, poniżej progu 0,50 USD.
Rezerwa nie jest kwotą naliczoną; wcześniejsze 0,23 USD było szacunkiem.

## Dowody i ograniczenia

[Manifest](../../dokumentacja%20pracy/2026-11-03_routing_pilot_01/manifest.json),
[wyniki wszystkich prób](../../dokumentacja%20pracy/2026-11-03_routing_pilot_01/results.json),
[porównanie](../../dokumentacja%20pracy/2026-11-03_routing_pilot_01/comparison.json).
Surowe dowody pozostają w ignorowanym katalogu materiałów pracy; ten raport
zachowuje wersjonowane podsumowanie i decyzję.

Dobór znanych niepowodzeń i kontroli ogranicza generalizację. Wynik 95%
nie jest skutecznością dla całej populacji zapytań ani końcowym zaliczeniem
ACC-09–ACC-11. Nie oceniono jakości danych, logiki rekomendacji, SKU,
czytelności i pełnego przepływu. Nie zmieniano kodu lub promptów podczas prób.

Przyszły eksperyment może sprawdzić połączenie poprawionego kanału z
utrzymaniem granic obsługi, ale wymaga osobnej hipotezy i planu przed pomiarem.
Pełna ocena powinna osobno mierzyć routing, logikę i dane, renderer,
czytelność oraz końcowy przepływ, z niezależnym holdoutem. Nie uruchomiono
automatycznie kolejnej kampanii ani nie wdrożono V2.
