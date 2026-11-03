# Przegląd ostrzeżeń, luk i decyzji przed stabilizacją MVP

> Raport z przeglądu, zachowany jako kontekst decyzji. Późniejsza dyspozycja
> autorki wstrzymuje analizę pięciu SKU. Proponowane poniżej czynności nie
> wznawiają zadania. Bieżące decyzje są w [spec.md](../../specs/001-mvp-stabilization/spec.md),
> a kolejność i stan w [tasks.md](../../specs/001-mvp-stabilization/tasks.md).

Data: 2026-10-22<br>
Status: DEC-01–DEC-03 zatwierdzone przez autorkę 2026-10-22;
DEC-04 pozostaje nierozstrzygnięta; weryfikację źródeł wstrzymano na prośbę autorki.

## 1. Podstawa i granice analizy

Przejrzano [kontrolę bazową](baseline_2026-10-22.md), implementację
walidatorów, rekomendacji i normalizacji, testy oraz kontrakty i pliki
curation. Wartości rekordów oraz ich użycie w przepisach odczytano offline
z zapisanej kopii PostgreSQL. Nie zmieniano danych ani kodu aplikacji.
Nie odwiedzano źródeł producentów i nie potwierdzano aktualności etykiet.

Szczegóły odczytu zapisano w
[warnings_audit.json](../../dokumentacja%20pracy/2026-10-22_baseline_02/warnings_audit.json).
To analiza uzupełniająca utworzona po kontroli bazowej. Nie zmienia jej
oryginalnych raportów i nie jest ujęta w pierwotnym spisie ich skrótów.
Metadane jednostek pochodzą z lokalnego CSV; liczby porównano z archiwum bazy.

## 2. Osiem ostrzeżeń o kcal

Walidator porównuje zapisane kcal z `4*B + 9*T + 4*W` i ostrzega, gdy
różnica przekracza `max(50 kcal, 35% zapisanych kcal)` na 100 g. Jest to
heurystyka spójności, nie dowód, że trzeba nadpisać dane. Sam komunikat
o błonniku lub poliolach nie potwierdza przyczyny dla konkretnego rekordu.

| ID i nazwa | Kcal w bazie / z 4/9/4 na 100 g | Liczba przepisów z konceptem | Wniosek |
| --- | --- | --- | --- |
| C012 — papryka słodka | 282 / 391,3 | 11 | Potrzebny przegląd źródła i definicji węglowodanów. |
| C333 — ksylitol | 240 / 400 | 0 | Możliwy wyjątek od uproszczonego wzoru; obecnie nie wpływa na przepisy. |
| C334 — erytrytol | 0 / 400 | 0 | Możliwy wyjątek od uproszczonego wzoru; obecnie nie wpływa na przepisy. |
| C338 — kakao gorzkie | 227 / 433,3 | 3 | Priorytet przeglądu w tej grupie; potrzebne spójne źródło kcal i makro. |
| C357 — papryka ostra mielona | 282 / 389 | 1 | Potrzebny przegląd źródła i definicji makro. |
| C367 — cynamon mielony | 247 / 350,8 | 4 | Potrzebny przegląd źródła i definicji makro. |
| C371 — kolendra mielona | 298 / 403 | 0 | Bez wpływu na obecne przepisy; zachować jako otwarty przegląd danych. |
| C373 — goździki | 274 / 464 | 0 | Bez wpływu na obecne przepisy; zachować jako otwarty przegląd danych. |

Dla kakao mechaniczna zamiana kcal na wynik wzoru zmieniałaby wartość
w ocenionych recepturach nawet o około 51,6 kcal na porcję. To ilustracja
skali różnicy między dwiema wartościami, nie oszacowanie rzeczywistego błędu
ani uzasadnienie takiej korekty. Mała ilość przyprawy nie zastępuje dowodu
poprawności jej danych.

Rekomendacja: nie zmieniać wzoru tolerancji ani nie przeliczać automatycznie
kcal. Dla używanych rekordów sprawdzić źródło, jednostkę i znaczenie
węglowodanów, następnie zapisać uzasadnioną akceptację albo korektę całego
zestawu danych. Cztery nieużywane koncepty mogą pozostać z udokumentowanym
ostrzeżeniem i zakresem braku wpływu, bez dodawania ich do receptur.

## 3. Dwanaście niezweryfikowanych statusów laktozy SKU

To jawne stany `NULL`, a nie potwierdzone niezgodności. Powody są już
opisane w [przeglądzie SKU](../../curation/lactose_sku_manual_review.md):
brak dowodu dla wariantu opakowania, niepełne źródło lub nierozstrzygnięta
deklaracja producenta. Opis ten pochodzi z wcześniejszego przeglądu.

Kod wymaga `is_lactose_free == 1`, gdy aktywne jest `lactose_free`.
SKU z `NULL` jest pomijane; zgodny koncept może pozostać generyczny lub
otrzymać kolejny zgodny SKU według istniejących reguł. Status nieznany
nie blokuje takiego produktu dla zapytań bez tego ograniczenia.

