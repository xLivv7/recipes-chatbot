import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import json
from pathlib import Path
from typing import Callable
from core.llm_tools import RECIPE_TOOLS


'''
    Wczytuję dane 
'''
#ścieżka bazowa do danych
base = Path("data/raw")
# CSV (bezpośrednio w data/raw)
concepts = pd.read_csv(base / "ingredient_concepts.csv")
nutrients = pd.read_csv(base / "global_ingredients_nutrients.csv")
diet_policy = pd.read_csv(base / "concept_diet_policy.csv")

# CSV (w podfolderze clients/Winiary)
client_skus = pd.read_csv(base / "clients/Winiary/client_skus_canonical.csv")
sku_map = pd.read_csv(base / "clients/Winiary/sku_to_concept_map.csv")
rules = pd.read_csv(base / "clients/Winiary/sku_selection_rules.csv")

# JSON (bezpośrednio w data/raw)
with open(base / "recipe_templates.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

'''
    Zamieniam dane na dict, żeby łatwiej było z nich korzystać w dalszej części
'''

diet_policy_by_concept = diet_policy.set_index("concept_id").to_dict(orient="index")

nutrients_by_concept = nutrients.set_index("concept_id")[
    ["energy_kcal_100g", "protein_g_100g", "fat_g_100g", "carbs_g_100g"]
].to_dict(orient="index")

skus_by_id = client_skus.set_index("client_sku_id").to_dict(orient="index")

concept_to_skus = {}
for _, row in sku_map.iterrows():
    concept_to_skus.setdefault(row["concept_id"], []).append(row["client_sku_id"])

rules_by_concept = {}
for cid, grp in rules.groupby("concept_id"):
    rules_by_concept[cid] = grp.sort_values("rule_order").to_dict(orient="records")

concept_name = concepts.set_index("concept_id")["name_pl"].to_dict()

# Obsługa różnych nazw kolumn dla nazwy produktu
if "name_pl" in client_skus.columns:
    sku_name = client_skus.set_index("client_sku_id")["name_pl"].to_dict()
elif "sku_name_pl" in client_skus.columns:
    sku_name = client_skus.set_index("client_sku_id")["sku_name_pl"].to_dict()
else:
    sku_name = {}

'''
    Funkcje pomocnicze do sprawdzania zgodności diety i preferencji oraz do orkiestracji przepisów
'''

PREF_TO_DIET = {
    "none": None,
    "vege": "vegetarian",
    "vegetarian": "vegetarian",
    "vegan": "vegan",
    "meat": "meat",
    "fish": "fish",
    "pescetarian": "pescetarian",
}

def concept_allows_diet(concept_id: str, diet: str | None) -> bool:
    if diet is None:
        return True
    row = diet_policy_by_concept.get(concept_id)
    if row is None:
        return True 
    if diet == "vegetarian":
        return int(row["is_vegetarian_ok"]) == 1
    if diet == "vegan":
        return int(row["is_vegan_ok"]) == 1
    raise ValueError(f"Unknown diet: {diet}")

def recipe_matches_user_pref(recipe: dict, user_pref: str) -> bool:
    diet = PREF_TO_DIET.get(user_pref, None)
    if diet is None:
        return True
        
    # LOGIKA DLA MIĘSA
    if diet == "meat":
        for ing in recipe.get("ingredients", []):
            row = diet_policy_by_concept.get(ing["concept_id"])
            # Proste i twarde sprawdzenie: czy to jest mięso?
            if row is not None and int(row.get("is_meat", 0)) == 1:
                return True
        return False

    # LOGIKA DLA RYB
    if diet == "fish":
        for ing in recipe.get("ingredients", []):
            row = diet_policy_by_concept.get(ing["concept_id"])
            # Proste sprawdzenie: czy to jest ryba/owoce morza?
            if row is not None and int(row.get("is_fish", 0)) == 1:
                return True
        return False

    # LOGIKA DLA PESCETARIAN
    if diet == "pescetarian":
        for ing in recipe.get("ingredients", []):
            row = diet_policy_by_concept.get(ing["concept_id"])
            # Odrzucamy przepis od razu, jeśli jakikolwiek składnik ma flagę mięsa
            if row is not None and int(row.get("is_meat", 0)) == 1:
                return False
        # Jeśli przeszliśmy pętlę i nie było mięsa - przepis jest bezpieczny
        return True

    # Dla wegetariańskich i wegańskich preferencji
    for ing in recipe.get("ingredients", []):
        if not concept_allows_diet(ing["concept_id"], diet):
            return False
            
    return True

'''
    orkiestracja przepisów i składanie rekomendacji
'''

def choose_sku(concept_id: str, user_pref: str, nutrition_goal: str):
    if concept_id not in rules_by_concept:
        return None
    for rule in rules_by_concept[concept_id]:
        ctype = rule["condition_type"]
        cval = str(rule["condition_value"])
        sku_id = rule["preferred_sku_id"]
        
        if ctype == "user_pref" and cval == user_pref: return sku_id
        if ctype == "nutrition_goal" and cval == nutrition_goal: return sku_id
        if ctype == "default": return sku_id
    return None

def orchestrate_recipe(recipe_id: str, user_pref="none", nutrition_goal="standard"):
    recipe = next((r for r in recipes if r["recipe_id"] == recipe_id), None)
    if recipe is None:
        raise ValueError(f"Recipe not found: {recipe_id}")

    total = {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
    brandified_ingredients = []
    used_skus = []

    for ing in recipe["ingredients"]:
        cid = ing["concept_id"]
        grams = float(ing["grams"])
        sku_id = None
        
        if cid in concept_to_skus:
            sku_id = choose_sku(cid, user_pref=user_pref, nutrition_goal=nutrition_goal)

        if sku_id is not None:
            sku_row = skus_by_id[sku_id]
            kcal_100 = float(sku_row["energy_kcal_100"])
            p_100 = float(sku_row["protein_g_100"])
            f_100 = float(sku_row["fat_g_100"])
            c_100 = float(sku_row["carbs_g_100"])
            brandified_ingredients.append({"concept_id": cid, "sku_id": sku_id, "grams": grams})
            used_skus.append(sku_id)
        else:
            n = nutrients_by_concept.get(cid)
            if n is None:
                raise ValueError(f"Missing nutrients for concept {cid}")
            kcal_100 = float(n["energy_kcal_100g"])
            p_100 = float(n["protein_g_100g"])
            f_100 = float(n["fat_g_100g"])
            c_100 = float(n["carbs_g_100g"])
            brandified_ingredients.append({"concept_id": cid, "grams": grams})

        mult = grams / 100.0
        total["kcal"] += kcal_100 * mult
        total["protein"] += p_100 * mult
        total["fat"] += f_100 * mult
        total["carbs"] += c_100 * mult

    servings = float(recipe.get("servings", 1))
    per_serv = {k: v / servings for k, v in total.items()}

    return {
        "recipe_id": recipe["recipe_id"],
        "title_pl": recipe["title_pl"],
        "time_min": recipe["time_min"],
        "servings": recipe["servings"],
        "brandified_ingredients": brandified_ingredients,
        "used_skus": sorted(set(used_skus)),
        "nutrition_total": total,
        "nutrition_per_serving": per_serv,
        "steps_pl": recipe["steps_pl"],
    }

def score_recipe(result: dict, nutrition_goal: str = "standard"):
    used = len(result["used_skus"])
    kcal = float(result["nutrition_per_serving"]["kcal"])
    protein = float(result["nutrition_per_serving"]["protein"])

    if nutrition_goal == "low_kcal": return (-kcal, protein, used)
    if nutrition_goal == "high_protein": return (protein, -kcal, used)
    return (used, -kcal, protein)

def orchestrate_top_n(user_pref="none", nutrition_goal="standard", top_n=3, category="kolacja", time_max=None):
    results = []
    for r in recipes:
        if category and r.get("category") != category: continue
        if time_max is not None and float(r.get("time_min", 9999)) > float(time_max): continue
        if not recipe_matches_user_pref(r, user_pref): continue
        
        try:
            res = orchestrate_recipe(r["recipe_id"], user_pref=user_pref, nutrition_goal=nutrition_goal)
            if "dish_type" not in res:
                res["dish_type"] = r.get("dish_type", "unknown")
            results.append(res)
        except Exception:
            continue

    results.sort(key=lambda x: score_recipe(x, nutrition_goal=nutrition_goal), reverse=True)

    selected, used_types = [], set()
    for res in results:
        dt = res.get("dish_type", "unknown")
        if dt in used_types: continue
        selected.append(res)
        used_types.add(dt)
        if len(selected) >= top_n: return selected

    if len(selected) < top_n:
        selected_ids = {r["recipe_id"] for r in selected}
        for res in results:
            if res["recipe_id"] in selected_ids: continue
            selected.append(res)
            if len(selected) >= top_n: break
    return selected

def get_recommendations(user_pref="none", nutrition_goal="standard", top_n=3, category="kolacja", time_max=None):
    top = orchestrate_top_n(user_pref, nutrition_goal, top_n, category, time_max)
    recs = []

    for rank, r in enumerate(top, start=1):
        serv = float(r.get("servings", 1))
        
        used_skus = [{"client_sku_id": sid, "name_pl": sku_name.get(sid, sid)} for sid in r.get("used_skus", [])]
        
        ingredients_out = []
        for ing in r.get("brandified_ingredients", []):
            cid = ing["concept_id"]
            grams_total = float(ing["grams"])
            item = {
                "concept_id": cid,
                "name_pl": concept_name.get(cid, cid),
                "grams_total": grams_total,
                "grams_per_serving": grams_total / serv
            }
            if "sku_id" in ing:
                item["client_sku_id"] = ing["sku_id"]
                item["client_sku_name_pl"] = sku_name.get(ing["sku_id"], ing["sku_id"])
            ingredients_out.append(item)

        recs.append({
            "rank": rank,
            "recipe_id": r["recipe_id"],
            "title_pl": r["title_pl"],
            "category": r.get("category", category),
            "dish_type": r.get("dish_type", "unknown"),
            "time_min": r.get("time_min"),
            "servings": r.get("servings"),
            "nutrition_per_serving": r.get("nutrition_per_serving"),
            "nutrition_total": r.get("nutrition_total"),
            "used_skus": used_skus,
            "ingredients": ingredients_out,
            "steps_pl": r.get("steps_pl", [])
        })

    return {
        "query": {"user_pref": user_pref, "nutrition_goal": nutrition_goal, "category": category, "time_max": time_max, "top_n": top_n},
        "recommendations": recs
    }

'''
    Normalizacja i walidacja (pod LLM)
'''

def safe_round(value, ndigits=1):
    return round(value, ndigits) if isinstance(value, (int, float)) else value

def safe_str(value) -> str:
    return str(value).strip() if value is not None else ""

def normalize_ingredient(ingredient: dict) -> dict:
    return {
        "concept_id": ingredient.get("concept_id"),
        "name_pl": safe_str(ingredient.get("name_pl")),
        "grams_total": safe_round(ingredient.get("grams_total"), 0),
        "grams_per_serving": safe_round(ingredient.get("grams_per_serving"), 0),
    }

def normalize_nutrition(nutrition: dict) -> dict:
    nutrition = nutrition or {}
    return {
        "kcal": safe_round(nutrition.get("kcal"), 1),
        "protein": safe_round(nutrition.get("protein"), 1),
        "fat": safe_round(nutrition.get("fat"), 1),
        "carbs": safe_round(nutrition.get("carbs"), 1),
    }

def normalize_steps(steps) -> list[str]:
    return [safe_str(step) for step in steps if safe_str(step)] if isinstance(steps, list) else []

def normalize_recipe(recipe: dict) -> dict:
    return {
        "rank": recipe.get("rank"),
        "recipe_id": recipe.get("recipe_id"),
        "title_pl": safe_str(recipe.get("title_pl")),
        "category": safe_str(recipe.get("category")),
        "dish_type": safe_str(recipe.get("dish_type")),
        "time_min": recipe.get("time_min"),
        "servings": recipe.get("servings"),
        "nutrition_per_serving": normalize_nutrition(recipe.get("nutrition_per_serving")),
        "nutrition_total": normalize_nutrition(recipe.get("nutrition_total")),
        "used_skus": recipe.get("used_skus", []),
        "ingredients": [normalize_ingredient(ing) for ing in recipe.get("ingredients", [])],
        "steps_pl": normalize_steps(recipe.get("steps_pl")),
    }

def normalize_recommendations_output(raw_data: dict) -> dict:
    raw_query = raw_data.get("query", {})
    return {
        "query": {
            "user_pref": safe_str(raw_query.get("user_pref")),
            "nutrition_goal": safe_str(raw_query.get("nutrition_goal")),
            "category": safe_str(raw_query.get("category")),
            "time_max": raw_query.get("time_max"),
            "top_n": raw_query.get("top_n"),
        },
        "recommendations": [normalize_recipe(r) for r in raw_data.get("recommendations", [])]
    }

def validate_recommendations_output(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict): return ["Dane wejściowe nie są słownikiem (dict)."]
    if "query" not in data: errors.append("Brak pola 'query'.")
    if "recommendations" not in data:
        errors.append("Brak pola 'recommendations'.")
        return errors
    if not isinstance(data["recommendations"], list):
        errors.append("'recommendations' nie jest listą.")
        return errors

    for idx, recipe in enumerate(data["recommendations"], start=1):
        if not recipe.get("recipe_id"): errors.append(f"Rekomendacja #{idx}: brak 'recipe_id'.")
        if not recipe.get("title_pl"): errors.append(f"Rekomendacja #{idx}: brak 'title_pl'.")
        if "nutrition_per_serving" not in recipe: errors.append(f"Rekomendacja #{idx}: brak 'nutrition_per_serving'.")
        if "nutrition_total" not in recipe: errors.append(f"Rekomendacja #{idx}: brak 'nutrition_total'.")
    return errors

'''
    Integracja z LLM - przygotowanie promptu i wywołanie API + Sprawdzam, czy klucz API jest poprawnie wczytany
'''
# Ta funkcja szuka pliku .env i ładuje jego zawartość
load_dotenv()
# Próbuję pobrać klucz
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def chat_with_bot(user_message: str, brand_name: str) -> str:
    # 1. Inicjalizacja konwersacji
    system_prompt = (
        "Jesteś kulinarnym asystentem. Twoim zadaniem jest pomaganie użytkownikom w znalezieniu "
        "idealnego posiłku. Zawsze używaj narzędzia 'get_recommendations', aby wyszukać przepisy w bazie. "
        "Gdy otrzymasz wyniki z narzędzia, przedstaw je w czytelny, apetyczny sposób w Markdown.\n\n"
        "ZASADY FORMATOWANIA:\n"
        "1. Zawsze podawaj czas przygotowania, kalorie i makro na porcję (kcal | B | T | W).\n"
        "2. Nie zmyślaj przepisów, składników ani wartości odżywczych spoza dostarczonych wyników.\n"
        "3. ZABRONIONE jest generowanie jakichkolwiek linków (URL) w odpowiedzi.\n"
        "4. Jeśli w wynikach w polu 'used_skus' znajdują się produkty, dodaj pod przepisem naturalną poradę. "
        f"WAŻNE: Pracujesz dla marki {brand_name}. Zawsze płynnie dodaj słowo '{brand_name}' do nazwy promowanego produktu. "
        "Zignoruj i usuń techniczne dopiski z nazwy w nawiasach, takie jak '(butelka)' czy '(słoik)'."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # 2. wiadomość usera idzie do modelu i on decyduje co robi dakej
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=RECIPE_TOOLS,
        tool_choice="auto", # decyzja modelu czy użyć naredzia
        temperature=0.1
    )
    
    response_message = response.choices[0].message
    
    # 3. Sprawdzam czy model użył toola
    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
        function_name = tool_call.function.name
        # Pobieramy parametry, które LLM zextractował z zapytania użytkownika
        function_args = json.loads(tool_call.function.arguments)
        
        print(f"🔧 [DEBUG] Model wywołuje Pythonową funkcję '{function_name}' z argumentami: {function_args}")
        
        # Uruchamiam twardą logikę w Pythonie
        if function_name == "get_recommendations":
            raw_data = get_recommendations(
                user_pref=function_args.get("user_pref", "none"),
                nutrition_goal=function_args.get("nutrition_goal", "standard"),
                category=function_args.get("category", "kolacja"),
                time_max=function_args.get("time_max"),
                top_n=function_args.get("top_n", 3)
            )
            # Normalizacja JSON'a pod model
            function_result = normalize_recommendations_output(raw_data)
        else:
            function_result = {"error": "Nieznana funkcja"}

        # 4. Zwracam wyniki działania Pythonowej funkcji z powrotem do LLM
        # Trzeba dodać do historii to, co model wysłał w kroku 2
        messages.append(response_message)
        
        # Dorzucam odpowiedź narzędzia(wygenerowany JSON)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(function_result, ensure_ascii=False)
        })
        
        # 5. Ostatnie wywołanie;model ma już JSON'a i redaguje dla nas ładną odpowiedź
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2
        )
        
        return final_response.choices[0].message.content
        
    else:
        # jeśli nie ma wywołania narzędzia, return samej odpowiedzi/komunikatu 
        return response_message.content
    


'''
    Uruchamiam pipeline rekomendacji 
'''

if __name__ == "__main__":
    user_input = "Zaproponuj mi kolację z rybą"

    print(f"👤 Użytkownik: {user_input}\n")
    answer = chat_with_bot(user_input, brand_name="Winiary")
    print("\n🤖 Asystent:\n")
    print(answer)