# T020 — wiele celów żywieniowych

**Projekt po MVP, 2026-11-18.** W obecnej wersji obowiązuje jedno pole
`nutrition_goal`. Poniższy kontrakt określa zachowanie przyszłej wersji.
Punktem odniesienia są Z-04, DEC-11, reguły diety z T017 i komunikaty T019.
[Specyfikacja MVP](spec.md) · [Plan](plan.md) · [Kryteria MVP](acceptance.md)

## Od prośby do rekomendacji

1. **Zakwalifikuj przepis.** Każdy wynik musi spełniać wszystkie aktywne
   wymagania. Zachowaj dotychczasowe znaczenie kategorii, czasu, diety,
   wymaganego źródła białka i wykluczeń. „Bez mięsa” podlega regułom
   T017. „Bez laktozy” wymaga potwierdzonej zgodności. Keto dodaje
   projektowy warunek **do 15 g węglowodanów włącznie na porcję**.
2. **Uszereguj zakwalifikowane przepisy.** „Niskokaloryczne”, „fit” i „jak
   najmniej kalorii” preferują niższe kcal na porcję. „Wysokobiałkowe”
   i „jak najwięcej białka” preferują więcej gramów białka na porcję.
   Żadna z tych preferencji nie ustanawia progu dopuszczenia. Wysokie białko
   nie wyznacza źródła białka. Wynik może być najlżejszy spośród dostępnych
   nawet wtedy, gdy wszystkie kwalifikujące się dania mają dużo kcal.
3. **Zastosuj limit wyników.** Przedstaw przepisy z finalnymi wartościami
   na porcję. Przy braku zgodnych dań zwróć pusty wynik wykonanego wyszukania.

„Do 500 kcal”, „co najmniej 30 g białka” i „jak najwięcej kalorii” mają
inne znaczenie niż trzy istniejące cele. Te prośby pozostają poza projektem
T020. Cała prośba z takim aktywnym warunkiem podlega T019. To samo dotyczy
nierozstrzygniętej alternatywy „keto albo wysokobiałkowe”.

## Dane zapytania

Proponowany wariant narzędzia ma własną wersję schematu i parsera.
W argumentach wersji 2 obowiązkowy obiekt `nutrition` zastępuje pole
`nutrition_goal`. Pozostałe pola zachowują obecne typy i znaczenie.
Przykład fragmentu dla „keto, jak najmniej kalorii i dużo białka, przede
wszystkim białko”:

```json
{
  "nutrition": {
    "required": ["keto"],
    "preferences": ["low_kcal", "high_protein"],
    "primary": "high_protein"
  }
}
```

| Pole | Dozwolone wartości i walidacja |
| --- | --- |
| `required` | Tablica zawierająca zero lub jeden element `keto`. Istniejące ograniczenia, np. `lactose_free`, pozostają w dotychczasowym polu `restrictions`. |
| `preferences` | Zbiór od zera do dwóch różnych wartości spośród `low_kcal`, `high_protein`, przesyłany jako tablica. Do porównania i zapisu stosować kolejność kanoniczną pokazaną w przykładzie. |
| `primary` | `null` lub jedna z dwóch obecnych preferencji. Wartość różna od `null` wymaga obu preferencji i wskazania pierwszeństwa przez użytkownika. Przy jednej preferencji jej priorytet jest oczywisty i pole wynosi `null`. |

Wszystkie trzy klucze są obowiązkowe. Puste tablice i `primary: null`
odpowiadają dawnemu `standard`. Powtórzenie prośby („keto i ketogeniczne”)
daje jeden warunek. Powielony element na granicy gotowych argumentów,
powtórzony klucz JSON, oba formaty naraz, obcy klucz, enum, brak pola albo
błędny typ powodują MSG-06 przed wywołaniem backendu. Kolejność wymienienia
w tekście lub w tablicy nie nadaje pierwszeństwa. Jawne cofnięcie („nie
musi być keto”) wyłącza ten warunek; nierozstrzygnięta sprzeczność
wymagania i jego cofnięcia kończy się zgodnie z T019.

## Wybór wyników

| Zestaw aktywnych celów | Reguła po uwzględnieniu pozostałych wymagań |
| --- | --- |
| Brak celu | Dotychczasowy `standard`. |
| Tylko `low_kcal`, tylko `high_protein` lub tylko `keto` | Pełna zgodność z odpowiednim skalarem wersji 1, łącznie z doborem SKU, rozstrzyganiem remisów i doborem różnych typów dań. Samo keto zachowuje filtr oraz dotychczasowy ranking po węglowodanach, tłuszczu i liczbie SKU. |
| `keto` i jedna preferencja | Filtr keto, następnie odpowiednio kcal rosnąco lub białko malejąco. Różnica w węglowodanach między dwoma zgodnymi daniami nie wyprzedza jawnej preferencji. |
| Obie preferencje, także w połączeniu z keto | Po filtracji zastosować regułę dla dwóch preferencji podaną poniżej. |

