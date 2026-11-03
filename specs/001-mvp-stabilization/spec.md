# Specyfikacja — stabilizacja istniejącego MVP

Data: 2026-10-22<br>
Wersja dokumentu: 0.3<br>
Status: zakres, progi i DEC-01–03 zatwierdzone; wymagania szczegółowe
rozwijane przed implementacją. Przegląd pięciu SKU wstrzymany przez autorkę.

Nawigacja: [kryteria](acceptance.md) · [plan](plan.md) ·
[zadania](tasks.md) · [weryfikacja](verification.md).

## 1. Cel dokumentu

Dokument określa rezultat, do którego dążymy przed dodawaniem kolejnych
funkcji. Stanowi punkt wyjścia do specyfikacji wymagań w podejściu
spec-driven development (SDD). Opisuje oczekiwany zakres pierwszej wersji,
a nie potwierdzenie, że wszystkie wymienione funkcje są już ukończone.

Dokument jest nadrzędnym opisem granic MVP. Szczegółowe kontrakty
rozwijają te ustalenia. W razie rozbieżności należy uzgodnić i zaktualizować
dokumenty przed implementacją; rozbieżność nie upoważnia do cichej zmiany
zachowania aplikacji. Historyczne raporty pozostają zapisem dawnych wersji.

## 2. Cel pierwszej wersji

Pierwsza wersja ma być ustabilizowanym, lokalnym demonstratorem obecnego
asystenta kulinarnego dla jednej marki spożywczej. Celem tego etapu jest
poprawa niezawodności, jakości odpowiedzi i możliwości oceny istniejącego
przepływu, bez dodawania nowych funkcji użytkowych. Użytkownik opisuje po polsku,
jakiego posiłku szuka. System interpretuje prośbę, wybiera zgodne przepisy
z przygotowanego katalogu, dobiera produkty marki według jawnych reguł
i prezentuje wynik wraz z wartościami odżywczymi.

MVP ma umożliwić demonstrację i ocenę trzech elementów projektu:

1. Interpretacji preferencji zapisanych językiem naturalnym przez LLM.
2. Deterministycznej selekcji przepisów i doboru produktów marki.
3. Kontrolowanej prezentacji danych pochodzących z backendu.

Docelowa wizja obejmuje SaaS i widget na stronach marek. Ich pełna realizacja
nie jest warunkiem ukończenia tego MVP.

## 3. Granice etapu stabilizacji

Punktem odniesienia jest zestaw funkcji istniejących w repozytorium
2026-10-22. Commit i wersję danych utrwalono w
[raporcie bazowym](../../docs/reports/baseline_2026-10-22.md).
Obecność funkcji w kodzie nie oznacza, że jej jakość została zaakceptowana.

| ID | Granica zakresu | Konsekwencja |
| --- | --- | --- |
| Z-01 | Jedna marka demonstracyjna: Winiary | Jeden przygotowany katalog SKU; izolacja wielu klientów wymaga późniejszej specyfikacji. |
| Z-02 | Lokalny sposób uruchomienia obecnego prototypu | Wystarcza istniejący punkt wejścia i instrukcja przekazania zapytania; interaktywna konsola, frontend i publiczne API nie są wymagane. |
| Z-03 | Każde zapytanie jest samodzielne | Nie zakładamy pamięci wcześniejszych wypowiedzi ani obsługi odwołań typu „a teraz bez ryby”. |
| Z-04 | Bez nowych funkcji użytkowych | Poprawiamy i weryfikujemy obecne zachowanie, bez nowych diet, ograniczeń, parametrów i sposobów interakcji. |

Zmiana tych założeń wymaga aktualizacji zakresu i oceny dodatkowej pracy.

### Obowiązujące decyzje

Ta tabela jest bieżącym rejestrem decyzji. Dawne raporty zachowują kontekst,
ale nie zastępują jej ani stanów w `tasks.md`.

| ID | Stan | Ustalenie |
| --- | --- | --- |
| DEC-01 | Zatwierdzona | Nieznane statusy laktozy pozostają. Takie SKU są pomijane przy `lactose_free`. Dodawanie produktów i dopuszczanie kolejnych SKU do tej polityki pozostaje poza MVP. |
| DEC-02 | Zasada zatwierdzona; implementacja oczekuje | Brak wymaganej polityki składnika nie oznacza zgodności. Szczegółowe scenariusze należy dopisać przed zmianą kodu. |
| DEC-03 | Zatwierdzona; implementacja oczekuje | Błąd przygotowania przepisu przerywa zapytanie; nie zwracamy częściowego sukcesu ani pozornego braku wyników. Błędy programistyczne nie są maskowane jako poprawna odpowiedź. |
| DEC-04 | Wstrzymana przez autorkę | Nie prowadzimy obecnie przeglądu źródeł pięciu SKU ani zależnych korekt czy wyłączeń. Luka podstawy makro pozostaje otwarta. |

