import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from core.llm_tools import RECIPE_TOOLS
from core.recommendation_normalization import normalize_recommendations_output
from core.recommendations import get_recommendations


load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def build_system_prompt(brand_name: str) -> str:
    return (
        "Jesteś kulinarnym asystentem. Twoim zadaniem jest pomaganie użytkownikom w znalezieniu "
        "idealnego posiłku. Zawsze używaj narzędzia 'get_recommendations', aby wyszukać przepisy w bazie. "
        "Gdy otrzymasz wyniki z narzędzia, przedstaw je w czytelny, apetyczny sposób w Markdown.\n\n"
        "ZASADY FORMATOWANIA:\n"
        "1. Zawsze podawaj czas przygotowania, kalorie i makro na porcję (kcal | B | T | W).\n"
        "2. Nie zmyślaj przepisów, składników ani wartości odżywczych spoza dostarczonych wyników.\n"
        "3. ZABRONIONE jest generowanie jakichkolwiek linków (URL) w odpowiedzi.\n"
        "4. Jeśli w wynikach w polu 'used_skus' znajdują się produkty, dodaj pod przepisem naturalną poradę. "
        f"WAŻNE: Pracujesz dla marki {brand_name}. Zawsze płynnie dodaj słowo '{brand_name}' "
        "do nazwy promowanego produktu. Zignoruj i usuń techniczne dopiski z nazwy w nawiasach, "
        "takie jak '(butelka)' czy '(słoik)'."
    )


def run_recommendation_tool(function_args: dict) -> dict:
    raw_data = get_recommendations(
        user_pref=function_args.get("user_pref", "none"),
        nutrition_goal=function_args.get("nutrition_goal", "standard"),
        category=function_args.get("category", "kolacja"),
        time_max=function_args.get("time_max"),
        top_n=function_args.get("top_n", 3),
    )
    return normalize_recommendations_output(raw_data)


def chat_with_bot(user_message: str, brand_name: str) -> str:
    messages = [
        {"role": "system", "content": build_system_prompt(brand_name)},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=RECIPE_TOOLS,
        tool_choice="auto",
        temperature=0.1,
    )

    response_message = response.choices[0].message
    if not response_message.tool_calls:
        return response_message.content

    tool_call = response_message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    print(f"[DEBUG] Model calls Python function '{function_name}' with args: {function_args}")

    if function_name == "get_recommendations":
        function_result = run_recommendation_tool(function_args)
    else:
        function_result = {"error": "Unknown function"}

    messages.append(response_message)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(function_result, ensure_ascii=False),
        }
    )

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )

    return final_response.choices[0].message.content


if __name__ == "__main__":
    user_input = "Szukam pomysłu na szybką kolację, wegańską do 30 minut. Co polecasz?"

    print(f"Użytkownik: {user_input}\n")
    answer = chat_with_bot(user_input, brand_name="Winiary")
    print("\nAsystent:\n")
    print(answer)
