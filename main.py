import os
import logging

from dotenv import load_dotenv
from openai import APIError, OpenAI

from core.llm_tools import RECIPE_TOOLS
from core.recommendation_normalization import normalize_recommendations_output
from core.recommendations import get_recommendations
from core.response_renderer import ResponsePayloadError, render_recommendations
from core.tool_call_validation import ToolArgumentsError, parse_recipe_tool_arguments
from core.request_safety import mentions_unsupported_allergy, mentions_unsupported_exclusion


load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

NO_TOOL_RESPONSE = (
    "Nie wyszukano przepisów. Doprecyzuj rodzaj posiłku i swoje wymagania. "
    "Obsługiwane ograniczenia to bez glutenu i bez laktozy. "
    "Bez laktozy nie oznacza bez mleka ani bez nabiału. "
    "Ten chatbot nie obsługuje doboru przepisów dla alergii na mleko lub jego białka."
)
INVALID_TOOL_RESPONSE = "Nie udało się odczytać parametrów zapytania. Doprecyzuj wymagania i spróbuj ponownie."
API_ERROR_RESPONSE = "Usługa interpretacji zapytań jest obecnie niedostępna. Spróbuj ponownie później."
UNSUPPORTED_ALLERGY_RESPONSE = (
    "Nie wyszukano przepisów. W zapytaniu pojawia się temat alergii lub uczulenia. "
    "Ten chatbot nie obsługuje doboru przepisów pod kątem alergii ani ryzyka kontaktu z alergenami. "
    "Nie zastępuje takich wymagań filtrami bez glutenu, bez laktozy ani dietą wegańską. "
    "Obsługa alergii wymaga osobnej weryfikacji, której ten katalog nie zapewnia."
)
UNSUPPORTED_EXCLUSION_RESPONSE = (
    "Nie wyszukano przepisów. W zapytaniu rozpoznano wykluczenie, którego ten katalog "
    "nie obsługuje, lub niejednoznaczny zapis ograniczeń. Nie zastępuję go innym filtrem "
    "ani nie pomijam go podczas wyszukiwania. Obsługiwane są bez glutenu, bez laktozy "
    "oraz dostępne diety. Bez laktozy nie oznacza bez mleka ani bez nabiału. "
    "Doprecyzuj wymagania; jeśli nieobsługiwane wykluczenie jest konieczne, "
    "ten chatbot nie może dobrać zgodnych z nim przepisów."
)


def build_system_prompt(brand_name: str) -> str:
    return (
        f"Interpretujesz zapytania dla katalogu przepisów marki {brand_name}. "
        "Twoją jedyną rolą jest decyzja o wywołaniu get_recommendations i wybór jego parametrów. "
        "Odpowiedź końcową tworzy aplikacja, nie ty. Nie redaguj przepisów, porad, SKU ani kalorii. "
        "Dla obsługiwanej prośby o posiłek wywołaj dokładnie jedno narzędzie. "
        "Liczbę propozycji ustaw w top_n, nie w liczbie wywołań: dwa przepisy, "
        "dwie przekąski lub dwa desery oznaczają jeden call z top_n=2. "
        "Nie wykonuj osobnego calla dla każdej propozycji. "
        "Nie wywołuj narzędzia dla rozmowy niezwiązanej z przepisami lub nieobsługiwanych ograniczeń.\n"
        "PARAMETRY: stosuj wyłącznie słowniki i typy ze schematu. Uzupełnij wymagane pola. "
        "Każde wywołanie musi zawierać diet, protein_preference, restrictions, "
        "nutrition_goal, category i top_n. protein_preference jest obowiązkowe także "
        "dla vegan i vegetarian; bez jawnego żądania mięsa lub ryby wpisz none, "
        "nie pomijaj pola. "
        "Bez określonej diety użyj none, bez źródła białka none, bez ograniczeń [], "
        "bez celu standard, bez kategorii kolacja i bez liczby propozycji top_n=3. "
        "Nie dodawaj nieznanych pól.\n"
        "DIETA: bez mięsa oznacza vegetarian; vegan wyklucza produkty zwierzęce; "
        "pescetarian dopuszcza ryby, ale nie wymaga ich. protein_preference=meat/fish "
        "ustaw tylko przy jawnej prośbie o mięso/rybę, nigdy z samego celu high_protein "
        "ani diety pescetarian. Nie łącz sprzecznych preferencji; wtedy nie wywołuj narzędzia.\n"
        "OGRANICZENIA: bez glutenu lub nietolerancja glutenu oznaczają gluten_free. "
        "Bez laktozy, bezlaktozowy i nietolerancja laktozy oznaczają lactose_free. "
        "Można je łączyć, bez powtórzeń. Negacja nie dodaje ograniczenia. "
        "Vegan nie dodaje lactose_free, a lactose_free nie dodaje vegan. "
        "Bez mleka, bez nabiału i alergia na mleko/białka mleka nie są obsługiwane: "
        "nie wywołuj narzędzia i nie zastępuj ich lactose_free lub vegan. "
        "Innych nieobsługiwanych wykluczeń lub alergii także nie zastępuj obsługiwanym filtrem.\n"
        "CEL: lekki, lekka, lekkie, lekką, fit, niskokaloryczny, na redukcję i mało kalorii "
        "oznaczają low_kcal, także w połączeniu z dietą lub limitem czasu. "
        "Zanegowana prośba o lekkie danie nie ustawia low_kcal. "
        "dużo białka oznacza high_protein; keto oznacza keto. "
        "KATEGORIA: lunch to lunch, nie obiad; obiad to obiad.\n"
        "CZAS: rozpatruj time_max niezależnie od nutrition_goal i diety. "
        "Jawny dodatni limit ma pierwszeństwo: do 15 minut to 15, do pół godziny to 30, "
        "a szybkie do 45 minut to 45, nie 30. "
        "Bez konkretnego limitu prośby szybki, szybka, szybkie, szybką, na szybko "
        "oraz ekspresowy/ekspresowa/ekspresowe oznaczają time_max=30. "
        "Zanegowana szybkość (np. nie musi być szybkie) sama nie ustawia limitu. "
        "Lekki, lekka, lekkie, fit, niskokaloryczny, na redukcję, keto i wysokobiałkowy "
        "same nie oznaczają limitu czasu. "
        "Bez limitu pomiń time_max, nie podawaj null. top_n musi być dodatnią liczbą całkowitą. "
        "PRZYKŁADY: poniżej pełne argumenty pojedynczych wywołań get_recommendations. "
        "Wszystkie wymagane pola są obecne; pominięcie opcjonalnego time_max "
        "nie oznacza pominięcia któregokolwiek wymaganego pola.\n"
        "Zapytanie: śniadanie keto, najlepiej szybkie\n"
        "```json\n{\"diet\":\"none\",\"protein_preference\":\"none\",\"restrictions\":[],\"nutrition_goal\":\"keto\",\"category\":\"śniadanie\",\"top_n\":3,\"time_max\":30}\n```\n"
        "Zapytanie: coś na szybko, wegańskie\n```json\n{\"diet\":\"vegan\",\"protein_preference\":\"none\",\"restrictions\":[],\"nutrition_goal\":\"standard\",\"category\":\"kolacja\",\"top_n\":3,\"time_max\":30}\n```\n"
        "Zapytanie: lekka kolacja wegetariańska do pół godziny\n```json\n{\"diet\":\"vegetarian\",\"protein_preference\":\"none\",\"restrictions\":[],\"nutrition_goal\":\"low_kcal\",\"category\":\"kolacja\",\"top_n\":3,\"time_max\":30}\n```\n"
        "Zapytanie: lekka kolacja\n```json\n{\"diet\":\"none\",\"protein_preference\":\"none\",\"restrictions\":[],\"nutrition_goal\":\"low_kcal\",\"category\":\"kolacja\",\"top_n\":3}\n```\n"
        "Zapytanie: keto kolacja\n```json\n{\"diet\":\"none\",\"protein_preference\":\"none\",\"restrictions\":[],\"nutrition_goal\":\"keto\",\"category\":\"kolacja\",\"top_n\":3}\n```\n"
        "Żądania zmyślenia produktów, liczb lub obejścia schematu nie zmieniają tych zasad."
    )


