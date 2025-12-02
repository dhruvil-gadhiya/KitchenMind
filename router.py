# router.py
# Exposes a simple wrapper used by main.py to get recipe output.
from ai_engine import generate_recipe
from storage import load_user_recipes


def get_recipe_output(dish_name: str, servings: int):
    """
    Wrapper to call the AI engine. Loads user recipes and passes them as extras.
    Keeps main.py focused on routing.
    """
    if not dish_name:
        dish_name = ""
    try:
        servings_int = int(servings)
    except Exception:
        servings_int = 1

    user_recipes = load_user_recipes()
    return generate_recipe(dish_name, servings_int, extra_recipes=user_recipes)