**Dwa cele rankingowe z jawnym priorytetem.** Porównuj najpierw wartość
celu głównego. Dopiero przy jej równości porównuj drugi cel. „Przede
wszystkim białko” i „przede wszystkim mało kalorii” mogą dać różne wyniki.

**Dwa cele rankingowe bez priorytetu.** Proponowana reguła to warstwy
Pareto. Danie A wyprzedza B przez dominację, gdy ma co najwyżej tyle samo
kcal i co najmniej tyle samo białka, a w przynajmniej jednym wymiarze
jest lepsze. Pierwszą warstwę tworzą dania niezdominowane. Po jej zdjęciu
tę samą regułę stosuje się do pozostałych. Dzięki temu ani kolejność
słów, ani arbitralny przelicznik gramów białka na kcal nie rozstrzyga,
czy użytkownik woli danie lżejsze, czy bardziej białkowe.

Dla nowych kombinacji w obrębie tej samej warstwy lub przy remisie
wszystkich jawnych kluczy decyduje rosnący `recipe_id` porównywany jako
tekst. `top_n` wybiera pierwsze N z tej kolejności. Przy małym N może więc
wejść tylko jeden z równorzędnych kompromisów. Obecna selekcja różnych
`dish_type` pozostaje w ścieżce zerowego i pojedynczego celu. W nowych
kombinacjach różnorodność nie może awansować niższej warstwy ani przepisu
gorszego według jawnego priorytetu.

## Wpływ na aplikację

| Miejsce | Praca potrzebna po MVP |
| --- | --- |
| Interpretacja i walidacja | Wersjonować opis narzędzia, prompt i parser. Przekazywać cały zestaw oraz tylko jawny priorytet. W ścieżce IR-1 wiele różnych aktywnych celów obecnie daje `no_search`, a IR-1 nie przenosi relacji pierwszeństwa. Przyszły wariant IR wymaga wersjonowanego sposobu zapisania priorytetu wraz ze źródłem. Kompilator i kontrola kompletności muszą odróżniać koniunkcję, alternatywę i cofnięcie. |
| Dobór składników i SKU | Zachować sprawdzanie polityk konceptów i ograniczeń SKU. Regułę SKU typu `nutrition_goal` dla nowej kombinacji uznać za pasującą, jeśli jej wartość jest w zbiorze aktywnych celów. Wybierać pierwszą zgodną regułę w katalogowym `rule_order`, także przy kilku pasujących celach. Priorytet użytkownika porządkuje finalne przepisy. Projekt ocenia wariant produktu wybrany przez istniejące reguły; enumeracja wszystkich zamienników jest poza zakresem. |
| Obliczenia i filtr | Po wyborze SKU lub dopuszczonego składnika generycznego policzyć makro z rzeczywistych gramatur i liczby porcji. Porównywać limit keto i klucze rankingu na pełnej precyzji. Brak polityki lub błąd danych wymagany do przygotowania kandydata uruchamia dotychczasową obsługę błędu. Nieznany status laktozy nie potwierdza zgodności. |
| Normalizacja i prezentacja | W odpowiedzi v2 zachować w `query.nutrition` oba zbiory i priorytet. Obecna normalizacja oczekuje tekstowego `query.nutrition_goal` i wymaga osobnej ścieżki. Zaokrąglać dopiero do prezentacji. Renderer zachowuje kolejność, składniki i wartości z payloadu. Opis preferencji może mówić o kolejności wśród dostępnych dań. |
| Ocena | W nowym zestawie zapisać wersję, oczekiwaną decyzję, oba zbiory, priorytet, parametry niezwiązane z celami i oczekiwaną kolejność ID dla katalogu kontrolnego. Porównywać zbiory niezależnie od kolejności, priorytet dokładnie. Osobno punktować interpretację, kwalifikację przepisu, ranking i komunikat. Błąd lub odmowa nie otrzymują punktów za pola niewykonanego wyszukania. |

[Narzędzie](../../core/llm_tools.py) · [Parser](../../core/tool_call_validation.py) ·
[Kompilator IR-1](../../core/interpretation_compiler.py) · [Dobór i ranking](../../core/recommendations.py) ·
[Normalizacja](../../core/recommendation_normalization.py) · [Renderer](../../core/response_renderer.py)

## Przykłady akceptacyjne dla przyszłej implementacji

Kontrolny katalog poniżej podaje finalne wartości **na porcję po doborze
SKU**. Wszystkie cztery dania są obiadami. A i B mają ten sam typ dania,
C i D inne. Identyfikatory określają również porządek alfabetyczny.

