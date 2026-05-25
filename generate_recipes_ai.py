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
        #sniadania
        ("Klasyczna jajecznica na maśle ze szczypiorkiem", "śniadanie"),
        ("Owsianka z jabłkiem, cynamonem i orzechami włoskimi", "śniadanie"),
        ("Szakszuka z pomidorami i papryką", "śniadanie"),
        ("Tosty z awokado i jajkiem w koszulce", "śniadanie"),
        ("Naleśniki z twarogiem i musem truskawkowym", "śniadanie"),
        ("Jaglanka na mleku kokosowym z borówkami", "śniadanie"),
        ("Omlet ze szpinakiem i serem feta", "śniadanie"),
        ("Kanapki z wędzonym łososiem, serkiem i koperkiem", "śniadanie"),
        ("Placuszki jogurtowe (pancakes) z syropem klonowym", "śniadanie"),
        ("Domowa granola z jogurtem greckim", "śniadanie"),
        ("Jajka na miękko z rzodkiewką i chrupiącą bułką", "śniadanie"),
        ("Tosty francuskie na słodko z malinami", "śniadanie"),
        ("Kanapki z domową pastą jajeczną", "śniadanie"),
        ("Wytrawne gofry z jajkiem sadzonym i boczkiem", "śniadanie"),
        ("Pieczona owsianka z bananem i czekoladą", "śniadanie"),
        ("Jajka zapiekane w połówkach awokado", "śniadanie"),
        ("Kasza manna na mleku z sokiem malinowym", "śniadanie"),
        ("Kanapki z hummusem i pieczoną papryką", "śniadanie"),
        ("Frittata z cukinią i pomidorkami koktajlowymi", "śniadanie"),
        ("Placuszki bananowe z płatkami owsianymi (bez mąki)", "śniadanie"),
        ("Twarożek ze śmietaną, rzodkiewką i szczypiorkiem", "śniadanie"),
        ("Jajka po benedyktyńsku z sosem holenderskim", "śniadanie"),
        ("Płatki kukurydziane na mleku", "śniadanie"),
        ("Wrap śniadaniowy z jajecznicą i szynką", "śniadanie"),
        ("Kanapki z pastą z tuńczyka", "śniadanie"),
        ("Szybki koktajl owsiany z bananem i masłem orzechowym", "śniadanie"),
        ("Tosty z mozzarellą, pomidorem i bazylią", "śniadanie"),
        ("Kasza gryczana na słodko z migdałami", "śniadanie"),
        ("Jajka po wiedeńsku w szklance", "śniadanie"),
        ("Bułka grahamka z masłem orzechowym i dżemem", "śniadanie"),
        # obiady
        ("Tradycyjny kotlet schabowy z ziemniakami i mizerią", "obiad"),
        ("Spaghetti Bolognese z parmezanem", "obiad"),
        ("Pieczony łosoś z kuskusem i brokułem", "obiad"),
        ("Kurczak curry z mleczkiem kokosowym i ryżem jaśminowym", "obiad"),
        ("Pierogi ruskie ze śmietaną i cebulką", "obiad"),
        ("Zupa pomidorowa z makaronem", "obiad"),
        ("Gulasz wołowy z kaszą gryczaną", "obiad"),
        ("Polędwiczki wieprzowe w sosie grzybowym", "obiad"),
        ("Makaron penne z kurczakiem, pesto i pomidorkami", "obiad"),
        ("Pieczone udka kurczaka z batatami", "obiad"),
        ("Zupa krem z dyni z pestkami słonecznika", "obiad"),
        ("Dorsz pieczony z warzywami korzeniowymi", "obiad"),
        ("Kotlety mielone z purée i buraczkami", "obiad"),
        ("Placki ziemniaczane z sosem pieczarkowym", "obiad"),
        ("Risotto z pieczarkami i białym winem", "obiad"),
        ("Naleśniki zapiekane ze szpinakiem i serem feta", "obiad"),
        ("Leczo z kiełbasą, cukinią i papryką", "obiad"),
        ("Tradycyjny rosół z kury z makaronem", "obiad"),
        ("Krewetki na maśle czosnkowym z bagietką", "obiad"),
        ("Lasagne mięsna z sosem beszamelowym", "obiad"),
        ("Żeberka wieprzowe pieczone w sosie BBQ", "obiad"),
        ("Gołąbki w sosie pomidorowym", "obiad"),
        ("Zupa ogórkowa z ziemniakami", "obiad"),
        ("Makaron carbonara z boczkiem (bez śmietany)", "obiad"),
        ("Gnocchi w sosie serowym z kurczakiem", "obiad"),
        ("Pulpety drobiowe w sosie koperkowym z kaszą jaglaną", "obiad"),
        ("Bitki wołowe w sosie własnym", "obiad"),
        ("Tofu w sosie słodko-kwaśnym z ryżem basmati", "obiad"),
        ("Zapiekanka ziemniaczana z mięsem mielonym", "obiad"),
        ("Kaczka pieczona z jabłkami i żurawiną", "obiad"),

        # lunche
        ("Sałatka Cezar z pieczonym kurczakiem i grzankami", "lunch"),
        ("Wrap z kurczakiem, sałatą i sosem czosnkowym", "lunch"),
        ("Lunchbox: komosa ryżowa, pieczony batat i ciecierzyca", "lunch"),
        ("Kanapka klubowa (Club Sandwich) z kurczakiem i bekonem", "lunch"),
        ("Sałatka z tuńczykiem, jajkiem i czarnymi oliwkami", "lunch"),
        ("Tortilla z hummusem i pieczonymi warzywami", "lunch"),
        ("Buddha bowl z tofu, ryżem i warzywami", "lunch"),
        ("Szybki Pad Thai z makaronem ryżowym", "lunch"),
        ("Zupa krem z pomidorów z grzankami", "lunch"),
        ("Sałatka grecka z oryginalną fetą i oliwkami", "lunch"),
        ("Quesadilla z kurczakiem, kukurydzą i serem", "lunch"),
        ("Kanapka z szarpaną wieprzowiną (Pulled Pork) i ogórkiem", "lunch"),
        ("Sałatka z makaronem penne, kurczakiem i pesto", "lunch"),
        ("Bowl: ryż, pieczony łosoś, awokado i sos sojowy", "lunch"),
        ("Bagietka z mozzarellą, pomidorem i rukolą", "lunch"),
        ("Wrap z wędzonym łososiem, serkiem i szpinakiem", "lunch"),
        ("Sałatka z kaszy bulgur, granatu i natki pietruszki (Tabbouleh)", "lunch"),
        ("Omlet na zimno w postaci rolady ze szpinakiem", "lunch"),
        ("Spring rollsy ze świeżymi warzywami i sosem orzechowym", "lunch"),
        ("Włoska zupa minestrone", "lunch"),
        ("Kanapka z pastą z awokado, pomidorem i jajkiem", "lunch"),
        ("Kawałek tarty ze szpinakiem i łososiem", "lunch"),
        ("Makaron z sosem pomidorowym podawany na zimno jako sałatka", "lunch"),
        ("Tosty z szynką, serem i musztardą (Croque Monsieur)", "lunch"),
        ("Poke bowl z marynowanym łososiem i mango", "lunch"),
        ("Półpita falafel z sosem jogurtowym", "lunch"),
        ("Sałatka z pieczonym burakiem, fetą i orzechami", "lunch"),
        ("Naleśniki na słono z szynką i serem (krokiety)", "lunch"),
        ("Ryż smażony z jajkiem, groszkiem i marchewką", "lunch"),
        ("Ciabatta z pieczonym kurczakiem i suszonymi pomidorami", "lunch"),

        #kolacje
        ("Sałatka Caprese z pomidorami i mozzarellą", "kolacja"),
        ("Placki z cukinii z sosem jogurtowo-koperkowym", "kolacja"),
        ("Bruschetta z pomidorami, czosnkiem i bazylią", "kolacja"),
        ("Jajka sadzone ze szparagami i masłem", "kolacja"),
        ("Pieczone warzywa korzeniowe z pokruszoną fetą", "kolacja"),
        ("Kanapki z domową pastą z makreli", "kolacja"),
        ("Krem z białych warzyw (kalafior, pietruszka)", "kolacja"),
        ("Szakszuka ze szpinakiem i czosnkiem (zielona szakszuka)", "kolacja"),
        ("Roladki z bakłażana z serkiem czosnkowym", "kolacja"),
        ("Twarożek na słono z rzodkiewką i chlebem żytnim", "kolacja"),
        ("Sałatka z roszponki, gruszki i sera z niebieską pleśnią", "kolacja"),
        ("Jajko w koszulce na grzance z guacamole", "kolacja"),
        ("Ryba (dorsz/mintaj) pieczona w folii z cytryną i ziołami", "kolacja"),
        ("Sałatka z wędzonym kurczakiem, ananasem i kukurydzą", "kolacja"),
        ("Frittata z pieczarkami i papryką", "kolacja"),
        ("Domowy hummus ze słupkami świeżych warzyw", "kolacja"),
        ("Klasyczne polskie zapiekanki z pieczarkami i serem na bagietce", "kolacja"),
        ("Zupa krem z brokułów z prażonymi płatkami migdałów", "kolacja"),
        ("Tatar ze śledzia z cebulką", "kolacja"),
        ("Kaszotto z kaszy jęczmiennej z grzybami leśnymi", "kolacja"),
        ("Ciepła sałatka z pieczonych batatów i ciecierzycy", "kolacja"),
        ("Naleśniki z mąki gryczanej z wędzonym łososiem", "kolacja"),
        ("Pasta z czerwonej soczewicy do chrupkiego pieczywa", "kolacja"),
        ("Omlet z suszonymi pomidorami i czarnymi oliwkami", "kolacja"),
        ("Tosty z kozim serem, miodem i orzechami", "kolacja"),
        ("Sałatka z ciecierzycą, tuńczykiem i czerwoną cebulą", "kolacja"),
        ("Tofu smażone w sosie sojowym z blanszowanymi brokułami", "kolacja"),
        ("Bułki grahamki z wędliną z piersi indyka i świeżym ogórkiem", "kolacja"),
        ("Niemiecka sałatka ziemniaczana z rzodkiewką i koperkiem", "kolacja"),
        ("Carpaccio z pieczonego buraka z rukolą i orzechami włoskimi", "kolacja"),

        # deserki
        ("Sernik na zimno z galaretką i truskawkami", "deser"),
        ("Klasyczna szarlotka z kruszonką", "deser"),
        ("Mocno czekoladowe brownie", "deser"),
        ("Tiramisu klasyczne z kawą i amaretto", "deser"),
        ("Panna cotta z musem z owoców leśnych", "deser"),
        ("Naleśniki na słodko z kremem czekoladowym i bananem", "deser"),
        ("Lody waniliowe z gorącymi malinami", "deser"),
        ("Klasyczne muffinki czekoladowe", "deser"),
        ("Tartaletki z owocami i kremem budyniowym", "deser"),
        ("Banoffee pie (ciasto bananowo-karmelowe na herbatnikach)", "deser"),
        ("Crème brûlée", "deser"),
        ("Domowy kisiel owocowy z jabłkami", "deser"),
        ("Budyń czekoladowy z wiórkami kokosowymi", "deser"),
        ("Galaretka wieloowocowa z kawałkami owoców", "deser"),
        ("Chrupiące ciasteczka owsiane z rodzynkami", "deser"),
        ("Sernik pieczony z brzoskwiniami z puszki", "deser"),
        ("Crumble (Owoce zapiekane pod kruszonką)", "deser"),
        ("Beza Pavlova z bitą śmietaną i truskawkami", "deser"),
        ("Ciasto marchewkowe z kremem sero-wym", "deser"),
        ("Malinowy mus w pucharku", "deser"),
        ("Gofry z bitą śmietaną, owocami i polewą czekoladową", "deser"),
        ("Szybkie ciasto jogurtowe z owocami leśnymi", "deser"),
        ("Ryż na mleku z cynamonem i jabłkami", "deser"),
        ("Fondant czekoladowy (lawa cake)", "deser"),
        ("Kulki mocy z daktyli, kakao i orzechów", "deser"),
        ("Pudding chia z mleczkiem kokosowym i puree z mango", "deser"),
        ("Torcik bezowy z kremem mascarpone", "deser"),
        ("Tradycyjny makowiec", "deser"),
        ("Truskawki zanurzane w gorzkiej czekoladzie", "deser"),
        ("Kogel-mogel", "deser"),

        # przekaski
        ("Nachosy z domowym guacamole", "przekąska"),
        ("Słupki z marchewki i selera z hummusem", "przekąska"),
        ("Chipsy z jarmużu z solą morską", "przekąska"),
        ("Mix prażonych orzechów i suszonych owoców", "przekąska"),
        ("Domowy popcorn maślany", "przekąska"),
        ("Oliwki marynowane w ziołach z kawałkami fety", "przekąska"),
        ("Mini pizzerinki na cieście francuskim", "przekąska"),
        ("Ślimaczki z ciasta francuskiego z szynką i serem", "przekąska"),
        ("Koreczki z serem, szynką i winogronem", "przekąska"),
        ("Bruschetta z tapenadą z czarnych oliwek", "przekąska"),
        ("Jajka faszerowane pieczarkami i natką pietruszki", "przekąska"),
        ("Mini pizzerki z krążków cukinii", "przekąska"),
        ("Kulki serowe obtaczane w ziołach i orzechach", "przekąska"),
        ("Prażona ciecierzyca w ostrej papryce", "przekąska"),
        ("Klasyczna deska serów z krakersami", "przekąska"),
        ("Plasterki jabłka smarowane masłem orzechowym", "przekąska"),
        ("Domowe batoniki musli", "przekąska"),
        ("Roladki z tortilli z serkiem kanapkowym i łososiem", "przekąska"),
        ("Kabanosy i kuleczki mini mozzarelli", "przekąska"),
        ("Kruche ciasteczka serowe", "przekąska"),
        ("Tosty z hummusem i czarnuszką", "przekąska"),
        ("Edamame (gotowana soja) z grubą solą morską", "przekąska"),
        ("Paluchy czosnkowe z ciasta drożdżowego", "przekąska"),
        ("Seler naciowy z kremowym serkiem i szczypiorkiem", "przekąska"),
        ("Wytrawne muffiny ze szpinakiem i serem feta", "przekąska"),
        ("Mini kanapki z pumpernikla z łososiem", "przekąska"),
        ("Faszerowane pomidorki koktajlowe (serek + zioła)", "przekąska"),
        ("Słone precle z dipem musztardowo-miodowym", "przekąska"),
        ("Pieczarki faszerowane serem i zapiekane", "przekąska"),
        ("Tostadas (chrupiące tortille) z pastą z czerwonej fasoli", "przekąska")
    ]
    
    print("Uruchamiam generator przepisów...")
    for nazwa_dania, kategoria in przepisy_do_wygenerowania:
        generate_recipe_with_ai(nazwa_dania, kategoria, ingredient_map)
        time.sleep(1.5) 
    
    print("\n--------Operacja zakończona--------")