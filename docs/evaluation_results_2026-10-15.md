# Powtorzenia i holdout v1: wyniki 2026-10-15

Protokol zamrozono przed wywolaniami: commit 42067e5,
docs/holdout_v1_protocol.md. Prompt/ochrona/expected niezmienione w kampanii.
Model zwrocony przez API: gpt-4o-mini-2024-07-18, temperatura 0.1.
Routing-only ze stubem narzedzia; zadnych wynikow bazy nie wysylano do API.

## Wszystkie pomiary
| Zestaw/tryb | Proby | Sukcesy lacznie | Stabilne przypadki | API errors |
| --- | --- | --- | --- | --- |
| Regresja raw | 65/76, 20/76, 64/76 | 149/228 (65.4%) | 19/76 | 49 |
| Regresja application | 68/76, 68/76, 63/76 | 199/228 (87.3%) | 63/76 | 5 |
| Holdout raw, pierwsza kampania | 0/24, 0/24, 0/24 | 0/72 | 0/24 | 72 |
| Holdout application, pierwsza kampania | 5/24, 11/24, 20/24 | 36/72 (50.0%) | 5/24 | 29 |
| Holdout raw, pelne ponowienie | 17/24, 17/24, 17/24 | 51/72 (70.8%) | 17/24 | 0 |
| Holdout application, pelne ponowienie | 20/24, 20/24, 19/24 | 59/72 (81.9%) | 19/24 | 0 |

Po calkowitej awarii pierwszego holdoutu raw ponowiono OBIE cale grupy
holdoutu (3 x 24 kazda), bez zmian lub selekcji cases. Zachowano wszystkie
szesc raportow w ignorowanym folderze dokumentacja pracy, z prefiksem
2026-10-15 i sufiksem _retry_full dla ponowienia. Laczone liczby wykonania:
744 oceny, 678 wywolan klienta SDK, 155 APIConnectionError. Nie uwzgledniaja
wewnetrznych retry ani kosztu rozliczeniowego. Pierwszy raw holdout nie
mierzy jakosci modelu; byl w calosci niedostepny.
Wyniki stabilnosci regresji sa obciazone awariami. Pomocniczo bez API errors:
raw 149/179 (83.2%), application 199/223 (89.2%). Nie zastepuje to tabeli.

## Wnioski z holdoutu bez awarii
- Regula jawnego limitu nie uogolnila sie: holdout_006 wybiera 30 zamiast 40
  minut, w obu trybach 3/3.
- holdout_010 wybiera vegetarian zamiast pescetarian przy dopuszczeniu ryb,
  w obu trybach 3/3.
- holdout_014 pomija wymagane protein_preference mimo poprawnego low_kcal
  i czasu, w obu trybach 3/3.
- Raw zle obsluguje uczulenie na jajka (lactose_free), alergie na orzechy
  (gluten_free), bez mleka krowiego (lactose_free) i wykluczenie soi (brak
  ograniczenia), po 3/3. Aplikacja blokuje te przypadki przed modelem.
- Ochrona aplikacji nadmiarowo blokuje "bez pospiechu" (holdout_013), 3/3.
- Jedna zmienna odmowa dotyczy holdout_004: prosby o bialko bez wymogu miesa.

Application ma 4 stale bledne cases, 1 zmienny i 19 poprawnych 3/3.
Raw ma 7 stale blednych cases i 17 poprawnych 3/3. Roznica nie jest czystym
efektem ochrony: tryby wykonywaly niezalezne zadania, a mianowniki metryk
warunkowych roznia sie. Nie przypisujemy blokad modelowi.
intent_007/059 (dwie propozycje) i intent_008 przeszly 3/3 w obu trybach.
intent_015/025 nadal nie przechodza z powodu brakujacego protein_preference
(oraz utraconych prob raw przez API). Nie zaliczamy poprawnych fragmentow
argumentow jako sukcesow calego kontraktu.

## Integralnosc i kolejne kroki
Sprawdzono hashe zrodel i datasetow wszystkich 6 raportow: bez rozbieznosci.
206 testow implementacji OK; baza 0 ERROR, 20 WARNING, 9 INFO.
Holdout v1 zawiera 24 nowe wypowiedzi nieuzywane do strojenia promptu;
ten sam asystent znal kontrakt i klasy bledow, wiec nie jest to niezalezna
anotacja zewnetrzna. Po tej analizie v1 jest ujawniony: nie mozna go uzyc
do strojenia i nadal nazywac niezaleznym holdoutem. Potrzebny v2.
Nie zmieniano expected pod odpowiedzi. Nie twierdzimy, ze system zapewnia
bezpieczenstwo medyczne lub pelna stabilnosc na podstawie tego pomiaru.
Kolejne priorytety: kompletnosc argumentow, jawne limity/dopuszczenie ryb,
false positives ochrony, a po korektach nowy holdout i stabilny pomiar API.
