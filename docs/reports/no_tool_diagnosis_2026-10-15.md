# Diagnoza odpowiedzi bez tool calla

Data: 2026-10-15. Prompt niezmieniony wzgledem 6e73a65 i poprzedniej kampanii.
Stary raport nie zawieral tresci no_tool, wiec nie odtwarzamy historycznych
odpowiedzi. Wykonano nowy, celowany pomiar diagnostyczny.

## Co zmierzono
Wybrano szesc wczesniej niepoprawnych cases: intent_003, 004, 010, 013,
031, 051, oraz dwie kontrole: intent_015/025. Po 2 powtorzenia, razem
16 wywolan raw, gpt-4o-mini-2024-07-18, temperatura 0.1, auto,
parallel_tool_calls=false. Bez recipe lookup i bez danych bazy w API.
Nie zmieniano zapytan, expected ani instrukcji.

## Wynik: JSON jako zwykla wiadomosc, nie wywolanie narzedzia
- Szesc problematycznych cases w obu probach: tool_call_count=0,
  finish_reason=stop, refusal=null, content zawiera obiekt JSON argumentow.
- 10 odpowiedzi ma blok Markdown json, 2 sa surowym JSON-em (intent_010).
- To nie sa odmowy, pytania doprecyzowujace ani puste odpowiedzi w tej probce.
- Po zdjeciu ramki Markdown WYLACZNIE do analizy, wszystkie 12 obiektow
  przechodzi parse_recipe_tool_arguments i dokladnie odpowiada expected.
- Dwie kontrole wywoluja tool poprawnie w obu probach: 4 prawidlowe calle,
  finish_reason=tool_calls. API errors: 0. Ocena routingu nadal wynosi 4/16;
  nie awansowano tekstowego JSON-a na sukces.

Przyklad rzeczywistego content dla intent_003 (bialko na obiad):

```json
{"diet":"none","protein_preference":"none","restrictions":[],"nutrition_goal":"high_protein","category":"obiad","top_n":3}
```

Jest to zawartosc zwyklej odpowiedzi assistant, a nie function.arguments
w tool_calls. Aplikacja prawidlowo nie wyszukuje na podstawie tego tekstu.

## Rozdzielenie ustalen od hipotezy
Potwierdzony objaw: w nowych probach parametry sa poprawne, lecz model
wybral zly kanal. Najbardziej prawdopodobna hipoteza to nasladowanie
blokow JSON jako formatu odpowiedzi po dodaniu pelnych przykladow w systemie.
Sam ten pomiar nie izoluje przyczyny. Nie wiemy, co dokladnie zawieralo
wszystkie 78/75 no_tool poprzedniej kampanii, bo nie zapisano ich tresci.
Zestaw zostal wybrany do diagnozy znanych porazek, wiec 4/16 nie jest
estymata jakosci na wszystkich zapytaniach ani holdoutem.

## Instrumentacja i dalszy krok
Ewaluator zapisuje teraz no_tool_content, no_tool_refusal i finish_reason
(schema_version=3). Zmiana dotyczy tylko eval, nie odpowiedzi produkcyjnej.
Pola sa null, gdy model nie byl wywolany lub wystapil brak choices/API.
Nie dodano parsowania tekstowej odpowiedzi do backendu i nie zmieniono ocen.
216 testow OK (5 nowych); baza 0 ERROR, 20 WARNING, 9 INFO.
Raport i wejscia: dokumentacja pracy/2026-10-15_no_tool_diagnostic_report.json
oraz 2026-10-15_no_tool_diagnostic_cases.json. Wszystkie hashe zgodne.
Tresc i hashe main.py/system_prompt odpowiadaja poprzedniemu pomiarowi.

Nastepny kontrolowany eksperyment powinien dotyczyc rozroznienia tool calla
od tekstowego JSON-a: jasna instrukcja uzycia narzedzia oraz przyklady
rzeczywistych wywolan zamiast sugerowania formatu zwyklej odpowiedzi.
Nie wymuszac narzedzia globalnie (sa poprawne no_tool) i nie zamieniac
JSON-a z content na wywolanie w fallbacku. Promptu w tym etapie nie zmieniono.
