import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import func
from core.database import SessionLocal, Ingredient, Nutrient, DietPolicy

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_next_concept_id(db) -> str:
    """
    Znajduje najwyższe ID w formacie 'C000' i generuje kolejne.

    Funkcja przeszukuje tabelę składników pod kątem identyfikatorów 
    zaczynających się od litery 'C'. Po znalezieniu najwyższej wartości 
    (na czas pisania skryptu - 'C047'), inkrementuje ją i zwraca w odpowiednim formacie.

    Args:
        db (Session): Aktywna sesja bazy danych SQLAlchemy.

    Returns:
        str: Nowy, unikalny identyfikator, np. 'C048'.
             Jeśli baza jest pusta, zwraca 'C001'.
    """
    max_id_str = db.query(func.max(Ingredient.id)).filter(Ingredient.id.like('C%')).scalar()
    
    if max_id_str:
        try:
            num = int(max_id_str[1:])
            return f"C{num + 1:03d}" 
        except ValueError:
            pass
            
    return "C001"

def generate_concept_with_ai(query: str) -> None:
    """
    Generuje dane dietetyczne dla podanego konceptu używając LLM i zapisuje je w bazie.

    Funkcja najpierw sprawdza, czy składnik o podanej nazwie już istnieje. 
    Jeśli nie, wysyła zapytanie do modelu OpenAI w celu wygenerowania 
    wartości odżywczych (makro) oraz flag dietetycznych (wegańskie, keto itp.).
    Na koniec zapisuje utworzone obiekty w relacyjnej bazie danych.

    Args:
        query (str): Nazwa ogólnego produktu spożywczego

    Returns:
        None: Funkcja nie zwraca danych, jej efektem jest zapis w bazie
    """
    db = SessionLocal()
    try:
        existing = db.query(Ingredient).filter(func.lower(Ingredient.name_pl) == query.lower()).first()
        if existing:
            print(f"Koncept '{query}' już istnieje w bazie (ID: {existing.id}). Pomijam.")
            return

        print(f"\nAI generuje koncept: '{query}'...")
        
        prompt = f"""
        Jesteś zaawansowanym asystentem dietetycznym. Tworzysz uśredniony koncept produktu spożywczego dla hasła: "{query}".
        
        Zwróć TYLKO czysty obiekt JSON (bez znaczników markdown typu ```json):
        {{
            "name_pl": "{query.capitalize()}",
            "kcal": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbs": 0.0,
            "is_vegetarian": 1,
            "is_vegan": 0,
            "is_meat": 0,
            "is_fish": 0,
            "is_keto": 0
        }}
        """
        
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[{"role": "user", "content": prompt}]
        )
        res = json.loads(ai_response.choices[0].message.content)

        c_id = get_next_concept_id(db)
        
        db.add(Ingredient(id=c_id, name_pl=res["name_pl"]))
        db.flush() 

        db.add(Nutrient(
            ingredient_id=c_id,
            energy_kcal_100g=res["kcal"],
            protein_g_100g=res["protein"],
            fat_g_100g=res["fat"],
            carbs_g_100g=res["carbs"]
        ))
        
        db.add(DietPolicy(
            ingredient_id=c_id,
            is_vegetarian_ok=res["is_vegetarian"],
            is_vegan_ok=res["is_vegan"],
            is_meat=res["is_meat"],
            is_fish=res["is_fish"],
            is_keto_ok=res["is_keto"]
        ))
        
        db.commit()
        print(f"ZAPISANO: {res['name_pl']} (Dostał ID: {c_id})")

    except Exception as e:
        print(f"Błąd podczas generowania '{query}': {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    nowe_koncepty = [
        # --- MĄKI I PIECZYWO ---
        "Mąka pszenna typ 450", "Mąka pszenna typ 500", "Mąka pszenna pełnoziarnista", 
        "Mąka żytnia", "Mąka orkiszowa", "Mąka gryczana", "Mąka ryżowa", 
        "Mąka kukurydziana", "Mąka ziemniaczana", "Chleb pszenny", "Chleb żytni na zakwasie", 
        "Chleb tostowy", "Bułka kajzerka", "Bagietka francuska", "Tortilla pszenna", 
        "Tortilla kukurydziana", "Pumpernikiel", "Bułka tarta",

        # --- KASZE, RYŻE, MAKARONY ---
        "Ryż biały", "Ryż brązowy", "Ryż jaśminowy", "Ryż basmati", "Ryż arborio", 
        "Ryż paraboliczny", "Kasza gryczana palona", "Kasza gryczana niepalona", 
        "Kasza jaglana", "Kasza jęczmienna wiejska", "Kasza pęczak", "Kasza kuskus", 
        "Kasza bulgur", "Komosa ryżowa", "Amarantus", "Makaron pszenny świderki", 
        "Makaron spaghetti", "Makaron penne", "Makaron pełnoziarnisty", "Makaron ryżowy", 
        "Makaron sojowy", "Makaron gryczany soba", "Makaron udon", "Płatki owsiane górskie", 
        "Płatki owsiane błyskawiczne", "Płatki jaglane", "Płatki kukurydziane", "Musli",

        # --- NABIAŁ I JAJA ---
        "Mleko krowie 3.2%", "Mleko krowie 2%", "Mleko krowie 0.5%", "Mleko bez laktozy", 
        "Jogurt naturalny", "Jogurt grecki", "Jogurt skyr", "Kefir", "Maślanka", 
        "Śmietana 12%", "Śmietana 18%", "Śmietanka 30%", "Śmietanka 36%", "Masło ekstra 82%", 
        "Masło klarowane ghee", "Ser żółty gouda", "Ser żółty edamski", "Ser cheddar", 
        "Ser parmezan", "Ser grana padano", "Ser mozzarella w zalewie", "Ser mozzarella żółta", 
        "Ser feta", "Ser halloumi", "Ser camembert", "Ser brie", "Ser gorgonzola", 
        "Twaróg chudy", "Twaróg półtłusty", "Twaróg tłusty", "Serek wiejski", 
        "Serek śmietankowy typu philadelphia", "Mascarpone", "Ricotta", 
        "Jajko kurze klasa M", "Jajko przepiórcze",

        # --- MIĘSO I DRÓB ---
        "Pierś z kurczaka", "Udo z kurczaka bez kości", "Skrzydła z kurczaka", 
        "Wątróbka drobiowa", "Pierś z indyka", "Mięso mielone z indyka", "Wołowina mielona", 
        "Rostbef wołowy", "Polędwica wołowa", "Antrykot wołowy", "Polędwiczka wieprzowa", 
        "Schab wieprzowy", "Karkówka wieprzowa", "Żeberka wieprzowe", "Mięso mielone wieprzowe", 
        "Boczek surowy", "Boczek wędzony", "Szynka wieprzowa surowa", "Szynka parmeńska", 
        "Szynka konserwowa", "Kiełbasa śląska", "Kiełbasa krakowska sucha", "Kabanosy wieprzowe", 
        "Kabanosy drobiowe", "Salami", "Pasztet pieczony", "Parówki wieprzowe", "Parówki z kurczaka",

        # --- RYBY I OWOCE MORZA ---
        "Łosoś świeży", "Łosoś wędzony na zimno", "Łosoś wędzony na gorąco", "Dorsz filet", 
        "Mintaj filet", "Morszczuk filet", "Halibut świeży", "Pstrąg tęczowy świeży", 
        "Dorada świeża", "Makrela wędzona", "Śledź w oleju", "Śledź w occie", 
        "Tuńczyk w sosie własnym", "Tuńczyk w oleju", "Sardynki w oleju", 
        "Szprotki w sosie pomidorowym", "Krewetki tygrysie", "Kalmary", "Małże", "Ośmiornica",

        # --- WARZYWA ŚWIEŻE ---
        "Ziemniaki", "Bataty", "Marchew", "Pietruszka korzeń", "Seler korzeń", "Por", 
        "Cebula biała", "Cebula czerwona", "Cebula szalotka", "Czosnek", "Burak ćwikłowy", 
        "Kapusta biała", "Kapusta czerwona", "Kapusta pekińska", "Kapusta włoska", "Kalafior", 
        "Brokuł", "Brukselka", "Kalarepa", "Szparagi zielone", "Szparagi białe", "Cukinia", 
        "Bakłażan", "Dynia hokkaido", "Dynia piżmowa", "Papryka czerwona", "Papryka żółta", 
        "Papryka zielona", "Ogórek szklarniowy", "Ogórek gruntowy", "Pomidor malinowy", 
        "Pomidorki koktajlowe", "Rzodkiewka", "Sałata masłowa", "Sałata lodowa", "Roszponka", 
        "Rukola", "Szpinak świeży", "Jarmuż", "Koper świeży", "Natka pietruszki", "Szczypiorek", "Bazylia świeża",

        # --- WARZYWA PRZETWORZONE I KONSERWOWE ---
        "Ogórki kiszone", "Ogórki konserwowe", "Kapusta kiszona", "Pomidory w puszce pelati", 
        "Przecier pomidorowy passata", "Koncentrat pomidorowy", "Suszone pomidory w oleju", 
        "Kukurydza konserwowa", "Groszek konserwowy", "Fasola czerwona w puszce", 
        "Fasola biała w puszce", "Ciecierzyca w puszce", "Soczewica w puszce", "Oliwki czarne", 
        "Oliwki zielone", "Kapary", "Papryka konserwowa", "Jalapeno marynowane",

        # --- OWOCE ŚWIEŻE ---
        "Jabłko", "Gruszka", "Banan", "Pomarańcza", "Mandarynka", "Grejpfrut", "Cytryna", 
        "Limonka", "Truskawki", "Maliny", "Borówka amerykańska", "Jagody", "Jeżyny", "Wiśnie", 
        "Czereśnie", "Śliwki", "Brzoskwinia", "Nektarynka", "Morela", "Winogrona jasne", 
        "Winogrona ciemne", "Arbuz", "Melon", "Kiwi", "Mango", "Papaja", "Ananas świeży", "Granat", "Figi świeże",

        # --- OWOCE SUSZONE, PUSZKI I BAKALIE ---
        "Rodzynki", "Żurawina suszona", "Morele suszone", "Śliwki suszone", "Figi suszone", 
        "Daktyle suszone", "Brzoskwinie w syropie", "Ananas w syropie", "Orzechy włoskie", 
        "Orzechy laskowe", "Orzechy nerkowca", "Orzechy ziemne", "Orzechy makadamia", 
        "Orzechy brazylijskie", "Orzechy pekan", "Migdały", "Płatki migdałowe", "Pistacje", 
        "Pestki dyni", "Ziarna słonecznika", "Nasiona chia", "Siemię lniane", "Sezam jasny", 
        "Sezam czarny", "Mak", "Wiórki kokosowe",

        # --- TŁUSZCZE ---
        "Oliwa z oliwek extra virgin", "Olej rzepakowy", "Olej słonecznikowy", "Olej kokosowy", 
        "Olej lniany", "Olej sezamowy", "Olej z awokado", "Smalec wieprzowy", "Margaryna",

        # --- STRĄCZKI I ZAMIENNIKI ROŚLINNE ---
        "Soczewica czerwona sucha", "Soczewica zielona sucha", "Ciecierzyca sucha", 
        "Fasola piękny jaś", "Groch łuskany", "Tofu naturalne", "Tofu wędzone", 
        "Tofu marynowane", "Tempeh", "Kostka sojowa", "Granulat sojowy", "Napój sojowy", 
        "Napój owsiany", "Napój migdałowy", "Napój kokosowy", "Mleczko kokosowe w puszce", 
        "Jogurt sojowy", "Płatki drożdżowe nieaktywne",

        # --- SOSY I PRZYPRAWY PŁYNNE ---
        "Majonez", "Ketchup", "Musztarda sarepska", "Musztarda dijon", "Sos sojowy jasny", 
        "Sos sojowy ciemny", "Sos teriyaki", "Sos rybny", "Sos ostrygowy", "Sos sriracha", 
        "Sos tabasco", "Ocet spirytusowy", "Ocet jabłkowy", "Ocet winny", "Ocet balsamiczny", 
        "Pesto zielone", "Pesto czerwone", "Pasta curry czerwona", "Pasta curry zielona", 
        "Pasta tahini", "Masło orzechowe 100%",

        # --- SŁODYCZE, WYPIEKI, DODATKI SYPKIE ---
        "Cukier biały", "Cukier trzcinowy", "Cukier puder", "Ksylitol", "Erytrytol", 
        "Miód pszczeli", "Syrop klonowy", "Syrop z agawy", "Kakao gorzkie", 
        "Czekolada gorzka 70%", "Czekolada mleczna", "Czekolada biała", "Krem orzechowo-czekoladowy", 
        "Dżem truskawkowy", "Konfitura malinowa", "Powidła śliwkowe", "Żelatyna", "Agar-agar", 
        "Proszek do pieczenia", "Soda oczyszczona", "Ekstrakt waniliowy", "Cukier wanilinowy", 
        "Drożdże świeże", "Drożdże suszone instant",

        # --- PRZYPRAWY SUCHE ---
        "Sól morska", "Pieprz czarny mielony", "Papryka słodka mielona", "Papryka ostra mielona", 
        "Papryka wędzona", "Czosnek granulowany", "Cebula suszona", "Oregano suszone", 
        "Bazylia suszona", "Tymianek suszony", "Rozmaryn suszony", "Majeranek", 
        "Zioła prowansalskie", "Cynamon mielony", "Imbir mielony", "Kurkuma mielona", 
        "Kmin rzymski kumin", "Kolendra mielona", "Gałka muszkatołowa", "Goździki", 
        "Kardamon", "Liść laurowy", "Ziele angielskie"
    ]
    
    print("Uruchamiam generator...")
    for produkt in nowe_koncepty:
        generate_concept_with_ai(produkt)
        time.sleep(1) 
    
    print("\nOperacja zakończona!")