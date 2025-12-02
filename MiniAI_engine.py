# mini_ai_engine.py
# Generic recipe engine (no hard-coded dishes)

def generate_recipe_output(name: str, ingredients: dict, steps: list):
    """
    Generic formatter — works for ANY recipe user adds.
    Does NOT include static items like 'Chhole Bhature'.
    """

    recipe = {}
    recipe["name"] = name.strip().title() if name else "Recipe"
    recipe["ingredients"] = ingredients or {}
    recipe["steps"] = steps or []

    return recipe


def format_ingredients(raw_text: str) -> dict:
    """
    Convert multi-line user input into {ingredient: quantity} dict.
    Accepts ANY recipe, no presets.
    Example line: "Flour - 2 cups"
    """
    result = {}
    if not raw_text:
        return result

    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # split on first dash
        if "-" in line:
            item, qty = line.split("-", 1)
            result[item.strip()] = qty.strip()
        else:
            # lines without qty are also allowed
            result[line] = ""

    return result


def format_steps(raw_text: str) -> list:
    """
    Convert multi-line steps into a clean list.
    Works for all recipes.
    """
    if not raw_text:
        return []

    return [s.strip() for s in raw_text.split("\n") if s.strip()]