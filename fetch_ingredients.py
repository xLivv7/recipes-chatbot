import os
import requests
import json
import time
import re
from dotenv import load_dotenv
from openai import OpenAI
from core.database import SessionLocal, Ingredient, Nutrient, DietPolicy

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def slugify(text: str) -> str:
    """Zamienia tekst na bezpieczny identyfikator (slug)."""
    # Zamiana na małe litery i usunięcie polskich znaków (opcjonalnie, ale bezpieczniej)
    text = text.lower()
    pl_chars = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'}
    for pl, en in pl_chars.items():
        text = text.replace(pl, en)
    
    # Zamiana spacji na myślniki
    text = text.replace(' ', '-')
    # Usunięcie wszystkiego co nie jest literą, cyfrą lub myślnikiem (usuwa %, ., ,, itp.)
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Usunięcie podwójnych myślników
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def fetch_generic_concept(query: str):
    db = SessionLocal()
    try:
        print(f"\n🧪 Przetwarzam koncept: '{query}'...")
        
        products_data = []
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 5,
            "fields": "product_name_pl,product_name,nutriments"
        }

        try:
            # TUTAJ ZNAJDUJE SIĘ ZMODYFIKOWANY USER-AGENT
            headers = {
                "User-Agent": "RecipesChatbot - Python - Version 1.0 - (orypinska)"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                products_data = response.json().get("products", [])
            else:
                print(f"⚠️ OFF status {response.status_code}. AI użyje wiedzy ogólnej.")
        except Exception as e:
            print(f"⚠️ Brak połączenia z OFF: {e}. AI użyje wiedzy ogólnej.")

        # AI buduje dane
        context = json.dumps(products_data) if products_data else "Brak danych zewnętrznych."
        
        # Generujemy czysty slug przed wysłaniem do AI, żeby AI też go znało
        clean_id = slugify(query)

        prompt = f"""
        Stwórz uśredniony koncept dietetyczny dla: "{query}".
        Dane pomocnicze: {context}
        Zwróć TYLKO czysty JSON:
        {{
            "concept_id": "{clean_id}",
            "name_pl": "{query.capitalize()}",
            "kcal": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0,
            "is_vegetarian": 1, "is_vegan": 0, "is_meat": 0, "is_fish": 0, "is_keto": 0
        }}
        """
        
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        res = json.loads(ai_response.choices[0].message.content)

        # ZAPIS DO BAZY
        c_id = res["concept_id"] # To już jest nasz czysty slug
        
        # A. Składnik
        db.merge(Ingredient(id=c_id, name_pl=res["name_pl"]))
        db.flush() 

        # B. Makro
        db.merge(Nutrient(
            ingredient_id=c_id,
            energy_kcal_100g=res["kcal"],
            protein_g_100g=res["protein"],
            fat_g_100g=res["fat"],
            carbs_g_100g=res["carbs"]
        ))
        
        # C. Polityka dietetyczna
        db.merge(DietPolicy(
            ingredient_id=c_id,
            is_vegetarian_ok=res["is_vegetarian"],
            is_vegan_ok=res["is_vegan"],
            is_meat=res["is_meat"],
            is_fish=res["is_fish"],
            is_keto_ok=res["is_keto"]
        ))
        
        db.commit()
        print(f"✅ ZAPISANO: {res['name_pl']} (ID: {c_id})")

    except Exception as e:
        print(f"❌ Krytyczny błąd dla '{query}': {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    koncepty = [
        # --- POBRANE (ZAKOMENTOWANE) ---
        # "Mleko 2%", "Mleko 3.2%", "Jogurt naturalny", "Jogurt grecki", "Twaróg chudy", 
        # "Twaróg półtłusty", "Śmietana 12%", "Śmietana 18%", "Śmietanka 30%", "Masło", 
        # "Jajko kurze", "Ser żółty gouda", "Ser mozzarella", "Ser feta", "Ser parmesan",
        # "Pierś z kurczaka", "Udo z kurczaka", "Mięso mielone wołowe", "Mięso mielone wieprzowe", 
        # "Boczek wędzony", "Szynka konserwowa", "Polędwiczka wieprzowa", "Łosoś świeży", 
        # "Dorsz polędwica", "Tuńczyk w puszce", "Krewetki mrożone",
        # "Mąka pszenna t500", "Mąka pełnoziarnista", "Ryż biały", "Ryż basmati", 
        # "Kasza gryczana", "Kasza jaglana", "Kasza kuskus", "Płatki owsiane", 
        # "Makaron spaghetti", "Makaron penne", "Bułka tarta", "Soczewica czerwona", 
        # "Cieciorka w puszce", "Fasola biała w puszce",
        # "Oliwa z oliwek", "Olej rzepakowy", "Majonez", "Musztarda", "Ketchup", 
        # "Koncentrat pomidorowy", "Przecier pomidorowy passata", "Sos sojowy",
        # "Ziemniaki", "Cebula biała", "Czosnek", "Pomidory w puszce", "Kukurydza konserwowa", 
        # "Groszek konserwowy", "Awokado", "Banany", "Jabłka",
        # "Tofu naturalne", "Tofu wędzone", "Napój owsiany", "Napój migdałowy", 
        # "Granulat sojowy", "Tempeh",

        # --- NOWE KONCEPTY DO POBRANIA ---
        # Warzywa świeże
        #"Marchew", "Pietruszka korzeń", "Seler korzeń", "Por", "Papryka czerwona", 
        #"Cukinia", "Bakłażan", "Ogórek świeży", "Ogórek kiszony", "Kapusta biała", 
        #"Kapusta kiszona", "Brokuły", "Kalafior", "Szpinak świeży", "Rzodkiewka", 
        #"Sałata lodowa", "Pomidory świeże", "Pieczarki",

        # Owoce i Bakalie
        #"Cytryna", "Pomarańcza", "Borówki", "Truskawki mrożone", "Orzechy włoskie", 
        #"Orzechy nerkowca", "Migdały", "Pestki dyni", "Nasiona słonecznika", 
        #"Sezam", "Wiórki kokosowe", "Rodzynki", "Daktyle suszone", "Masło orzechowe",

        # Przyprawy i sypkie dodatki (AI wyliczy ich gęstość kcal)
        #"Cukier biały", "Cukier brązowy", "Miód pszczeli", "Erytrol", "Sól kuchenna", 
        #"Kakao ciemne", "Kawa mielona", "Herbata czarna", "Drożdże suszone", 
        #"Proszek do pieczenia", "Skrobia ziemniaczana", "Ocet jabłkowy",

        # Inne dodatki
        "Bulion warzywny", "Mleczko kokosowe", "Pesto bazyliowe", "Hummus klasyczny", 
        "Dżem truskawkowy", "Czekolada gorzka 70%", "Czekolada mleczna", "Twarożek sernikowy"
    ]
    
    print(f"🚀 Startuję drugą turę pobierania ({len(koncepty)} nowych produktów)...")
    for i, produkt in enumerate(koncepty, 1):
        # Pomijamy te, które mogłyby zostać w liście jako puste stringi lub zakomentowane
        if not produkt or produkt.startswith("#"): 
            continue
            
        print(f"[{i}/{len(koncepty)}] ", end="")
        fetch_generic_concept(produkt)
        time.sleep(3) 
    
    print("\n🎉 Druga tura zakończona!")