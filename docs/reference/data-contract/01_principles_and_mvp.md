# Zasady i MVP

[Powrot do indeksu](README.md)

## Cel kontraktu danych

Kontrakt danych definiuje, jakie dane system uznaje za poprawne, jakie relacje musza byc spelnione oraz jakie reguly powinny zostac pozniej zaimplementowane w walidatorach i testach.

Kontrakt ma trzy funkcje:

1. Uporzadkowac slowniki domenowe.
2. Opisac poprawny ksztalt rekordow w bazie i plikach zrodlowych.
3. Przygotowac podstawe pod pelny walidator bazy i testy automatyczne.

## Zakres MVP

Zakres pierwszej wersji, elementy poza MVP i warunki ukonczenia opisuje
[Zakres MVP](../../../specs/001-mvp-stabilization/spec.md). Uzgodniony kierunek to stabilizacja obecnych
funkcji bez dodawania nowych mozliwosci uzytkowych. Kryteria i progi zapisano
w [acceptance.md](../../../specs/001-mvp-stabilization/acceptance.md).
Specyfikacja jest nadrzednym opisem granic MVP.
Ten kontrakt rozwija wymagania dotyczace danych; nie utrzymuje osobnej listy
funkcji MVP.

## Podzial odpowiedzialnosci

### LLM

LLM odpowiada za:

- rozpoznanie intencji uzytkownika,
- decyzje o wywolaniu narzedzia `get_recommendations` i wypelnienie jego parametrow.

Odpowiedz koncowa jest tworzona lokalnie przez renderer na podstawie danych
backendu. Swobodny tekst modelu nie jest prezentowany jako wynik rekomendacji.

LLM nie moze:

- tworzyc nowych przepisow spoza bazy,
- dopisywac produktow SKU spoza bazy,
- zmieniac wartosci kcal lub makro,
- zmieniac listy skladnikow,
- obiecywac zgodnosci dietetycznej, jezeli nie wynika ona z bazy.

### Backend

Backend odpowiada za:

- deterministyczne filtrowanie przepisow,
- sprawdzanie zgodnosci dietetycznej,
- wybor SKU wedlug regul biznesowych,
- obliczanie wartosci odzywczych,
- przygotowanie ustrukturyzowanego wyniku dla lokalnego renderera.

### Baza danych

Baza danych odpowiada za:

- definicje skladnikow-konceptow,
- wartosci odzywcze skladnikow i SKU,
- polityki dietetyczne skladnikow,
- przepisy,
- klientow,
- katalogi SKU klientow,
- reguly wyboru SKU.