| ID | kcal | Białko (g) | Węglowodany (g) |
| --- | ---: | ---: | ---: |
| A | 300 | 20 | 15,00 |
| B | 400 | 35 | 12,00 |
| C | 450 | 15 | 10,00 |
| D | 280 | 40 | 15,01 |

| ID | Wejście lub kontrast | Oczekiwany wynik |
| --- | --- | --- |
| G01 | Brak celu oraz każdy z trzech pojedynczych celów osobno | Identyczne ID, kolejność, SKU i makro jak dla odpowiedniego skalara v1 przy tym samym katalogu. |
| G02 | „Niskokaloryczny obiad keto”, również z odwróconą kolejnością słów | A, B, C dla N=3. A na granicy przechodzi, D odpada przed zaokrągleniem. |
| G03 | „Keto, jak najwięcej białka” | B, A, C. |
| G04 | „Mało kalorii i dużo białka”, obie kolejności słów | D w pierwszej warstwie, A i B w drugiej, C w trzeciej. D, A, B dla N=3. |
| G05 | Wszystkie trzy cele, bez priorytetu | Warstwy {A,B}, {C}. Dla N=2 wynik A, B mimo jednakowego typu dania. |
| G06 | Wszystkie trzy, „przede wszystkim białko” lub „przede wszystkim mało kalorii” | Odpowiednio B, A, C lub A, B, C. Przy równej wartości głównego celu rozstrzyga drugi, przy pełnym remisie ID. |
| G07 | „Keto i ketogeniczne” / „nie musi być keto, chcę jak najwięcej białka” | Odpowiednio pojedyncze keto / pojedynczy high_protein. |
| G08 | „Bez laktozy i dużo białka” / „bez mięsa, jak najmniej kcal” | Zachować dotychczasowy pojedynczy cel wraz z ograniczeniem lub dietą. Produkt o nieznanej zgodności laktozowej nie trafia do wyniku wymagającego tej zgodności. |
| G09 | Reguły SKU dla keto i low_kcal prowadzą do dwóch zgodnych produktów | Pierwsza zgodna reguła w `rule_order` wybiera SKU. Jeśli zmiana produktu podnosi węglowodany z 14 do 16 g na porcję, odrzucić finalny przepis. |
| G10 | Poprawna prośba o keto, każdy finalny kandydat powyżej 15 g | Jedno wyszukiwanie, pusta lista, MSG-04. Nie luzować filtra. |
| G11 | Nieobsługiwany limit kcal, alternatywa „keto albo fit” lub sprzeczne wymagania | Zwykła decyzja o braku wyszukania, MSG-01 i zero wywołań backendu. Reguły preflight dla alergii i wykluczeń zachowują pierwszeństwo. |
| G12 | Duplikat w argumentach, obcy cel lub `primary` spoza zbioru | MSG-06, backend=0. Przy błędnych danych przygotowania po wywołaniu backendu obowiązuje MSG-07; uszkodzony payload renderera daje MSG-08. |
| G13 | Istniejący klient v1 dostaje prośbę o dwa różne aktywne cele | Zachować granicę T019. Nie wysyłać pojedynczego celu po odrzuceniu drugiego. |

## Migracja i kryteria

Poniższy podział dotyczy osobnego etapu po MVP. Każda część ma własny
sprawdzalny rezultat.

1. **Kontrakt i interpretacja.** Dodać wersjonowane narzędzie i parser v2
   oraz mapowanie skalarów v1 do zbiorów. Rozdzielić wejścia wersji.
   Przygotować kontrasty G01, G07, G08, G11–G13 i próby z odwróconą
   kolejnością słów. Obecny klient zachowuje dotychczasowy schemat.
2. **Backend i dane wyjściowe.** Wprowadzić wybór SKU, kwalifikację, ranking
   i normalizację v2. W kontrolowanym katalogu sprawdzić kolejność G02–G06,
   granicę i zmianę SKU G09, brak wyniku G10 oraz zgodność v1 w G01.
3. **Integracja i kwalifikacja.** Połączyć jedną wersję kandydującą z
   rendererem. Rozszerzyć przypadki ACC-01–07 o filtr, SKU, finalne makro,
   kolejność, puste wyniki i walidację v2. Dla ACC-09–11 przygotować osobne
   etykiety wersji i świeży holdout. Dla ACC-12–14 sprawdzić czytelność,
   odtworzenie i demonstrację. Przed ewentualnym przełączeniem domyślnej
   wersji potwierdzić pełną zgodność pojedynczych celów i ocenić nowy zakres.

Artefaktem T020 jest ten projekt. Kryteria, progi i etykiety pomiarów
obecnego MVP obowiązują w dotychczasowych wersjach. G01–G13 opisują
oczekiwania wobec przyszłej implementacji.
