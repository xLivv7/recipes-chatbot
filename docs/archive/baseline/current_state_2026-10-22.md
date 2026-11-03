# Stan zastany projektu przed etapem stabilizacji w SDD

> Zapis historyczny. Dokument przeniesiono podczas organizacji SDD;
> odsyłacze prowadzą do nowych lokalizacji. Bieżące ustalenia są w
> [specyfikacji](../../../specs/001-mvp-stabilization/spec.md), a stan prac
> w [zadaniach](../../../specs/001-mvp-stabilization/tasks.md).

Data przeglądu: 2026-10-22<br>
Wersja dokumentu: 0.1<br>
Status: propozycja opisu punktu wyjścia; przegląd kodu i dokumentacji.

## 1. Cel i charakter dokumentu

Dokument opisuje prototyp istniejący w chwili rozpoczęcia ustandaryzowanego
etapu stabilizacji w podejściu spec-driven development (SDD). Służy jako
punkt odniesienia dla wymagań jakościowych, późniejszych zmian i opisu
procesu w pracy inżynierskiej.

Opis zachowania kodu nie oznacza jego akceptacji. Błędy i ograniczenia
stanu zastanego nie stają się wymaganiami docelowymi. Zakres dalszych prac
określa [dokument MVP](../../../specs/001-mvp-stabilization/spec.md): poprawa obecnych funkcji bez dodawania
nowych możliwości użytkowych.

Dokument jest historycznym zapisem punktu wyjścia. Dalszy rozwój powinien
być rejestrowany w specyfikacjach, decyzjach i raportach z weryfikacji.
Korekty błędów w tym opisie należy oznaczać jawnie.

## 2. Identyfikacja stanu i granice przeglądu

| Element | Stan w chwili przeglądu |
| --- | --- |
| Commit HEAD | `739586a4ffec05a61c284deb62b1a6302eb3cfda` |
| Podstawa opisu | Odczyt kodu, kontraktów i opisów historycznych eksperymentów. |
| Aktualny snapshot bazy | Nie wykonano; wersja danych nie została ustalona w tym przeglądzie. |
| Wersje środowiska i zainstalowanych bibliotek | Nie zinwentaryzowano w tym przeglądzie. |
| Nowe uruchomienie testów i walidatora | Nie wykonano na potrzeby dokumentu. |
| Nowa ewaluacja z użyciem API | Nie wykonano na potrzeby dokumentu. |

Commit identyfikuje wersjonowane źródła, a nie zawartość lokalnej bazy,
plików ignorowanych przez Git lub środowiska. Dokument nie jest jeszcze
pełnym, odtwarzalnym snapshotem uruchomieniowym. Wyniki przywołane poniżej
są historyczne i pochodzą ze wskazanych raportów opisowych; w tym przeglądzie
nie przeprowadzono ponownego audytu surowych raportów JSON.

## 3. Przeznaczenie i forma prototypu

Projekt jest lokalnym prototypem asystenta kulinarnego dla marki spożywczej.
Przyjmuje polskie zapytanie o posiłek, interpretuje preferencje, wyszukuje
przepisy w przygotowanym katalogu, dobiera produkty marki i prezentuje
wartości odżywcze. Bieżący przykład uruchomienia dotyczy marki Winiary.

Punkt wejścia w `main.py` uruchamia zapytanie zapisane w kodzie i wypisuje
odpowiedź. Funkcja `chat_with_bot(user_message, brand_name)` przyjmuje
zapytanie programistycznie. Nie ma interaktywnej pętli konsolowej, pamięci
rozmowy ani gotowego widgetu. Każde wywołanie buduje kontekst od nowa.

Docelowa wizja SaaS jest szersza od prototypu. Istnienie modeli klientów
w bazie nie oznacza ukończonej izolacji danych wielu marek.

## 4. Struktura i odpowiedzialności