Rekomendacja: utrzymać tę politykę i zaakceptować nieznane statusy jako
udokumentowane ograniczenie pokrycia katalogu. Nie trzeba potwierdzać
wszystkich 20 SKU, aby ukończyć MVP. Warunkiem jest dowód filtrowania,
brak nieuzasadnionych deklaracji i opis mniejszej dostępności produktów.
Nie należy nadawać `1` ani `0` jedynie w celu usunięcia ostrzeżenia.

## 4. Dziewięć informacji o nieużywanych SKU

Są to produkty obecne w katalogu, ale niewskazane przez żadną regułę.
Kod `choose_sku` wybiera po regułach; sama obecność SKU nie wystarcza.

Rekomendacja: pozostawić jako informację o pokryciu. Nie dodawać nowych
reguł ani nie usuwać produktów wyłącznie po to, by wyczyścić raport.
Kompletne wykorzystanie portfolio nie jest kryterium obecnego MVP.

## 5. Luka niewidoczna w raporcie: podstawa obliczeń SKU

Model nie przechowuje `nutrition_basis`, a backend zawsze mnoży wartości
odżywcze przez `grams / 100`. Import kopiuje wartości z CSV bez konwersji.
W archiwum liczby poniższych SKU są identyczne jak w lokalnym CSV:

| SKU wskazywane przez reguły | Podstawa w lokalnym źródle |
| --- | --- |
| WINIARY_MAJONEZ_DEKORACYJNY_400ML | per 100 ml |
| WINIARY_MAJONEZ_WEGANSKI_300ML | per 100 ml |
| WINIARY_SOS_CZOSNKOWY_BUTELKA_300ML | per 100 ml |
| WINIARY_BULION_DROBIOWY_160G | po przygotowaniu w 100 ml |
| WINIARY_BULION_WARZYWNY_SLOIK_160G | po przygotowaniu w 100 ml |

Nie potwierdzono w tym przeglądzie, czy same metadane źródłowe i etykiety
są prawdziwe. Potwierdzono natomiast brak udokumentowanego przeliczenia
między wskazaną podstawą danych a gramaturą używaną w kodzie. Wartości dla
produktu po przygotowaniu wymagają również ustalenia, czego dotyczy ilość
składnika w recepturze. Ta luka blokuje pełne uzasadnienie ACC-03, mimo
poprawnej arytmetyki i przechodzących testów.

Rekomendacja: zachować obliczenia oparte na gramach i uporządkować dane
istniejących SKU do zweryfikowanej podstawy na 100 g właściwej postaci
składnika. Tam, gdzie brak dowodu, uzgodnić czasowe niedopuszczenie SKU
do wyboru i użycie zgodnego konceptu generycznego z poprawnym makro.
Wyłączenie SKU także wymaga jawnej zmiany reguł i oceny wpływu na istniejące
scenariusze. Nie zakładać automatycznie 1 ml = 1 g ani nie używać wartości
gotowego bulionu dla masy koncentratu.

Nie rekomenduję rozbudowy obsługi jednostek i przeliczników w runtime
na tym etapie. Korekta istniejących danych jest stabilizacją; nowy ogólny
mechanizm jednostek wymagałby osobnej oceny zakresu. Sam dopisek
„wartości orientacyjne” nie dowodzi poprawności ACC-03 i nie zamyka tej luki.

## 6. Pozostałe luki w wymaganiach i dowodach

| Obszar | Ustalenie | Potrzebne działanie |
| --- | --- | --- |
| Brak polityki dietetycznej, ST-03 | Snapshot nie zawiera używanego konceptu bez polityki. Kod jednak dopuszcza brak rekordu dla vegetarian/vegan i traktuje brak flag mięsa jako 0 przy pescetarian. | Uzgodnić zachowanie dla niekompletnych danych i dodać kontrolowane przypadki braku polityki. To luka odporności, nie potwierdzona niezgodna rekomendacja w obecnym snapshotcie. |
| Maskowanie wyjątków, ST-04 | Szeroki `except Exception` pomija przepis. Pusta lista może ukrywać awarię przygotowania danych. | Rozdzielić przewidywalne wykluczenie od niespójności danych i błędu programistycznego; opisać oczekiwany wynik przed poprawką. |
| Obliczenia, ACC-03 | Testy sprawdzają m.in. wybrane kcal i ranking; nie stanowią kompletnego niezależnego rachunku B/T/W, porcji i jednostek. | Mały ręcznie policzony zestaw obejmujący wszystkie cztery wartości, SKU i wariant generyczny oraz jawne tolerancje. |
| Precyzja prezentacji | Makro jest zaokrąglane do 0,1, gramatura do pełnych gramów. Dodatnia mała ilość może stać się zerem i zostać odrzucona przez renderer. | Opisać precyzję oraz przypadki małej gramatury przed uznaniem ścieżki za zweryfikowaną. Nie potwierdzono wystąpienia problemu w obecnym katalogu. |
| Routing, ACC-09–ACC-11 | Aktualna kontrola sprawdziła tylko dry-run; znany problem JSON-a poza tool callami pozostaje. | Kontrolowany eksperyment na zbiorze rozwojowym, bez parsowania zwykłego tekstu jako zastępczego wywołania. |
| Czytelność i pełny przepływ, ACC-12/14 | Brak zatwierdzonego zestawu i wypełnionego formularza oceny. | Przygotować scenariusze oraz kryteria tak/nie; oznaczyć użycie rzeczywistego modelu i kontrolowane awarie. |
| Odtwarzalność, ACC-13 | Archiwum i wersje zapisano, lecz nie odtworzono osobnej bazy ani nowego środowiska. | Instrukcja odtworzenia, aktualizacja README, później próba odtworzenia bez nadpisywania bieżącej bazy. |

