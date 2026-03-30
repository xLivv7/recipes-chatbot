import os
from dotenv import load_dotenv
import pandas as pd
import json
from pathlib import Path

#ścieżka bazowa do danych
base = Path("data/raw")
# CSV (bezpośrednio w data/raw)
concepts = pd.read_csv(base / "ingredient_concepts.csv")
nutrients = pd.read_csv(base / "global_ingredients_nutrients.csv")

# CSV (w podfolderze clients/Winiary)
client_skus = pd.read_csv(base / "clients/Winiary/client_skus_canonical.csv")
sku_map = pd.read_csv(base / "clients/Winiary/sku_to_concept_map.csv")
rules = pd.read_csv(base / "clients/Winiary/sku_selection_rules.csv")

# JSON (bezpośrednio w data/raw)
with open(base / "recipe_templates.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

print("OK:", len(concepts), "concepts,", len(nutrients), "nutrient rows,", len(client_skus), "skus,", len(recipes), "recipes")



# Ta funkcja szuka pliku .env i ładuje jego zawartość do środowiska
load_dotenv()

# Próbujemy pobrać klucz
api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    print("Sukces! Twój klucz API jest poprawnie wczytany (jest bezpieczny, nie wyświetlamy go).")
else:
    print("Coś poszło nie tak. Upewnij się, że klucz jest zapisany w pliku .env jako OPENAI_API_KEY=...")