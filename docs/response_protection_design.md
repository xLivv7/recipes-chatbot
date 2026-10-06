# Projekt ochrony odpowiedzi koncowej

Status: projekt do wdrozenia, 2026-10-01. Nie zmienia jeszcze chat_with_bot.

Aktualizacja 2026-10-06: etap 1 wdrozony w core/response_renderer.py.
render_recommendations przyjmuje tylko payload backendu i nazwe marki,
bez tekstu modelu/uzytkownika, bez wyboru stylu i bez API. Nie jest jeszcze
podlaczony do main.py. Niepoprawne dane powoduja ResponsePayloadError;
komunikat bledu dla uzytkownika zostanie dodany przy integracji.
Renderer sprawdza finitywne nieujemne liczby, dodatnie porcje/gramature,
strukture list oraz zgodnosc used_skus z przypisaniami w ingredients.
Zachowuje kolejnosc, liczby i nazwy SKU bez zmian; nie usuwa dopiskow.
Nazwy i kroki escapuje dla Markdown/HTML oraz odrzuca URL zamiast
po cichu modyfikowac dane. Nie analizuje semantycznej zgodnosci instrukcji.
Obecny normalize_ingredient usuwa client_sku_id: przy etapie 2 trzeba
zachowac te metadane i dodac testy regresji, nie omijac kontroli renderera.

## Problem i cel

final_013 w 3/3 prob dopisal bulion Winiary nieobecny w used_skus.
Wzmocnienie promptu nie usunelo problemu. Kontrola leksykalna w eval
wykrywa wybrane naruszenia, ale nie jest kompletna ochrona runtime.
Celem jest uniemozliwienie modelowi dopisywania faktow i produktow
do finalnej prezentacji, bez zmiany rekomendacji, rankingu lub SKU.

## Decyzja architektoniczna

Backend jest jedynym zrodlem faktow. Deterministyczny renderer tworzy
Markdown z zatwierdzonego payloadu: tytuly, czas, porcje, makro, skladniki,
instrukcje i produkty. Swobodny tekst modelu nie trafia do odpowiedzi.
Nie polegamy na regexach jako kompletnej ochronie dowolnej prozy.

LLM zachowuje ekstrakcje intencji i ograniczona redakcje przez wybor
wariantu z zamknietego slownika. Opcjonalny drugi call moze zwrocic tylko:

```json
{"intro_key": "neutral", "layout_key": "compact"}
```

Dozwolone intro_key: neutral, friendly. Dozwolone layout_key: compact,
detailed. Slownik tekstow jest lokalny, zatwierdzony i nie zawiera twierdzen
dietetycznych/medycznych ani nazw produktow. Brak dowolnego pola text.
Model nie wybiera nowych przepisow, kolejnosci, SKU, liczb ani instrukcji.
Nowe klucze wymagaja jawnej zmiany kodu i testow. Na poczatek mozna pominac
drugi call i uzyc neutral/compact; to najbardziej przewidywalny wariant MVP.
Koszt decyzji: mniej swobodny styl; korzysc: kontrola zawartosci odpowiedzi.

## Przeplyw i granice zaufania

1. Istniejaca ekstrakcja intencji -> walidacja kontraktu backendu.
2. Backend -> normalize_recommendations_output -> validate_recommendations_output.
3. Jesli payload jest niepoprawny: komunikat bledu danych bez przepisow,
   bez pozorowania braku wynikow i bez wywolania modelu po porady.
4. Jesli recommendations jest puste: staly komunikat braku wynikow.
   Bez przepisow, SKU, zamiennikow ani samoczynnego luzowania restrictions.
5. Opcjonalny wybor redakcyjny LLM: parsowanie JSON, dokladny zestaw kluczy,
   sprawdzenie typow i wartosci enum. Nadmiarowe pola tez sa bledem.
6. Renderer przyjmuje tylko lokalny wariant i zwalidowany payload backendu.
7. Blad API, odmowa, brak/parsing blad lub niepoprawny wybor redakcyjny:
   neutral/compact z TEGO SAMEGO payloadu, bez ponownego wyszukiwania.

Przy wyborze renderera nie wystarczy deklaracja zgodnosci schematu API:
lokalna walidacja pozostaje obowiazkowa. Nie interpolowac odpowiedzi modelu
do szablonu, naglowka, porady ani komunikatu bledu. Nie pokazywac surowych
wyjatkow, kluczy API lub tresci technicznych w odpowiedzi dla uzytkownika.

## Kontrakt renderera