## 7. Decyzje autorki projektu

DEC-01 została zatwierdzona: nieznane statusy laktozy pozostają; dodawanie
produktów i dopuszczanie kolejnych zweryfikowanych SKU jest poza MVP.
Obecne wykluczanie nieznanych SKU przy `lactose_free` pozostaje obowiązujące.
DEC-02 została zatwierdzona: program nie zakłada zgodności składnika
pozbawionego wymaganej polityki dietetycznej.
DEC-03 została zatwierdzona: w MVP błąd przygotowania przepisu przerywa
zapytanie; nie zwracamy częściowego sukcesu ani pozornego braku wyników.
Szczegóły walidacji, diagnostyki i komunikatów wymagają specyfikacji przed
implementacją. Nie oznacza to akceptacji niespójnego katalogu.
DEC-04 wymaga weryfikacji źródeł przed zmianą danych; wyłączenie SKU
nie zostało zatwierdzone.
Nie wymagają obniżenia zaakceptowanych progów jakości.

| ID | Decyzja | Rekomendowany wybór |
| --- | --- | --- |
| DEC-01 — zatwierdzona | Czy nieznane statusy laktozy mogą pozostać w katalogu? | Tak, z wykluczeniem tych SKU przy aktywnym `lactose_free`. Zwiększanie liczby produktów oraz dopuszczanie kolejnych SKU do polityki laktozy pozostaje poza MVP. |
| DEC-02 — zasada zatwierdzona | Co robić przy braku wymaganej polityki? | Nie zakładać zgodności składnika bez polityki. Szczegółową obsługę błędu integralności i walidację należy opisać przed implementacją. |
| DEC-03 — zatwierdzona | Co robić przy awarii przygotowania kandydata? | Przerwać zapytanie zamiast pomijać błędny przepis i zwracać częściowy sukces. Rozpoznane błędy danych mają kontrolowany komunikat i diagnostykę; błędów programistycznych nie maskować jako braku wyników. |
| DEC-04 | Jak zamknąć problem podstawy makro SKU? | Zweryfikować i poprawić dane do 100 g właściwej postaci; SKU bez takiego dowodu czasowo nie wybierać. Pozostawić zgodny wariant generyczny. Bez rozbudowy mechanizmu jednostek. |

Osiem ostrzeżeń kcal nie wymaga jeszcze arbitralnego wyboru „akceptuj albo
przelicz”. Najpierw należy dostarczyć źródła i rozstrzygnąć ich znaczenie.
Po analizie autorka może zaakceptować uzasadnione wyjątki. Dziewięć informacji
o SKU nie wymaga decyzji produktowej w ramach obecnego zakresu.

## 8. Proponowana kolejność prac

1. Utrzymać zatwierdzone DEC-01–DEC-03; przed rozstrzygnięciem DEC-04
   sprawdzić źródła pięciu SKU, bez zmiany progów akceptacji.
2. Opracować jedną specyfikację integralności danych i obsługi błędów
   obejmującą ACC-01/03/07/08, przypadki braku polityki oraz podstawę makro.
3. Sprawdzić źródła czterech używanych konceptów z ostrzeżeniami kcal
   i pięciu wskazanych SKU. Zapisać źródła, korekty lub uzasadnione ograniczenia.
4. Dopiero po specyfikacji wdrożyć małe poprawki wraz z testami ujawnionych luk;
   zachować snapshot i raport sprzed zmian oraz wykonać nową kontrolę danych.
5. Przygotować specyfikację i porównanie wariantów routingu na regresji;
   zamrozić finalny wariant przed pomiarem na nowym holdoucie.
6. Uzgodnić zawartość holdoutu i zestawu przeglądowego. Autorka sprawdza
   etykiety; zamrożonego holdoutu nie używa się do wyboru promptu.
7. Uzupełnić instrukcje odtworzenia i wykonać kampanię akceptacyjną oraz
   ocenę pełnego przepływu dla jednej wersji kandydującej.

Najbliższym rezultatem powinna być zatwierdzona decyzja o integralności
danych i błędach, a następnie krótka specyfikacja. Samo zwiększanie liczby
testów albo strojenie promptu nie rozwiąże problemu podstawy danych.