| Plik lub katalog | Obecna rola |
| --- | --- |
| [main.py](../../../main.py) | Prompt, kontrola zakresu zapytania, wywołanie LLM, obsługa narzędzia i przekazanie wyniku do renderera. |
| [core/database.py](../../../core/database.py) | Modele SQLAlchemy i konfiguracja połączenia PostgreSQL. |
| [core/recommendation_catalog.py](../../../core/recommendation_catalog.py) | Wczytanie danych z bazy do katalogu w pamięci. |
| [core/recommendations.py](../../../core/recommendations.py) | Filtry, wybór SKU, obliczenia odżywcze, ranking i dobór wyników. |
| [core/recommendation_preferences.py](../../../core/recommendation_preferences.py) | Słowniki diet i ograniczeń oraz kontrola sprzeczności preferencji. |
| [core/llm_tools.py](../../../core/llm_tools.py) | Schemat i opisy parametrów narzędzia `get_recommendations`. |
| [core/tool_call_validation.py](../../../core/tool_call_validation.py) | Parsowanie i lokalna walidacja argumentów wywołania narzędzia. |
| [core/request_safety.py](../../../core/request_safety.py) | Reguły tekstowe blokujące wzmianki o alergiach i wybrane nieobsługiwane wykluczenia. |
| [core/recommendation_normalization.py](../../../core/recommendation_normalization.py) | Normalizacja wyniku backendu. |
| [core/response_renderer.py](../../../core/response_renderer.py) | Kontrola payloadu i lokalne tworzenie odpowiedzi. |
| [core/validation](../../../core/validation) | Walidacja danych, relacji, słowników, polityk i reguł produktowych. |
| [curation](../../../curation) | Wersjonowane klasyfikacje i decyzje dotyczące danych. |
| [tests](../../../tests) | Testy jednostkowe i integracyjne, w tym testy z kontrolowanymi odpowiedziami API. |
| [evals](../../../evals) | Zbiory przypadków i programy ewaluacji modelu, routingu i renderera. |
| [docs](../..) | Kontrakty, decyzje, protokoły i opisy wyników. |

Przygotowanie danych stanowi osobny przepływ: `fetch_ingredients.py`,
`generate_ingredients_ai.py` i `generate_recipes_ai.py` wspomagają pozyskiwanie
lub generowanie danych, `apply_data_curation.py` stosuje korekty i polityki,
a `validate_db.py` uruchamia walidację. Generowanie danych nie jest częścią
obsługi zapytania użytkownika.

## 5. Przepływ obsługi zapytania

1. Reguły lokalne sprawdzają wzmianki o alergiach oraz wybrane wykluczenia.
   Rozpoznana prośba poza zakresem otrzymuje stały komunikat przed wywołaniem LLM.
2. Dla pozostałych wypowiedzi aplikacja wysyła instrukcję systemową, zapytanie
   i schemat narzędzia do modelu `gpt-4o-mini`. Konfiguracja w kodzie:
   `temperature=0.1`, `tool_choice=auto`, `parallel_tool_calls=false`.
3. Aplikacja oczekuje pojedynczego wywołania `get_recommendations`.
   Brak wywołania daje stały komunikat bez wyszukiwania; zwykły tekst modelu,
   także zawierający JSON, nie jest wykonywany ani prezentowany jako rekomendacja.
4. Argumenty są parsowane i walidowane lokalnie. Niepoprawne argumenty,
   nieznane narzędzie lub wiele wywołań nie uruchamiają wyszukiwania.
5. Backend filtruje katalog, dobiera SKU, oblicza makro i porządkuje wyniki.
6. Wynik jest normalizowany i renderowany lokalnie. Nie ma drugiego wywołania
   LLM redagującego przepisy; wynik rekomendacji nie jest wysyłany do modelu
   w tym przepływie.

Obsługiwane są stałe komunikaty m.in. dla braku wywołania narzędzia,
niepoprawnych argumentów, błędu API, pustego wyniku i niepoprawnego payloadu.
Nie oznacza to obsługi każdej możliwej awarii aplikacji.

## 6. Istniejący zakres funkcjonalny

| Obszar | Zachowanie widoczne w kodzie |
| --- | --- |
| Dieta | `none`, `vegetarian`, `vegan`, `pescetarian`. |
| Źródło białka | `none`, `meat`, `fish`; kontrola sprzeczności z dietą. |
| Ograniczenia | `gluten_free`, `lactose_free` i ich połączenie; są już zaimplementowane. |
| Cel żywieniowy | `standard`, `low_kcal`, `high_protein`, `keto`. |
| Kategorie | Śniadanie, lunch, obiad, kolacja, deser, przekąska. |
| Czas i liczba wyników | Opcjonalny dodatni `time_max` i dodatni `top_n`; schemat nie wyznacza ich górnych granic. |
| Produkty marki | Dobór SKU według uporządkowanych reguł i aktywnych ograniczeń. |
| Wartości odżywcze | Obliczenia dla finalnego doboru składników; wynik dla całości i na porcję. |
| Odpowiedź | Lokalny renderer przedstawia przepisy, liczby i przypisania produktów z payloadu. |

