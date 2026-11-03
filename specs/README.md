# Specyfikacje i sposób pracy SDD

Aktywny etap: [001 — stabilizacja MVP](001-mvp-stabilization/spec.md).
Najbliższe zadanie i stan prac: [tasks.md](001-mvp-stabilization/tasks.md).

## Role plików

| Plik w pakiecie etapu | Pytanie |
| --- | --- |
| `spec.md` | Co ma działać, jakie są granice i zatwierdzone decyzje? |
| `acceptance.md` | Jakie warunki musi spełnić rezultat? |
| `plan.md` | Jak i w jakiej kolejności osiągniemy ten rezultat? |
| `tasks.md` | Jakie konkretne zadania wykonujemy i jaki mają stan? |
| `verification.md` | Gdzie są testy i dowody, a gdzie brakuje pokrycia? |

To konwencja tego repozytorium. SDD nie narzuca jednej nazwy katalogu
ani zestawu plików. Nie instalujemy frameworka; używamy Markdown i Git.
Nie tworzymy kolejnej specyfikacji dla każdej notatki.

## Zasady utrzymania

1. Przed zmianą zachowania doprecyzuj wymaganie w `spec.md`, z identyfikatorem
   i przykładem, oraz powiąż je z ACC. Ogólne ustalenia rozwijamy iteracyjnie.
2. W `plan.md` opisz podejście i zależności. W `tasks.md` zapisz wykonalne zadanie
   oraz warunek jego ukończenia. Dopiero potem zmieniaj kod.
3. Weryfikuj względem ustaleń, aktualizuj mapę i stan zadania, dołącz raport,
   jeśli wykonano pomiar. Sama obecność testu nie oznacza zaliczenia kryterium.
4. Zatwierdzone decyzje utrzymuj w `spec.md`. Dawny raport nie zmienia
   bieżącego zakresu ani stanu zadań.
5. Aktualizuj istniejący plik zamiast dopisywać podobny dokument w `docs/`.
   Nie kopiuj tych samych wymagań do planu i raportów.
6. Nowy pakiet `NNN-nazwa/` twórz dla osobnej uzgodnionej zmiany lub etapu,
   nie dla drobnej poprawki w aktywnym pakiecie.
7. Raporty pomiarów zachowuj jako dowody. Archiwum nie jest backlogiem.

Obowiązuje zakres aktywnej specyfikacji. Materiały techniczne w
[docs](../docs/README.md) rozwijają szczegóły; rozbieżności rozstrzygamy
przed implementacją. Stan faktyczny opisuje [architektura](../docs/architecture.md).
Przyjęte wymaganie może czekać na implementację — wskazuje to `tasks.md`.