W tym etapie dopuszczalne są poprawki błędów, zmiany promptu, refaktoryzacja,
korekty istniejących danych, testy, narzędzia pomiarowe i dokumentacja,
jeśli służą obecnym funkcjom. Rozbudowa katalogu o nowe przepisy lub SKU
nie jest warunkiem ukończenia MVP. Przygotowanie testów i nowych przypadków
oceny jest pracą nad weryfikacją, a nie rozszerzeniem możliwości chatbota.

## 4. Użytkownik i podstawowy scenariusz

Użytkownikiem jest osoba szukająca pomysłu na posiłek z uwzględnieniem
preferencji obsługiwanych przez katalog. Autorka projektu przygotowuje
dane, reguły oraz środowisko demonstracyjne poza rozmową z użytkownikiem.

Przykładowe zapytanie: „Poleć dwie szybkie kolacje wegańskie do 30 minut”.

Oczekiwany przebieg:

1. Użytkownik wprowadza zapytanie po polsku.
2. Aplikacja sprawdza zakres obsługi i interpretuje parametry zapytania.
3. Backend wybiera przepisy zgodne z parametrami.
4. Dla odpowiednich składników dobiera zgodne SKU marki, jeśli są dostępne.
5. Oblicza wartości odżywcze na podstawie finalnego doboru składników.
6. Lokalny renderer przedstawia wynik. Brak wyników lub błąd prowadzi
   do odpowiedniego komunikatu zamiast wygenerowania zastępczego przepisu.

System może zwrócić mniej propozycji niż zażądano, jeżeli katalog nie zawiera
wystarczającej liczby zgodnych przepisów. Nie rozluźnia samodzielnie ograniczeń.

## 5. Istniejące funkcje objęte stabilizacją

Identyfikatory MVP oznaczają obszary zakresu. Szczegółowe wymagania
i przypadki akceptacyjne zostaną wyprowadzone z nich w kolejnym kroku SDD.
Poniższa lista nie jest planem dodania funkcji; określa, które istniejące
mechanizmy mają zostać opisane, sprawdzone i poprawione w razie błędów.

| ID | Obszar | Oczekiwany rezultat |
| --- | --- | --- |
| MVP-01 | Interpretacja zapytania | Rozpoznanie parametrów i decyzji o wyszukiwaniu na podstawie polskiej wypowiedzi. |
| MVP-02 | Filtrowanie i ranking | Wybór przepisów z katalogu według jawnych reguł, z zachowaniem aktywnych ograniczeń. |
| MVP-03 | Dobór produktów marki | Zastosowanie reguł wyboru SKU dla marki demonstracyjnej bez wymyślania produktów. |
| MVP-04 | Wartości odżywcze | Obliczenie kcal, białka, tłuszczów i węglowodanów z danych finalnie użytych składników i SKU. |
| MVP-05 | Prezentacja | Odpowiedź po polsku z nazwą przepisu, czasem, porcjami, makro na porcję oraz dostępnymi składnikami i instrukcjami. |
| MVP-06 | Kontrolowane sytuacje wyjątkowe | Rozróżnienie braku wyników, braku wyszukiwania, niepoprawnych argumentów, błędu danych i niedostępności LLM. |
| MVP-07 | Przygotowany katalog | Dane i polityki wystarczające do demonstracji, sprawdzone walidatorem i przeglądem treści. |
| MVP-08 | Weryfikacja i odtwarzalność | Testy, ewaluacja LLM oraz opis uruchomienia i odtworzenia wersji demonstracyjnej. |

### Obecnie obsługiwane parametry

- Dieta: brak wskazania, wegetariańska, wegańska, pescetariańska.
- Preferowane źródło białka: brak wskazania, mięso lub ryby, z kontrolą
  sprzeczności z dietą.
- Ograniczenia: `gluten_free`, `lactose_free` oraz ich połączenie.
- Cel żywieniowy: standardowy, niskokaloryczny, wysokobiałkowy lub keto.
- Kategoria: śniadanie, lunch, obiad, kolacja, deser lub przekąska.
- Maksymalny czas przygotowania i liczba oczekiwanych propozycji.

`gluten_free` i `lactose_free` są już obecne w schemacie narzędzia,
backendzie i testach. Ich wymienienie oznacza utrzymanie i weryfikację
istniejącej obsługi. MVP nie obejmuje wdrażania nowych ograniczeń ani
rozszerzania znaczenia obecnych flag.

Cele żywieniowe podlegają regułom katalogu, filtrowania i rankingu.
Nie oznaczają indywidualnego planu dietetycznego. Dokładne progi,
wartości domyślne, negacje i interpretacje słów takich jak „szybki”
muszą zostać opisane w szczegółowych wymaganiach.

### Zasady doboru SKU i prezentacji

- Produkt marki może zostać użyty tylko wtedy, gdy istnieje w katalogu
  i spełnia obowiązujące reguły zgodności.
- Promocja marki nie ma pierwszeństwa przed ograniczeniami użytkownika.
- Brak odpowiedniego SKU pozwala pozostawić składnik generyczny wyłącznie
  wtedy, gdy sam składnik spełnia aktywne warunki.
- Makro wynika z finalnego wyboru, z rozróżnieniem ilości na cały przepis
  i wartości na porcję.