W rankingu `low_kcal` preferuje niższą kaloryczność, a `high_protein` większą
ilość białka na porcję. Nie są to same w sobie sztywne progi kwalifikacji.
Keto obejmuje odrzucenie wyniku z ponad 15 g węglowodanów na porcję i ranking
preferujący mniejszą ilość węglowodanów. Wybór wyników uwzględnia także
różnorodność `dish_type`. To opis reguł projektu, nie definicje diet klinicznych.

Przykłady interpretacji zapisane w prompcie obejmują „szybki” jako 30 minut,
pierwszeństwo jawnego limitu oraz „lekki” jako `low_kcal` bez automatycznego
limitu czasu. Obecność instrukcji nie dowodzi poprawnej interpretacji przez LLM.

## 7. Dane i środowisko

PostgreSQL przechowuje składniki, makro, polityki dietetyczne, klientów,
SKU, reguły doboru oraz przepisy z danymi JSONB. `CATALOG` powstaje przy
imporcie modułu, a więc import części aplikacji wymaga dostępnej bazy.
Zmiany w bazie nie odświeżają automatycznie tego obiektu w działającym procesie.

Konfiguracja korzysta z `DATABASE_URL` i `OPENAI_API_KEY`. Plik `.env`
jest ignorowany przez Git. Nie należy umieszczać jego wartości w dokumentacji.
`requirements.txt` wymienia biblioteki, lecz nie przypina ich wersji.

Katalog `data/` i folder `dokumentacja pracy/` są ignorowane przez Git.
Pierwszy zawiera lokalne dane, drugi m.in. szczegółowe notatki i raporty.
Klasyfikacje z `curation/` są wersjonowane, ale nie zastępują pełnego snapshotu
bazy. Historycznych liczebności katalogu nie potwierdzono nowym odczytem.

Ładowanie katalogu obejmuje SKU i reguły wielu rekordów klientów bez
ograniczenia do klienta przekazanego w żądaniu. `get_recommendations`
nie przyjmuje `client_id`. Argument `brand_name` nie zapewnia izolacji danych.

## 8. Dostępne dowody weryfikacji

### Testy i walidacja

Repozytorium zawiera testy rekomendacji, ograniczeń, SKU, obliczeń,
normalizacji, renderera, kontroli zapytań, argumentów narzędzia i ewaluatorów.
Test z podstawioną odpowiedzią modelu sprawdza zachowanie aplikacji dla tej
odpowiedzi, a nie zdolność LLM do samodzielnej interpretacji wypowiedzi.

Walidator obejmuje encje, przepisy JSONB, relacje, słowniki, polityki diet,
wartości odżywcze i reguły doboru produktów. Poprawność strukturalna danych
nie jest dowodem prawdziwości ich treści.

[Raport diagnostyczny z 2026-10-15](../../reports/no_tool_diagnosis_2026-10-15.md) podaje
216 poprawnych testów oraz walidację bazy: 0 ERROR, 20 WARNING, 9 INFO.
To wynik historyczny, nie potwierdzenie obecnego środowiska. Ostrzeżenia
wymagają indywidualnej oceny przed akceptacją MVP.

### Ewaluacja modelu i przepływu aplikacji

Nowy runner rozdziela tryb `raw` (model bez lokalnych kontroli wejścia)
i `application` (rzeczywista obsługa zapytania z podstawionym wyszukiwaniem).
Pomiar application nie ocenia wyników SQL ani pełnego działania na katalogu.
Szczegóły: [rozdzielona ewaluacja](../../reference/evaluation/separated_routing_evaluation.md).

[Pomiar po pełnych przykładach z 2026-10-15](../../reports/evaluation_complete_examples_2026-10-15.md)
opisuje prompt z commita `6e73a65`, 76 przypadków regresyjnych i trzy
powtórzenia w każdym trybie:

| Tryb | Poprawne oceny | Przypadki poprawne w każdym powtórzeniu |
| --- | --- | --- |
| raw | 145/228 (63,6%) | 46/76 |
| application | 141/228 (61,8%) | 45/76 |

W kampanii nie odnotowano błędów API. Wszystkie zwrócone wywołania narzędzia
były poprawne strukturalnie, lecz wiele obsługiwanych próśb nie wywoływało
narzędzia. Zmiana promptu nie została uznana za zaakceptowaną poprawę
całego przepływu. Wyniki dotyczą konkretnego eksperymentu, a nie ogólnej
skuteczności systemu ani nowego pomiaru dla commita z sekcji 2.