- Zachowuje wszystkie przepisy, kolejnosc i identyfikatory backendu.
- Fakty bierze tylko z odpowiednich pol konkretnego przepisu, nie z promptu.
- Kalorie i B/T/W wyraznie na porcje; ilosci skladnikow laczne dla podanej
  liczby porcji. Nie miesza grams_total z grams_per_serving.
- Nie przelicza makro ani nie dodaje zaokraglen poza kontraktem normalizacji.
- Marka i porada tylko dla used_skus tego przepisu, zgodnych z przypisaniami
  client_sku_id w ingredients. Przy pustym used_skus brak promowania marki.
- Niespojnosc SKU/skladnikow traktuje jako blad payloadu, nie naprawia zgadywaniem.
- Puste ingredients/steps_pl: calkowicie pomija odpowiednia sekcje.
- Podstawowe teksty sa po polsku; wartosci danych escapuje dla Markdown,
  bez wykonywania HTML i bez traktowania danych katalogu jako instrukcji.
- Nie deklaruje certyfikacji, zerowej laktozy ani bezpieczenstwa dla alergikow.
  Opcjonalna etykieta ograniczenia mowi o zgodnosci z polityka katalogu.

## Poza ochrona renderera

Renderer nie naprawi nieprawdziwych danych w bazie, jak wykazal R120.
steps_pl nadal wymagaja audytu skladnikow, jezyka i instrukcji. Escaping
nie jest kontrola semantyczna ani usuwaniem URL; katalog moze zawierac
niepozwolone linki i wymagac dodatkowej walidacji przed prezentacja.
Ekstrakcja intencji nadal ma bledy protein_preference/nutrition_goal.
Nie gwarantujemy medycznego bezpieczenstwa ani zgodnosci dowolnego SKU.

Sciezka bez tool calla nie moze ominac renderera i zwrocic swobodnej porady
z przepisami. Dla nieobslugiwanych prosb (alergia, bez nabialu) docelowo
potrzebny zamkniety typ odpowiedzi clarify_unsupported z lokalnym tekstem,
a nie akceptacja dowolnego message.content. To osobny kontrakt rozmowy;
wdrozenie samego renderera nalezy opisac jako ochrone sciezki po backendzie,
nie wszystkich mozliwych odpowiedzi chatbota.

## Plan wdrozenia i testy

1. Renderer bez API: testy snapshot i semantyczne dla wielu przepisow,
   roznych SKU, pustych sekcji, pustych wynikow, liczb i escapingu Markdown.
2. Integracja main: walidacja payloadu, renderer i kontrolowany fallback.
   Mock API: niepoprawny JSON, dodatkowy produkt/pole, odmowa, timeout.
3. Opcjonalny zamkniety wybor stylu; kazdy wariant ma te same fakty.
4. Osobno zamkniecie sciezki bez tool calla; do tego czasu jawna luka zakresu.
5. Nowy holdout atakow: dopisz SKU, zmien kcal, zamien skladnik, pomin wynik,
   wymysl wynik, zapewnij bezpieczenstwo dla alergikow, instrukcja w danych.
6. Ewaluacja: oddzielic poprawnosc intencji, decyzji redakcyjnej i renderera.
   Stary runner swobodnych odpowiedzi pozostawic jako historyczny baseline.

Akceptacja: zadne nowe SKU/liczby/przepisy z odpowiedzi modelu nie trafiaja
do wyrenderowanej odpowiedzi; final_013 i niezalezny holdout nie dopisuja
bulionu; awaria drugiego calla nie zmienia faktow; testy backendu nadal OK.
Pomiar estetyki/czytelnosci pozostaje osobny od deterministycznej zgodnosci.
# Aktualizacja 2026-10-06: integracja renderera

`main.chat_with_bot` po tool callu renderuje wynik backendu lokalnie. Drugie
wywolanie LLM zostalo usuniete: wyniki bazy nie sa wysylane do modelu w tej sciezce.
Normalizacja zachowuje `client_sku_id` i `client_sku_name_pl` bez dopisywania ich
do skladnikow generycznych. `ResponsePayloadError` powoduje staly komunikat
o niespojnych danych i zapis diagnostyczny w loggerze, bez czesciowej odpowiedzi.
Nieznane narzedzie nie uruchamia backendu. Sciezka bez tool calla pozostaje
odpowiedzia LLM i nie jest objeta ta ochrona; walidacja argumentow, bledy API
oraz semantyczny audyt instrukcji katalogu pozostaja osobnymi zadaniami.
Dotychczasowa ewaluacja odpowiedzi LLM jest eksperymentem historycznym,
nie ewaluacja aktualnej produkcyjnej prezentacji wynikow.
