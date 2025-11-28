# router.py
# Exposes a simple wrapper used by mai.py to get recipe output.
from ai_engine import generate_recipe

def get_recipe_output(dish_name: str, servings: int):
    """
    Wrapper to call the AI engine. Kept separate so mai.py stays focused on routing.
    """
    if not dish_name:
        dish_name = ""
    try:
        servings_int = int(servings)
    except Exception:
        servings_int = 1
    return generate_recipe(dish_name, servings_int)
