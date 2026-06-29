# Zasady i MVP

[Powrot do indeksu](../data_contract.md)

## Cel kontraktu danych

Kontrakt danych definiuje, jakie dane system uznaje za poprawne, jakie relacje musza byc spelnione oraz jakie reguly powinny zostac pozniej zaimplementowane w walidatorach i testach.

Kontrakt ma trzy funkcje:

1. Uporzadkowac slowniki domenowe.
2. Opisac poprawny ksztalt rekordow w bazie i plikach zrodlowych.
3. Przygotowac podstawe pod pelny walidator bazy i testy automatyczne.

## Zakres MVP

Minimalny zakres systemu, ktory powinien zostac doprowadzony do stabilnosci przed budowa frontendu:

- rekomendacje przepisow z bazy PostgreSQL,
- filtrowanie po preferencji dietetycznej, celu zywieniowym, kategorii posilku i czasie,
- brandyfikacja skladnikow przez SKU klienta,
- przeliczanie kcal i makro z danych w bazie,
- brak halucynowania produktow i wartosci odzywczych przez LLM,
- walidator danych obejmujacy wszystkie tabele,
- testy najwazniejszej logiki domenowej.

## Poza MVP

Poza minimalnym zakresem zostaja:

- rozbudowany frontend/widget,
- panel administracyjny,
- billing i pelna obsluga kont SaaS,
- duzy katalog wielu marek,
- zaawansowane wyszukiwanie semantyczne,
- analytics dashboard.

## Podzial odpowiedzialnosci

### LLM

LLM odpowiada za:

- rozpoznanie intencji uzytkownika,
- wypelnienie parametrow narzedzia `get_recommendations`,
- redakcje finalnej odpowiedzi w przyjaznym jezyku.

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
- przygotowanie ustrukturyzowanego JSON dla LLM.

### Baza danych

Baza danych odpowiada za:

- definicje skladnikow-konceptow,
- wartosci odzywcze skladnikow i SKU,
- polityki dietetyczne skladnikow,
- przepisy,
- klientow,
- katalogi SKU klientow,
- reguly wyboru SKU.
