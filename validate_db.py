from core.database import SessionLocal, Recipe

def validate_recipe_ingredients():
    db = SessionLocal()
    print("Rozpoczynam audyt tabeli 'recipes'...\n" + "="*60)
    
    anomalies_found = 0
    
    try:
        recipes = db.query(Recipe).all()
        
        for recipe in recipes:
            # Zabezpieczenie czy w ogóle jest jakakolwiek lista składników
            if not recipe.ingredients_data:
                continue
                
            issues = []
            
            # Przejscie przez każdy element na liście składników w danym przepisie
            for idx, item in enumerate(recipe.ingredients_data):
                # Czy to w ogóle jest słownik?
                if not isinstance(item, dict):
                    issues.append(f"Element [{idx}] nie jest słownikiem! Wartość: {item} (Typ: {type(item).__name__})")
                    continue
                    
                # Czy ma wymagane klucze?
                if "concept_id" not in item:
                    issues.append(f"Element [{idx}] brakuje klucza 'concept_id'. Obecne dane: {item}")
                
                if "grams" not in item:
                    issues.append(f"Element [{idx}] brakuje klucza 'grams'. Obecne dane: {item}")
                    
                # czy klucze mają sensowne typy? (gramy powinny być liczbą)
                if "grams" in item and not isinstance(item["grams"], (int, float)):
                    issues.append(f"Element [{idx}] klucz 'grams' nie jest liczbą: {item['grams']}")
            
            # jakiekolwiek błędy dla tego przepisu -> raport
            if issues:
                anomalies_found += 1
                print(f"ZNALEZIONO BŁĄD: ID {recipe.id} | {recipe.title_pl}")
                for issue in issues:
                    print(f"   -> {issue}")
                print("-" * 60)
                
        # Podsumowanie audytu
        print("="*60)
        if anomalies_found == 0:
            print("Baza jest idealnie czysta! Nie znaleziono żadnych błędów w strukturze składników.")
        else:
            print(f"Podsumowanie: Znaleziono anomalie w {anomalies_found} przepisach.")
            print("Otwórz pgAdmin, wyszukaj przepisy po powyższych ID i popraw JSONB ręcznie.")
            
    except Exception as e:
        print(f"Krytyczny błąd podczas skanowania bazy: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    validate_recipe_ingredients()