- LLM interpretuje zapytanie; backend wybiera wyniki i oblicza wartości,
  a lokalny renderer przedstawia dane. Model nie dopisuje faktów do odpowiedzi.
- Puste sekcje danych są pomijane. Niepoprawny payload powoduje komunikat
  błędu zamiast zgadywania brakujących informacji.

## 6. Granice obsługi

Ograniczenia bez glutenu i bez laktozy oznaczają zgodność z udokumentowaną
polityką katalogu. Nie są deklaracją certyfikacji, pomiaru zawartości substancji
ani gwarancją bezpieczeństwa dla osoby z alergią.

MVP nie obejmuje doboru przepisów dla alergii ani oceny kontaktu z alergenami.
„Bez laktozy” nie jest zamiennikiem „bez mleka” lub „bez nabiału”.
Nieobsługiwane wymaganie nie może zostać świadomie pominięte lub zastąpione
innym filtrem. Zakres rozpoznawania takich próśb oraz znane pomyłki wymagają
osobnych przypadków ewaluacyjnych; nie zakładamy bezbłędnego rozpoznawania
dowolnej parafrazy przez model lub reguły tekstowe.

## 7. Poza zakresem pierwszej wersji

- Nowe funkcje użytkowe, w tym nowe diety, ograniczenia i parametry zapytania.
- Rozbudowa katalogu o kolejne przepisy, produkty lub marki jako cel tego etapu.
- Zwiększanie liczby SKU dopuszczonych do polityki laktozy: obecne nieznane
  statusy pozostają, a takie SKU nadal są wykluczane przy `lactose_free`
  (decyzja autorki z 2026-10-22). Weryfikacja podstawy makro istniejących
  danych jest odrębną kwestią i nie oznacza dopuszczenia SKU do tej polityki.
- Nowy interaktywny interfejs konsolowy lub inny nowy sposób obsługi użytkownika.
- Produkcyjny SaaS, konta klientów, role, płatności i abonamenty.
- Jednoczesna obsługa wielu marek i izolacja ich danych.
- Osadzalny widget, rozbudowany frontend i panel administracyjny.
- Publiczne API oraz produkcyjne wdrożenie i skalowanie usługi.
- Pamięć rozmowy, profile użytkowników i długoterminowa personalizacja.
- Dowolne wykluczenia składników, obsługa alergii i porady medyczne.
- Generowanie nowych przepisów lub dowolnych zamienników w trakcie rozmowy.
- Wyszukiwanie w internecie podczas rekomendacji i automatyczne aktualizacje
  deklaracji produktów.
- Zaawansowane wyszukiwanie semantyczne i infrastruktura wektorowa.
- Swobodna redakcja odpowiedzi przez drugi LLM oraz brand voice wielu marek.
- Dashboard analityczny i badanie skuteczności marketingowej produktu.

Narzędzia generowania danych mogą wspomagać przygotowanie katalogu.
Ich wynik wymaga weryfikacji przed dopuszczeniem do demonstracji.

## 8. Warunki uznania MVP za ukończone

Jedyną listą kryteriów ukończenia jest [acceptance.md](acceptance.md),
obejmująca ACC-01–ACC-14 i zatwierdzone progi. Stan wykonania pracy zapisujemy
w [tasks.md](tasks.md), a powiązania z dowodami w [verification.md](verification.md).
Nie utrzymujemy tu drugiej checklisty.

Kontrola bazowa została wykonana. Skład końcowych zbiorów i przypadki
pomiarowe pozostają do przygotowania. Problem routingu oraz wstrzymana
luka makro nadal nie są zamknięte; samo przejście istniejących testów
nie stanowi akceptacji MVP.

## 9. Kolejny krok SDD i kontrola zmian

Stan zastany, kontrola bazowa i wstępna mapa dowodów są zapisane.
Najbliższy krok to T005: szczegółowe wymagania integralności i błędów
wynikające z DEC-02/03. Kolejność opisuje [plan](plan.md), a stan prac
[zadania](tasks.md). Nie uruchamiamy ponownie wykonanych etapów na podstawie
dawnych notatek.

Ocena obejmuje poprawność interpretacji i routingu, stabilność w powtórzeniach,
zgodność rekomendacji z ograniczeniami, poprawność liczb i produktów,
czytelność oraz kompletność odpowiedzi względem danych, a także zachowanie
w sytuacjach błędnych. Zatwierdzone progi są w `acceptance.md`; przypadki
i konfiguracja kampanii muszą zostać ustalone przed jej wykonaniem.

Nowa funkcja poza powyższym zakresem trafia do planu dalszego rozwoju.
Włączenie jej do MVP wymaga jawnej aktualizacji tego dokumentu wraz
z uzasadnieniem i wpływem na warunki ukończenia.

## 10. Dokumenty powiązane

- [Indeks dokumentacji technicznej i raportów](../../docs/README.md).
- [Architektura obecnego kodu](../../docs/architecture.md).
- [Kontrakt danych](../../docs/reference/data-contract/README.md).
- [Stan zastany](../../docs/archive/baseline/current_state_2026-10-22.md)
  i [kontrola bazowa](../../docs/reports/baseline_2026-10-22.md).
