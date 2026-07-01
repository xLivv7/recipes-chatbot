MEAL_CATEGORIES = {
    "śniadanie",
    "obiad",
    "lunch",
    "kolacja",
    "deser",
    "przekąska",
}

USER_PREFS = {
    "none",
    "vegetarian",
    "vegan",
    "meat",
    "fish",
    "pescetarian",
}

USER_PREF_ALIASES = {
    "vege": "vegetarian",
}

NUTRITION_GOALS = {
    "standard",
    "low_kcal",
    "high_protein",
    "keto",
}

CONDITION_TYPES = {
    "user_pref",
    "nutrition_goal",
    "default",
}

INGREDIENT_ID_PATTERN = r"^C\d{3,}$"
RECIPE_ID_PATTERN = r"^R\d{3,}$"

NUTRIENT_FIELDS = {
    "energy_kcal_100g": "kcal",
    "protein_g_100g": "protein",
    "fat_g_100g": "fat",
    "carbs_g_100g": "carbs",
}

SKU_NUTRIENT_FIELDS = {
    "energy_kcal_100": "kcal",
    "protein_g_100": "protein",
    "fat_g_100": "fat",
    "carbs_g_100": "carbs",
}
