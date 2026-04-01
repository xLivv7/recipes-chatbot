import os
from dotenv import load_dotenv
import pandas as pd
import json
from pathlib import Path


'''
1: Wczytuję dane 
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
2: Zamieniam dane na dict, żeby łatwiej było z nich korzystać w dalszej części
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
X: Sprawdzam, czy klucz API jest poprawnie wczytany
'''
# Ta funkcja szuka pliku .env i ładuje jego zawartość do środowiska
load_dotenv()
# Próbujemy pobrać klucz
api_key = os.environ.get("OPENAI_API_KEY")
#Sprawdzam czy klucz jest ok
if api_key:
    print("Sukces! Twój klucz API jest poprawnie wczytany (jest bezpieczny, nie wyświetlamy go).")
else:
    print("Coś poszło nie tak. Upewnij się, że klucz jest zapisany w pliku .env jako OPENAI_API_KEY=...")