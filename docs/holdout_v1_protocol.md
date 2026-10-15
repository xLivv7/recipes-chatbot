# Holdout v1 i plan pomiaru powtarzanego

Data planu: 2026-10-15. Plan spisany przed pierwszym wywolaniem modelu
na holdout_cases_v1.json. Nie zmieniac promptu, ochrony ani expected w kampanii.

## Zbiory i ograniczenia
Regresja: 76 dotychczasowych przypadkow routingu. Holdout v1: 24 nowe
parafrazy, 16 tool + 8 no_tool. Holdout uruchamiac przez --holdout: nie dodaje
sie wtedy cases, routing-cases ani guard-cases. Przypadki nie wystepuja
doslownie w zbiorach rozwojowych i nie byly uzywane do poprawiania promptu.
Oczekiwania wynikaja z obecnego kontraktu, zapisane sa przed pomiarem.
Zestaw opracowal ten sam asystent znajacy kontrakt i klasy bledow, nie
niezalezny anotator; to ograniczony test generalizacji, nie slepa walidacja
zewnetrzna. Po odczytaniu wynikow v1 staje sie ujawnionym testem: dalsze
strojenie na jego wynikach wymaga nowego v2 do oceny generalizacji.

## Plan zamrozony przed pomiarem
- gpt-4o-mini, temperatura 0.1, auto, parallel_tool_calls=false.
- 3 pelne powtorzenia w kazdej z czterech grup: regresja/raw,
  regresja/application, holdout/raw, holdout/application.
- Razem 600 ocen (3 * (76 + 76 + 24 + 24)); planowane 552 wywolania SDK
  (228 + 198 + 72 + 54). Nie obejmuje wewnetrznych retry.
- Backend pozostaje stubowany; do API trafiaja kontrolowane wypowiedzi,
  prompt i schemat, nie przepisy/SKU z bazy.
- Osobne raporty w ignorowanym folderze dokumentacja pracy. Stare raporty
  nie sa nadpisywane. Checkpoint po kazdym przypadku ma complete=false;
  dopiero ukonczony pomiar ma complete=true i completed_at_utc.
- Kazdy wynik ma attempt. Summary pokazuje wynik kazdego przebiegu,
  przypadki poprawne we wszystkich powtorzeniach i bledy stale/zmienne.
  Ta klasyfikacja dotyczy calego routingu, nie wylacznie zachowania modelu.
- API bledow nie poprawiac selektywnym ponawianiem pojedynczych nieudanych
  cases; odnotowac je oddzielnie. Niewykonczony pomiar nie jest pelnym wynikiem.
- Nie dostosowywac expected do odpowiedzi. Ujawniona rzeczywista wada
  etykiety wymaga osobnego audytu i wersji, zachowania starego raportu oraz
  jawnego przeliczenia, nie cichej podmiany.

## Interpretacja
Raportowac ogolny wynik oraz stabilne przypadki, a nie tylko najlepszy
przebieg. Rozdzielac decyzje, protokol, argumenty, semantyke i preflight.
Warunkowa dokladnosc pol ma inne mianowniki niz wynik calkowity.
Pomiar regresyjny po zmianach nie jest scisle porownywalny z historycznym
63/70: inne zbiory, konfiguracja i metryki. Porownywac wspolne cases z
zastrzezeniem niezaleznych probek. Nie wyciagac wnioskow medycznych.

Referencja: https://developers.openai.com/api/docs/guides/evaluation-best-practices
