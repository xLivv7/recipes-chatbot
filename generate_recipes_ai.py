import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import func
from core.database import SessionLocal, Ingredient, Recipe

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_next_recipe_id(db) -> str:
    """Znajduje najwyższe ID w formacie 'R000' i generuje kolejne."""
    max_id_str = db.query(func.max(Recipe.id)).filter(Recipe.id.like('R%')).scalar()
    
    if max_id_str:
        try:
            num = int(max_id_str[1:])
            return f"R{num + 1:03d}" 
        except ValueError:
            pass
            
    return "R001"

def fetch_ingredient_dictionary(db) -> str:
    """Pobiera wszystkie składniki z bazy i formatuje je do dla AI."""
    ingredients = db.query(Ingredient).all()
    #lista w formacie "C001: majonez, C002: ketchup..."
    ing_list = [f"{ing.id}: {ing.name_pl}" for ing in ingredients]
    return " | ".join(ing_list)

def generate_recipe_with_ai(dish_name: str, category: str, ingredient_dict: str):
    """Generuje przepis przy pomocy ai i zapisuje do bazy."""
    db = SessionLocal()
    try:
        #Zabezpieczenie przed duplikatami
        existing = db.query(Recipe).filter(func.lower(Recipe.title_pl) == dish_name.lower()).first()
        if existing:
            print(f"Przepis '{dish_name}' już istnieje (ID: {existing.id}). Pomijam.")
            return

        print(f"\nAI generuje przepis: '{dish_name}'...")
        
        #prompt dla AI
        prompt = f"""
        Jesteś szefem kuchni. Stwórz dokładny przepis na danie: "{dish_name}".
        Kategoria posiłku to: "{category}".
        WAŻNA ZASADA: 
        Do zbudowania listy składników możesz użyć TYLKO I WYŁĄCZNIE produktów z poniższej listy.
        Jeśli potrzebujesz składnika, którego tu nie ma, pomiń go lub zastąp dostępnym.
        DOSTĘPNE SKŁADNIKI (ID: Nazwa):
        {ingredient_dict}
        Zwróć TYLKO czysty obiekt JSON o takiej strukturze:
        {{
            "title_pl": "{dish_name.capitalize()}",
            "category": "{category.lower()}",
            "dish_type": "Krótki typ (np. Salad, Pasta, Casserole, Soup)",
            "time_min": 30,
            "servings": 2,
            "ingredients_data": [
                {{"concept_id": "TUTAJ WPISZ ID Z LISTY, np. C001", "grams": 150}},
                {{"concept_id": "TUTAJ WPISZ INNE ID Z LISTY", "grams": 20}}
            ],
            "steps_pl": [
                "Pierwszy krok przygotowania.",
                "Drugi krok przygotowania."
            ]
        }}
        """
        
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        res = json.loads(ai_response.choices[0].message.content)

        #Zapis do bazy
        r_id = get_next_recipe_id(db)
        
        new_recipe = Recipe(
            id=r_id,
            title_pl=res["title_pl"],
            category=res["category"],
            dish_type=res["dish_type"],
            time_min=res["time_min"],
            servings=res["servings"],
            ingredients_data=res["ingredients_data"], #jsonb
            steps_pl=res["steps_pl"]                  #jsonb
        )
        
        db.add(new_recipe)
        db.commit()
        print(f"OK ; ZAPISANO PRZEPIS: {res['title_pl']} (ID: {r_id})")

    except Exception as e:
        print(f"BŁĄD podczas generowania przepisu '{dish_name}': {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    db_session = SessionLocal()
    #wyciągam dict konceptów
    ingredient_map = fetch_ingredient_dictionary(db_session)
    db_session.close()
    
    if not ingredient_map:
        print("baza składników jest pusta!")
        exit()

    przepisy_do_wygenerowania = [
    ]
    
    print("Uruchamiam generator przepisów...")
    for nazwa_dania, kategoria in przepisy_do_wygenerowania:
        generate_recipe_with_ai(nazwa_dania, kategoria, ingredient_map)
        time.sleep(1.5) 
    
    print("\n--------Operacja zakończona--------")