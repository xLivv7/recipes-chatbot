# T029 — kontrola kompletności przed wyszukiwaniem

W wewnętrznym trybie `facts_checked_v1` aplikacja zatrzymała wszystkie 11
błędnych wyszukiwań zaobserwowanych w przebiegu aplikacyjnym T027.
Liczba poprawnie obsłużonych prób wyniosła 25/36. Pozostałych 11 prób
zakończyło się komunikatem MSG-06. Domyślny chatbot nadal używa legacy/V0.

## Metoda

Odtworzyliśmy trzy odpowiedzi IR-1 na każde z 12 zapytań. Program sprawdza
SHA-256 plików z odpowiedziami i etykietami T027. W pierwszym przebiegu
dekoduje zapisane odpowiedzi dostawcy, waliduje IR-1, kompiluje fakty
i uruchamia CMP-1. W drugim podaje te same odpowiedzi przez atrapę klienta
do funkcji `chat_with_bot`. Przechodzi przez rzeczywisty preflight, adapter
i wybór komunikatu. Atrapa wyszukiwarki rejestruje przekazane parametry.
Ocenę z etykietą wykonuje dopiero ewaluator. Koszt nowych wywołań API wyniósł 0 USD.
[Protokół CMP-1](../../specs/001-mvp-stabilization/interpretation-completeness.md) ·
[Pomiar T027](t027_interpretation_2026-11-18.md)

## Wyniki na tych samych 36 odpowiedziach

| Miara | Sam adapter IR-1 z CMP-1 | Pełna ścieżka aplikacji z CMP-1 |
| --- | ---: | ---: |
| Poprawna decyzja i poprawne parametry lub właściwa odmowa | 22/36 | 25/36 |
| Poprawne wyszukania | 19 | 19 |
| Poprawne odmowy | 3 | 6 |
| Błędne wyszukania przed dodaniem CMP-1 | 14 | 11 |
| Wyszukania zatrzymane przez CMP-1 z MSG-06 | 14 | 11 |
| Błędne wyszukania przepuszczone do wykonania | 0 | 0 |
| Poprawne obserwacje błędnie zablokowane przez CMP-1 | 0/22 | 0/25 |

Na prośbę „deser bez mięsa” model trzykrotnie pominął kategorię. Kompilator
poprawnie wywnioskował dietę wegetariańską, lecz zastosował domyślną kolację.
CMP-1 znalazł słowo „deser” bez odpowiadającego mu faktu i zatrzymał trzy
wywołania. Pozostałe osiem blokad aplikacyjnych obejmowało cztery pominięcia
lunchu, jedno pominięcie celu niskokalorycznego i trzy prośby o wegański
obiad z wymaganym mięsem. Trzy prośby o bezmleczny lunch odrzucił
istniejący preflight, zanim aplikacja sięgnęła po zapisaną odpowiedź.

Jakość interpretacji modelu w T027 wynosiła 22/36, a zgodność pełnego
zestawu faktów 19/36. Zatrzymanie błędnego wyszukania zachowuje ocenę
niepowodzenia próby. Po MSG-06 brak wykonanych parametrów, więc oceny diety,
białka, wykluczeń, celu, kategorii, czasu i liczby wyników są nieadekwatne
(`null`). Trzy poprawne wyszukania dla „na wieczór” nadal korzystają
z trafnego defaultu kolacji mimo pominięcia tej kategorii przez model.

## Zakres dowodu i odtworzenie

Testy obejmują 35 kontrastów CMP-1, 35 poprawnych przykładów IR-1, pięć
próśb odblokowanych w T024, oryginalne fragmenty Unicode, cytaty, operatory,
błędy protokołu i źródła oraz identyczność żądania SDK obu trybów.
Pełna regresja przeszła 372/372 bez pominięć. Blokady SDK i zapisów do
katalogu zarejestrowały zero prób. Pełna regresja wykonała 35 odczytów
PostgreSQL. Zapisy testowe dotyczyły wyłącznie SQLite w pamięci.

Z katalogu projektu, w środowisku z zainstalowanymi zależnościami i lokalnym
archiwum kampanii T027, polecenie wypisuje szczegóły wszystkich 36 obserwacji
i kończy się błędem przy niespełnieniu progów replay.

```powershell
venv/Scripts/python.exe -X utf8 -m evals.replay_interpretation_completeness
```

Zbiór pochodzi z diagnostyki, na której zaprojektowano reguły. Poza
słownikiem CMP-1 parafraza może nadal prowadzić do błędnego defaultu.
Nadmiarowy fakt może przejść, gdy poprawny fakt także występuje. Ocena
na nowych zapytaniach i końcowa kwalifikacja MVP pozostają otwarte.
[Wyniki jednostkowe](../../dokumentacja%20pracy/2026-11-18_t029/replay.json) ·
[Pełna regresja](../../dokumentacja%20pracy/2026-11-18_t029/full.json)
