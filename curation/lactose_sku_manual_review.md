# Weryfikacja SKU lactose_free

Data przegladu: 2026-10-01. 8 dopuszczonych, 0 potwierdzonych wykluczen,
12 niezweryfikowanych. Puste pole w CSV oznacza NULL, nie 0.
Zrodlem prawdy jest winiary_sku_lactose_policy.csv.

Dopuszczenie wynika z pelnego skladu producenta bez skladnikow mlecznych
i dopasowania wariantu. To wniosek polityki MVP, nie deklaracja producenta
o poziomie <0.01 g/100 g ani certyfikat laboratoryjny. Brak alergenu sam
w sobie nie wystarcza. Dla majonezow 300 ml sklep potwierdza opakowanie,
a producent jest zrodlem skladu. Nie kwalifikowano jedynie po nazwie vegan.

## Do recznego potwierdzenia

| SKU | Brakujacy dowod |
| --- | --- |
| WINIARY_MAJONEZ_DELIKATNY_300ML | Nie znaleziono pelnego skladu producenta dla wariantu 300 ml. |
| WINIARY_MAJONEZ_OMEGA_36_300ML | Nie znaleziono pelnego skladu producenta dla wariantu 300 ml. |
| WINIARY_KETCHUP_PIKANTNY_560G | Strona producenta opisuje 450 g zamiast katalogowych 560 g; brak dowodu tej samej receptury. |
| WINIARY_KETCHUP_BEZ_CUKRU_410G | Strona producenta opisuje 450 g zamiast katalogowych 410 g; brak dowodu tej samej receptury. |
| WINIARY_SOS_CZOSNKOWY_SLOIK_250ML | Nie potwierdzono pelnego skladu producenta dla sloika 250 ml; aktualna strona dotyczy butelki 200 ml. |
| WINIARY_SOS_CZOSNKOWY_BUTELKA_300ML | Strona dotyczy 200 ml zamiast 300 ml i deklaruje mozliwa obecnosc mleka; nie rozstrzyga starego wariantu. |
| WINIARY_SOS_AMERYKANSKI_BBQ_348G | Aktualna strona dotyczy 200 ml i innych wartosci odzywczych zamiast 348 g; nie przenosic receptury. |
| WINIARY_SOS_SPAGHETTI_500G | Nie znaleziono aktualnego pelnego skladu producenta sosu w sloiku 500 g; mieszanki w proszku nie sa tym SKU. |
| WINIARY_SOS_BOLONSKI_500G | Nie znaleziono aktualnego pelnego skladu producenta sosu w sloiku 500 g; Italia w proszku nie jest tym SKU. |
| WINIARY_BULION_DROBIOWY_160G | Producent deklaruje mozliwa obecnosc mleka; brak wyjasnienia lub deklaracji bez laktozy. |
| WINIARY_BULION_WARZYWNY_SLOIK_160G | Producent deklaruje mozliwa obecnosc mleka; brak wyjasnienia lub deklaracji bez laktozy. |
| WINIARY_BULION_GRZYBOWY_6KOSTEK_60G | Producent deklaruje mozliwa obecnosc mleka; dodatkowo brak potwierdzenia zgodnosci wariantu i makro 60 g. |

Potrzebna pelna etykieta lub specyfikacja producenta konkretnego wariantu.
Nie przenosic receptur pomiedzy opakowaniami bez dowodu ich zgodnosci.
may_contain milk nie dowodzi laktozy i nie jest podstawa do 0, lecz wedlug
kontraktu MVP blokuje 1 bez wyjasnienia. Nie aktualizowano danych raw,
bazy ani polityki gluten_free w ramach tego etapu.