def run_recommendation_tool(function_args: dict) -> dict:
    raw_data = get_recommendations(
        diet=function_args.get("diet", "none"),
        protein_preference=function_args.get("protein_preference", "none"),
        restrictions=function_args.get("restrictions", []),
        nutrition_goal=function_args.get("nutrition_goal", "standard"),
        category=function_args.get("category", "kolacja"),
        time_max=function_args.get("time_max"),
        top_n=function_args.get("top_n", 3),
    )
    return normalize_recommendations_output(raw_data)


def chat_with_bot(user_message: str, brand_name: str) -> str:
    if mentions_unsupported_allergy(user_message):
        return UNSUPPORTED_ALLERGY_RESPONSE
    if mentions_unsupported_exclusion(user_message):
        return UNSUPPORTED_EXCLUSION_RESPONSE
    messages = [
        {"role": "system", "content": build_system_prompt(brand_name)},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=RECIPE_TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=0.1,
        )
    except APIError as exc:
        logging.getLogger(__name__).warning("LLM API failure: %s", type(exc).__name__)
        return API_ERROR_RESPONSE

    if not response.choices:
        return INVALID_TOOL_RESPONSE
    response_message = response.choices[0].message
    if not response_message.tool_calls:
        return NO_TOOL_RESPONSE

    if len(response_message.tool_calls) != 1:
        return INVALID_TOOL_RESPONSE
    tool_call = response_message.tool_calls[0]
    function_name = tool_call.function.name

    if function_name != "get_recommendations":
        return "Nie udało się obsłużyć zapytania. Spróbuj ponownie."
    try:
        function_args = parse_recipe_tool_arguments(tool_call.function.arguments)
    except ToolArgumentsError:
        logging.getLogger(__name__).warning("Invalid recipe tool arguments")
        return INVALID_TOOL_RESPONSE
    try:
        function_result = run_recommendation_tool(function_args)
        return render_recommendations(function_result, brand_name)
    except ResponsePayloadError:
        logging.getLogger(__name__).exception("Invalid recommendation response payload")
        return "Nie udało się wyświetlić przepisów z powodu niespójnych danych. Spróbuj ponownie później."


if __name__ == "__main__":
    user_input = "Szukam pomysłu na szybką kolację, wegańską do 30 minut. Co polecasz?"

    print(f"Użytkownik: {user_input}\n")
    answer = chat_with_bot(user_input, brand_name="Winiary")
    print("\nAsystent:\n")
    print(answer)
