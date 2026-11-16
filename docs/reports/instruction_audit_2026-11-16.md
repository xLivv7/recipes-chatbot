# Audyt instrukcji interpretacji zapytań — 2026-11-16

Commit źródeł: `5a41f0c`. Zakres: cały pakiet instrukcji chatbotowego routingu
pochodzący z repozytorium. Audyt obejmuje aktywny V0, eksperymentalny V4
i historyczne V1–V3. Wykonano analizę kodu i kontrole offline, bez API i bazy.

**Wynik:** potwierdzono bezwarunkowe „użyj zawsze” sprzeczne z wyjątkami
no_tool, niejednoznaczną regułę „bez mięsa → vegetarian” i dalsze luki
kontraktu. Oddzielnie opisano słabości przykładów oraz różnice aplikacji
i ewaluacji. Nie znaleziono instrukcji nakazującej fish z samego pescetarian.
Audyt nie dowodzi, która z tych cech spowodowała konkretną odpowiedź modelu.

Status po audycie: na osobne polecenie autorki usunięto INS-01 w T018.
Poniższe ustalenia zachowują stan źródeł `5a41f0c`; zakres poprawki i dowody
są w [mapie weryfikacji](../../specs/001-mvp-stabilization/verification.md#t018--usunięcie-ins-01-zakończone).

## 1. Co rzeczywiście otrzymuje model

Ścieżka [chat_with_bot](../../main.py), w. 113–130:

1. Preflight może zatrzymać zapytanie przed modelem.
2. Jeśli nie zatrzyma: jedna wiadomość systemowa z `build_system_prompt`,
   jedna wiadomość użytkownika i jedno narzędzie `get_recommendations`.
3. Narzędzie zawiera opis funkcji oraz siedem parametrów: typy, enumy,
   wymagane pola i opisy. Te opisy są częścią instrukcji dla modelu.
4. Wywołanie: gpt-4o-mini, temperatura 0,1, tool_choice=auto,
   parallel_tool_calls=false. Nie ma wiadomości developer, historii rozmowy
   ani rzeczywistych wiadomości assistant/tool demonstrujących przykłady.

Aktywny builder jest identyczny z `evals/routing_prompts/V0.txt` dla Winiary.
V4 zastępuje ten jeden prompt w eksperymencie; V0 i V4 nie są łączone.
Warianty dzielą ten sam schemat `RECIPE_TOOLS`. Ewaluacja podmienia również
lokalny import buildera w `run_llm_eval.py`; nie znaleziono przypadkowego
wysyłania V0 zamiast wybranego wariantu w sprawdzanej ścieżce.

`spec.md`, dokumentacja, expected przypadków, parser i kod backendu nie są
automatycznie wysyłane modelowi. Renderer buduje odpowiedź lokalnie;
wynik wyszukiwania nie trafia do drugiego modelu w aktywnym przepływie.
Stałe komunikaty odmów w `main.py` również nie są instrukcjami API.

`legacy_final_answer_prompt.py` i `run_final_answer_eval.py` dotyczą osobnego
historycznego pomiaru redakcji odpowiedzi. `fetch_ingredients.py`,
`generate_ingredients_ai.py` i `generate_recipes_ai.py` wywołują model
w osobnych zadaniach przygotowania katalogu. Nie są dołączane do wiadomości
chatbota; ich instrukcji nie należy sumować z aktualnym promptem.

## 2. Ustalenia

P1 oznacza pierwszeństwo w projekcie poprawki instrukcji, P2 kolejny etap
porządkowania. To priorytety audytu, nie dowód wpływu na odsetek błędów.

### INS-01 — „użyj zawsze” kontra jawne wyjątki no_tool — P1

**Rodzaj: rzeczywista niespójność zakresu instrukcji, wszystkie warianty.**

[Opis funkcji](../../core/llm_tools.py), w. 8: „Użyj tej funkcji zawsze, gdy
użytkownik szuka pomysłu na posiłek, prosi o przepis lub chce coś ugotować”.
[Prompt](../../main.py), w. 49/53/70–71: wywołać dla obsługiwanej prośby,
nie wywoływać dla nieobsługiwanych wymagań. V3/V4 doprecyzowują pierwszeństwo
granic, ale wspólny opis funkcji nadal zawiera bezwarunkowe „zawsze”.

Przykład: prośba o lunch bez mleka jest prośbą o posiłek, a zarazem
nieobsługiwanym wymaganiem. Dwa opisy nakazują różne decyzje.
Kierunek poprawki: opis funkcji powinien mówić o prośbie zgodnej z zakresem
i respektować wyjątki. Nie zmieniać globalnie tool_choice na required.

### INS-02 — bezwarunkowe „bez mięsa → vegetarian” — P1

**Rodzaj: nadmierne uogólnienie i brak reguły pierwszeństwa, V0–V4.**

[Prompt](../../main.py), w. 62: „bez mięsa oznacza vegetarian”.
[Opis diet](../../core/llm_tools.py), w. 16: vegetarian wyklucza mięso i ryby,
pescetarian wyklucza mięso, ale dopuszcza ryby. V4, w. 3, dodatkowo wzmacnia
„Wykluczenie mięsa oznacza diet=vegetarian”.

Istniejący `intent_020`: „coś bez mięsa, ale ryby mogą być, na kolację”
ma expected pescetarian/none. Literalne użycie pierwszej reguły daje vegetarian.
Podobna kolizja może powstać przy jawnej diecie vegan połączonej z „bez mięsa”.
Brakuje zastrzeżenia, że jawne doprecyzowanie dozwolonych produktów lub diety
rozstrzyga ogólną frazę. Kierunek: określić kolejność interpretacji diety
i ograniczeń, zachowując pierwotne expected. To nie jest bezpośrednie
wyjaśnienie `intent_032`, który nie zawiera frazy „bez mięsa”.

### INS-03 — niepełny kontrakt zachowania przy no_tool — P2

**Rodzaj: niedopowiedzenie między opisem narzędzia a rolą modelu.**

[Opis restrictions](../../core/llm_tools.py), w. 28: wymagania bez mleka,
bez nabiału i alergia „wymagają doprecyzowania poza narzędziem”.
[Prompt](../../main.py), w. 47–48, ogranicza rolę modelu do decyzji i argumentów,
a końcową odpowiedź powierza aplikacji. Nie opisuje wyraźnie formy no_tool.

`main.py`, w. 139–141, ignoruje content modelu i zwraca własny komunikat.
Zatem wygenerowane przez model pytanie doprecyzowujące nie trafia do użytkownika.
To nie nakaz wywołania narzędzia ani dowód błędnego routingu; tekst sugeruje
jednak czynność, której aktywny interfejs modelu nie realizuje.
Kierunek: jednoznacznie opisać decyzję no_tool i odpowiedzialność aplikacji
za komunikat, bez dorabiania nowego dialogu w ramach MVP.

### INS-04 — przykłady argumentów przypominają odpowiedź tekstową — P1 dla V0

**Rodzaj: niejednoznaczny wzorzec kanału, nie błąd schematu.**

[V0](../../evals/routing_prompts/V0.txt) i V1 pokazują „Zapytanie” oraz blok
Markdown z JSON-em. Wymagają wywołania funkcji, lecz przykład nie przedstawia
rzeczywistej wiadomości assistant z tool_calls. Może zostać odczytany jako
wzór odpowiedzi tekstowej. Historyczne pomiary wykazały zgodne argumenty
w content; nie jest to dowód, że właśnie format przykładów był ich przyczyną.

V2–V4 dodają etykiety narzędzia i zakaz wypisywania argumentów. To zmniejsza
niejednoznaczność instrukcji, lecz nadal są to przykłady tekstowe w systemie.
W T014.3 pojawiła się odpowiedź „Narzędzie/Argumenty” w content mimo zakazu.
Kierunek: zaprojektować i osobno ocenić jednoznaczny wzorzec kanału, zachowując
zakaz wykonywania JSON-a ze zwykłej odpowiedzi.

### INS-05 — przykłady nie pokrywają kluczowych rozróżnień — P1 dla diagnozy diet/protein

**Rodzaj: luka przykładów, nie sprzeczność reguł.**

Wszystkie warianty mają te same pięć zapytań i argumentów:

| Cecha | Pokrycie pięciu przykładów |
| --- | --- |
| protein_preference | none: 5/5; fish/meat: 0 |
| diet | none: 3, vegan: 1, vegetarian: 1; pescetarian: 0 |
| top_n | 3: 5/5; inna liczba: 0 |
| restrictions | puste: 5/5; aktywne ograniczenie: 0 |
| category | śniadanie: 1, kolacja: 4; deser/lunch/obiad/przekąska: 0 |
| no_tool | 0 przykładów |

Argumenty wszystkich pięciu przykładów są poprawne i zgodne z opisem ich
zapytań. Brakuje jednak par pokazujących „ryby są dozwolone” wobec „chcę rybę”,
a także granic odmowy. Dodawanie kolejnych zdań przy niezmienionych przykładach
nie sprawdzało hipotezy o wartości takich kontrastów. Kierunek: w nowej,
zapisanej hipotezie dopuścić zmianę przykładów; nie zmieniać ich po cichu
w historycznych wariantach ani kopiować wyłącznie problematycznego zapytania.

### INS-06 — inne granice negacji w modelu i preflight — P1 w ocenie całej aplikacji

**Rodzaj: rozbieżność warstw aplikacji, nie dwie instrukcje otrzymane przez model.**

Prompt i opis restrictions mówią, że negacja nie dodaje ograniczenia.
[Preflight](../../core/request_safety.py), w. 14–18/40–44, blokuje także
wzmianki zanegowane. W kontroli offline przed API zatrzymano:

- „Nie mam alergii, podaj kolację.”;
- `guard_005`: „Nie musi być bez jaj, chcę kolację” — expected tool;
- `guard_006`: „Bez laktozy i szybki obiad” — expected tool; blokuje go
  gramatyka listy, mimo że oba wymagania są obsługiwane.

Jest to znany koszt konserwatywnej ochrony, opisany w jej kontraktach.
Z punktu widzenia expected dwa ostatnie przypadki pozostają błędnymi blokadami.
Model w application nie otrzymuje wtedy żadnych instrukcji ani zapytania,
więc edycja samego promptu nie naprawi tego zachowania. Raw celowo je otrzymuje.
Kierunek: zachować osobne metryki i odrębnie zaplanować decyzję o preflight;
ten audyt nie upoważnia do osłabienia ochrony ani zmiany etykiet.

### INS-07 — brak rozstrzygnięcia wielu wartości jednego pola — P2

**Rodzaj: luka specyfikacji interpretacji, bez wyniku LLM w tym audycie.**

Schemat dopuszcza jedną category i jeden nutrition_goal. Opis kategorii mówi
„jeśli lunch, zawsze lunch” oraz „jeśli obiad, obiad”; nie określa wyboru,
gdy użytkownik wymieni oba. Analogicznie „lekka kolacja keto” uruchamia dwie
reguły celu, a pole przyjmuje tylko jedną wartość. „Sprzeczne preferencje”
nie rozstrzyga, czy takie połączenie jest sprzeczne, czy tylko niereprezentowalne.
Kierunek: przed implementacją ustalić politykę dla takich próśb w zakresie
istniejących pól; nie dodawać automatycznie wielowartościowych parametrów.

### INS-08 — inna konfiguracja pomiaru i aktywnego wywołania — P2

**Rodzaj: różnica warunków wykonania, nie konflikt znaczenia parametrów.**

Model, temperatura, auto i parallel_tool_calls=false są wspólne.
`BudgetedClient.create` w pomiarze wymusza max_completion_tokens=512;
aktywny `chat_with_bot` nie ustawia tego limitu jawnie. Klient kampanii ma
retry=0 i timeout=30, a konstruktor aktywnego klienta nie podaje tych wartości.
Retry/timeout nie są instrukcjami modelu, ale wpływają na wykonanie i koszt.

To jawny protokół małego eksperymentu; nie błąd porównania V0/V4, bo oba
warianty miały te same ustawienia. Nie należy jednak nazywać pomiaru pełnym
odtworzeniem konfiguracji aktywnej aplikacji. Brak ucięć w T016 nie daje
podstaw do przypisania fish limitowi odpowiedzi.

## 3. Co jest spójne

| Pole / mechanizm | Wniosek |
| --- | --- |
| diet | Enum i domyślny none są zgodne; niejednoznaczne pierwszeństwo frazy „bez mięsa” wobec doprecyzowanej diety opisuje INS-02. |
| protein_preference | Prompt, V4 i opis parametru zgodnie wymagają jawnej prośby o fish/meat; sama dieta pescetarian oznacza none. Nie znaleziono przeciwnej instrukcji. |
| restrictions | Słowniki gluten_free/lactose_free, niezależność od vegan, brak zamiany bez mleka na lactose_free oraz unikalność tablicy są spójne. Granice preflight opisuje INS-06. |
| nutrition_goal | Enum i podstawowe mapowania celu są zgodne. Problem wielu jednoczesnych wartości opisuje INS-07. |
| category | Sześć wartości i domyślna kolacja są zgodne; nie brakuje deseru ani obsługi lunchu. |
| time_max | Opcjonalna dodatnia liczba całkowita, brak null, jawny limit przed domyślnymi 30 minutami i oddzielenie czasu od celu są zgodne. |
| top_n | Dodatnia liczba całkowita, domyślnie 3; brak maksimum 3 w schemacie. Wcześniejsza odmowa czterech propozycji nie wynikała z takiego zapisanego limitu. |
| Kanał i liczba wywołań | Auto dopuszcza brak wywołania, parallel_tool_calls=false jest zgodne z jednym narzędziem; parser dodatkowo odrzuca wiele wywołań. |
| Walidacja przykładów | 25 wystąpień pięciu identycznych przykładów w V0–V4 przeszło parser; nie są to 25 niezależne scenariusze ani próby LLM. |

Opis „brak źródła białka” warto ujednoznacznić jako brak jawnej preferencji.
`none` nie jest dietą bez białka ani zakazem ryb. Pescetarian + fish może
być poprawne dla innej prośby, więc samo dopuszczenie takiego zestawienia
przez parser nie jest niespójnością. Problem T016 dotyczy jego przypisania
do wypowiedzi bez jawnej preferencji, nie legalności kombinacji.

## 4. Dowody i dalszy zakres

[Kontrole i hashe źródeł](../../dokumentacja%20pracy/2026-11-16_instruction_audit/audit_checks.json),
[przechwycone pakiety V0/V4](../../dokumentacja%20pracy/2026-11-16_instruction_audit/wire_requests.json).

Wyodrębniono dwie funkcje z AST `main.py` i uruchomiono je z lokalną atrapą
klienta. Nie importowano modułu main, SDK API ani bazy. Zweryfikowano strukturę
wiadomości i narzędzia, zgodność aktywnego promptu z V0, argumenty przykładów
oraz pięć przypadków preflight. Wykonano 3 przechwycenia żądania do atrapy,
**0 rzeczywistych wywołań API**. Nie uruchamiano generowania katalogu.

Wnioski stanowią część diagnozy T017. Audyt nie kończy całego zadania:
pozostają tabela kontrastów, wybrana hipoteza, scenariusze i protokół
weryfikacji. Kod aplikacji, prompty, schemat, expected i wcześniejsze raporty
pozostawiono bez zmian. Zalecenia wymagają zaprojektowania wersjonowanej
poprawki przed kolejnym eksperymentem; nie należy wdrażać wszystkich naraz
i przypisywać późniejszej zmiany wyniku jednemu wybranemu elementowi.
