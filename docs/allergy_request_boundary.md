# Granica obslugi zapytan dotyczacych alergii

Status: wdrozona konserwatywna ochrona leksykalna, 2026-10-06.

## Kontrakt
Katalog nie zapewnia doboru przepisow dla alergii ani kontroli kontaktu
z alergenami. Zadnego wymagania alergicznego nie mozna zastapic gluten_free,
lactose_free, vegetarian lub vegan.

`chat_with_bot` sprawdza wzmianke o alergii przed API. Funkcja
`mentions_unsupported_allergy` wykrywa rdzenie alerg/allerg, uczul,
anafilak/anaphyla w slowach, bez rozrozniania wielkosci liter. Dla trafienia
zwracany jest staly UNSUPPORTED_ALLERGY_RESPONSE; nie wywoluje sie modelu
ani backendu, nie wyswietla tresci uzytkownika, SKU lub propozycji.
Dotyczy to takze kombinacji z obslugiwanymi filtrami i instrukcji ignorowania
alergii. Odpowiedz mowi o wzmiance, nie przypisuje uzytkownikowi diagnozy.

## Celowa ostroznosc
Blokowane sa takze negacje ("nie mam alergii"), pytania ogolne i cytaty.
Regula nie interpretuje ich semantycznie. Jest to koszt uzytecznosci, wybrany
zamiast ryzyka usuniecia wymagania na podstawie niepewnej negacji.
Zwykle zapytania o nietolerancje laktozy/glutenu lub bez laktozy/glutenu
nie sa blokowane przez te regule, o ile nie zawieraja wzmianki alergicznej.

## Granice
To nie jest pelne NLP ani gwarancja wykrycia wszystkich alergii. Literowki,
obfuskacja, inne jezyki i opis objawow bez wykrywanych slow moga nie trafic
w regule. Same wykluczenia (np. "bez orzechow", "bez mleka") nie sa tym
detektorem alergii objete: dotychczasowe instrukcje no_tool w modelu pozostaja
ich jedyna warstwa interpretacji. Nie twierdzimy, ze ten etap zabezpieczyl
wszystkie nieobslugiwane wykluczenia. Wywolania backendu bez chat_with_bot
rowniez nie korzystaja z preflight.

## Ewaluacja
Test regresyjny obejmuje oryginalny routing_004 i brak API/backendu.
`run_llm_eval.py` nadal mierzy surowa decyzje modelu, celowo bez tej ochrony.
Nie nalezy poprawiac historycznego 63/70 po dodaniu preflight ani deklarowac
naprawy rozumienia modelu. Testy aplikacyjnej ochrony i metryki modelu sa osobne.
Nastepny etap powinien objac kontrakt nieobslugiwanych wykluczen oraz osobna
ewaluacje calego routingu aplikacji na holdoucie, z negacjami i parafrazami.
