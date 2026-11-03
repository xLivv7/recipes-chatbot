# T009 — przygotowanie kampanii routingu

Data: 2026-11-03. Status: część offline wykonana; płatna kampania nieuruchomiona.

## Wersje i zakres

- `005efef` — specyfikacja eksperymentu T008.
- `a1f7583` — instrumentacja i zamrożone prompty V0/V1/V2.
- Aktywny prompt `main.py`, schemat, dane oraz expected przypadków pozostają bez zmian.
- Warianty zapisano w `evals/routing_prompts/`; V0 jest identyczny z promptem
  bazowym `97638cf`, V1/V2 realizują wyłącznie transformacje zadeklarowane w T008.

Nowy `evals/run_routing_experiment.py` przygotowuje manifest i osobne
pliki promptów, sprawdza hashe przed wykonaniem, rotuje trzy rundy,
zapisuje grupy raw/application i checkpointy. Agregator sprawdza kompletność
przypadków, etykiety, numery rund i wersję modelu, a następnie stosuje
ustaloną regułę wyboru. Wybór kandydata nie zmienia promptu aplikacji.

Raw i application używają tego samego wybranego promptu. Uwzględniono
lokalny import funkcji promptu w `run_llm_eval.py`. Poprawny JSON w zwykłym
tekście pozostaje błędem kanału; odczyt parserem służy tylko diagnostyce.

## Kontrole offline

Pełna regresja: **240 testów, 0 niepowodzeń, 0 błędów, 0 pominięć**.
Dziesięć nowych metod z wariantami sprawdza m.in. równoważność przykładów,
izolację promptu, protokół i argumenty, błędne blokady preflight,
brak API w przygotowaniu, rotację, agregację, wybór i remisy, zmiany
resolved model, zatrzymanie po błędzie API i zakaz selektywnego wznowienia.
Rzeczywiste żądania OpenAI były blokowane w testach.

Dowody testowe:
[wynik](../../dokumentacja%20pracy/2026-11-03_t006/t009_full.json),
[log](../../dokumentacja%20pracy/2026-11-03_t006/t009_full.log).
Katalog nazwy T006 jest lokalizacją współdzielonego runnera; nazwa plików
jednoznacznie identyfikuje kontrole T009.

## Zamrożona kampania i koszt

Przygotowano `2026-11-03_t009_campaign_01`:
[manifest](../../dokumentacja%20pracy/2026-11-03_t009_campaign_01/manifest.json).
Zawiera pełne przypadki i prompty, hashe kodu, specyfikacji, schematu,
zbiorów, konfigurację oraz wersje bibliotek.

- 3 warianty × 3 rundy × 2 tryby × 76 przypadków = 1368 ocen.
- Plan: 1278 wywołań SDK; nie obejmuje dodatkowych żądań retry SDK.
- 66 obsługiwanych próśb i 10 no_tool; niezmienione znane false positives.
- **Faktyczne wywołania API: 0.**

Według [oficjalnej karty modelu](https://developers.openai.com/api/docs/models/gpt-4o-mini)
sprawdzonej 2026-11-03 cena wynosi 0,15 USD / milion tokenów wejściowych
i 0,60 USD / milion wyjściowych. Nie założono zniżki cache.

Manifest szacuje wejście konserwatywnie przez liczbę bajtów UTF-8
zserializowanych żądań plus 2000 tokenów narzutu na wywołanie, a nie
dokładnym tokenizerem. Daje to proxy 13 279 680 tokenów wejściowych:
około **2,38 USD** przy założeniu 500 tokenów odpowiedzi na wywołanie
lub **14,56 USD** przy maksymalnych 16 384 tokenach odpowiedzi.
To scenariusze szacunkowe, nie twardy limit rachunku. Retry i podatki są
poza szacunkiem; rzeczywiste usage zostanie zapisane w wynikach.
Karta modelu oznacza snapshot jako deprecated; nie zastępujemy go innym
modelem bez zmiany planu. Dostępność na koncie nie została zmierzona API.

## Stan wykonania

Automatyczna kontrola uprawnień odrzuciła polecenie uruchomienia kampanii
przed startem procesu. Powód: mimo zgody na T009 uznała brak jednoznacznej
autoryzacji przesłania opisanego payloadu do OpenAI oraz kosztu płatnych
wywołań. Nie ponawiano polecenia ani nie obchodzono blokady.
Wyświetlono autorce prośbę o zgodę obejmującą treści 76 kontrolowanych
zapytań, prompty V0/V1/V2, schemat, odbiorcę i oszacowanie kosztów.

Manifest pozostaje `prepared`; nie powstały raporty rund ani porównanie.
Nie wybrano zwycięzcy i nie oceniono progów 90%/85%. T009 nie jest
ukończone: dalszy krok to wykonanie niezmienionej zamrożonej kampanii po
jednoznacznym zatwierdzeniu płatnego etapu. Pięć SKU pozostaje wstrzymanych.