Późniejsza [diagnoza](../../reports/no_tool_diagnosis_2026-10-15.md) objęła sześć znanych
niepowodzeń i dwie kontrole, po dwa powtórzenia. Dwanaście odpowiedzi dla
problematycznych przypadków zawierało poprawne argumenty jako zwykły tekst
JSON zamiast wywołania narzędzia. Cztery odpowiedzi kontrolne poprawnie
wywołały narzędzie. To potwierdza objaw w tej próbce, ale nie dowodzi przyczyny
ani nie wyjaśnia wszystkich błędów wcześniejszej kampanii.

Istnieją również historyczne ewaluacje swobodnych odpowiedzi drugiego LLM.
Nie mierzą obecnej prezentacji przez lokalny renderer. Holdout v1 został
już ujawniony i nie jest niezależnym zbiorem dla dalszego strojenia.
Zobacz [instrukcje ewaluacji](../../../evals/README.md)
i [protokół holdout v1](../evaluation/holdout_v1_protocol.md).

## 9. Znane problemy, ograniczenia i luki dowodowe

| ID | Ustalenie i podstawa | Znaczenie dla stabilizacji |
| --- | --- | --- |
| ST-01 | Historyczny pomiar wykazał brak wywołań narzędzia dla obsługiwanych próśb. | Priorytet dla kontrolowanych eksperymentów routingu; nie należy utożsamiać poprawnego JSON-a w tekście z sukcesem wyszukiwania. |
| ST-02 | Reguły tekstowe mają znane fałszywe blokady i nie obejmują wszystkich parafraz; opisują to kontrakty. | Osobna ocena poprawnych blokad, fałszywych blokad i pominięć. |
| ST-03 | Dla aktywnych ograniczeń potrzebne jest jawne dopuszczenie konceptu i SKU; dla diet vegetarian/vegan brak rekordu polityki konceptu jest w kodzie dopuszczany. | Różne reguły traktowania braku danych wymagają jawnej decyzji i kontroli kompletności katalogu. |
| ST-04 | `orchestrate_top_n` przechwytuje `Exception` podczas przygotowania przepisu i pomija taki wynik. | Może ukrywać błąd jako mniejszą liczbę wyników lub pustą listę; zakres obsługi błędów wymaga przeglądu. |
| ST-05 | Renderer kontroluje strukturę i prezentację, ale nie potwierdza prawdziwości danych ani semantycznej zgodności instrukcji przepisu. | Potrzebny przegląd istniejących danych; testy renderera nie zastępują audytu treści. |
| ST-06 | Brak snapshotu bazy i inwentaryzacji wersji środowiska dla tej daty. | Punkt odniesienia nie jest jeszcze w pełni odtwarzalny. |
| ST-07 | README opisuje starszy przepływ, a część kontraktów łączy pierwotny projekt i późniejsze aktualizacje. | Należy oddzielić obowiązujące ustalenia od historii. |
| ST-08 | Nie ustalono jeszcze kompletu mierzalnych progów akceptacji MVP. | Samo przejście istniejących testów nie zamyka oceny jakości. |

Ograniczenia `gluten_free` i `lactose_free` oznaczają zgodność z polityką
katalogu. Nie potwierdzają certyfikacji, pomiaru ani bezpieczeństwa alergicznego.
Brak pamięci rozmowy, interfejsu webowego i izolacji wielu klientów jest
granicą obecnego MVP, a nie zadaniem do realizacji w tym etapie.

## 10. Przejście do dalszej pracy SDD

Na podstawie tego zapisu należy:

1. Uzupełnić identyfikację danych i środowiska, aby utrwalić punkt odniesienia.
2. Opisać szczegółowe wymagania dla obecnych funkcji i wymagania jakościowe.
3. Powiązać je z testami, pomiarami i znanymi problemami ST-01–ST-08.
4. Ustalić kryteria akceptacji i protokół nowego pomiaru przed jego wykonaniem.
5. Zarejestrować aktualny wynik testów i walidacji oraz osobno zaplanowany
   pomiar LLM jako bazę porównań.
6. Prowadzić poprawki według kolejności: specyfikacja, plan, implementacja,
   weryfikacja i decyzja o przyjęciu zmiany.

Prace dotyczą stabilizacji istniejących możliwości. Ten dokument nie stanowi
zgody na dodawanie nowych funkcji ani potwierdzenia gotowości MVP.
