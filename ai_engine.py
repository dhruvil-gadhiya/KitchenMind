# ai_engine.py
import random
import difflib
from recipes_data import RECIPES
from utils_scaling import scale_ingredients
from typing import List, Dict, Optional

# (keep your existing COMMON_ING_DESCRIPTIONS, GOOD_MESSAGES, FUNNY_LINE_TEMPLATES,
# _generate_funny_lines, _ingredient_description, _expand_step unchanged)
# I'll paste them here exactly as before from your final code to keep behavior identical.

COMMON_ING_DESCRIPTIONS = {
    "besan": "chickpea flour used in many Indian snacks — gives a nutty, dense texture.",
    "semolina": "coarse durum wheat flour (rava) that gives body and slight bite.",
    "sugar": "sweetener; adjust to taste.",
    "lemon": "fresh lemon juice adds acidity and freshness.",
    "eno": "fruit salt used to aerate batter just before steaming.",
    "salt": "enhances flavors; add to taste.",
    "turmeric": "earthy spice used for color and mild flavor.",
    "water": "to bind the batter/dough; quantity may vary slightly.",
    "dosa batter": "fermented rice & lentil batter, ready-to-cook.",
    "oil": "neutral cooking oil.",
    "potato": "starchy vegetable; usually boiled and mashed.",
    "tomato": "adds tangy sweetness when cooked down.",
    "onion": "adds savory sweetness and body when sautéed.",
    "rice": "long-grain rice typically used in biryani.",
    "mixed vegetables": "a mix of seasonal vegetables, chopped.",
    "cheese": "melting cheese for pizzas (e.g., mozzarella).",
    "bread slices": "regular sandwich bread slices.",
    "maida": "all-purpose wheat flour.",
    "peas": "fresh or frozen peas to add texture and sweetness.",
    "ghee": "clarified butter, adds rich flavor."
}

GOOD_MESSAGES = [
    "Enjoy your meal! 🍽️😋",
    "Bon appétit — hope it tastes amazing! 🌟🍛",
    "Dig in and enjoy every bite! 😄🍴",
    "Serve hot and smile big! 🔥😀",
    "Happy cooking — you nailed it! 🧑‍🍳👏",
    "Wishing you tasty bites and happy vibes! 😋✨",
    "Eat well, smile often! 😊🍲",
    "Hope your dish brings joy to your table! 💛🍽️",
    "Good food = good mood. Enjoy! 😌🍕",
    "Flavor time! Enjoy the deliciousness! 🤤🎉",
    "Here's to a perfect meal and a happy heart! ❤️🍛",
    "Celebrate with a good bite! 🎊🍽️",
    "Hope this dish brightens your day! 🌞🍲",
    "Taste, smile, repeat! 😀🍴",
    "Food made with love always tastes better! 💖🍳",
    "Your plate is ready for greatness! 🌟🍛",
    "Take a bite and enjoy the moment! ⏳😋",
    "Wishing you warm food and warm smiles! 😊🔥",
    "May every bite be full of joy! 😄🍽️",
    "Enjoy your delicious creation! 🔥🤩"
]

FUNNY_LINE_TEMPLATES = [
    "If {dish} had a fan club, I'd be the president! 🤩👑",
    "{dish}: the reason forks walk with confidence. 🍴😎",
    "Caution: {dish} may cause extreme happiness. 😂🔥",
    "Leftovers of {dish}? More like tomorrow’s treasure. 🏴‍☠️🍲",
    "{dish} is basically edible therapy. 🍽️🧠💖",
    "If hugs were food, they’d taste like {dish}. 🤗🍛",
    "{dish} is so good, even the calories clap for it. 👏😂",
    "Pro tip: eat {dish}, become unstoppable. 💪😄",
    "{dish} + you = a perfect love story. 💘🍕",
    "One bite of {dish} can fix almost anything. 🛠️😄",
    "{dish} is proof that magic exists. ✨🪄",
    "Today’s vibe: {dish} and zero stress. 😌🍛",
    "Breaking: {dish} officially voted 'Best Life Decision'. 🗳️🍲",
    "Craving {dish}? Congratulations, you have great taste. 😎🍕",
    "{dish} — because happiness starts in the kitchen. 🧑‍🍳💛",
    "{dish} is basically a warm handshake for your taste buds. 🤝😋"
]

def _generate_funny_lines(dish_name: str):
    """Return a list of 10 unique funny lines for a dish (randomized)."""
    lines = []
    base = dish_name.title()
    for i in range(10):
        tmpl = FUNNY_LINE_TEMPLATES[i % len(FUNNY_LINE_TEMPLATES)]
        twist = ""
        if random.random() < 0.25:
            twist = " (eat responsibly!)"
        lines.append(tmpl.format(dish=base) + twist)
    random.shuffle(lines)
    return lines

def _ingredient_description(item_name: str):
    key = item_name.lower()
    if "(" in key:
        key = key.split("(")[0].strip()
    for k, desc in COMMON_ING_DESCRIPTIONS.items():
        if k in key:
            return desc
    return f"{item_name.split('(')[0].strip()} — a common ingredient used to build flavor and texture."

def _expand_step(step_text: str, dish_name: str, serving: int):
    st = step_text.lower().strip()
    dish = dish_name.title()
    if "mix" in st and "dry" in st:
        return ("Combine all dry ingredients in a large bowl. Sift together to remove lumps "
                "and ensure even distribution — this helps the final texture be uniform. "
                "If using spices, grind them fresh for best aroma.")
    if "mix" in st and "add" in st:
        return ("Gently combine the wet and dry components until a homogenous batter or dough forms. "
                "Avoid overmixing where aeration isn't desired; use a spatula to scrape the sides and fold until smooth.")
    if "add water" in st:
        return ("Slowly add water while stirring continuously so the mixture doesn't form lumps. "
                "Stop when you reach the consistency described in the recipe (usually a pourable batter or soft dough).")
    if "eno" in st or "add eno" in st:
        return ("Just before steaming or cooking, sprinkle the Eno (fruit salt) evenly over the batter and fold gently. "
                "You'll notice immediate bubbling — this is how the dish becomes light and fluffy. Transfer quickly for steaming.")
    if "steam" in st:
        return ("Pour the batter into a greased mould or tray and steam in a preheated steamer for the recommended time "
                "until a toothpick inserted into the center comes out clean. Let it rest for a few minutes before unmolding.")
    if "tempering" in st or "tempering on top" in st:
        return ("Prepare a tempering: heat oil/ghee, add mustard seeds, curry leaves, mustard, and any other whole spices until they pop. "
                "Pour this sizzling tempering over the cooked dish for aroma and a flavor boost.")
    if "heat pan" in st or "heat the pan" in st:
        return ("Heat a non-stick or cast-iron tawa over medium heat until it's just hot. A drop of water should sizzle and evaporate.")
    if "spread batter" in st:
        return ("Pour a ladleful of batter onto the hot tawa and spread it out in a circular motion to the desired thinness. "
                "Cook until the bottom turns golden and crisp before flipping if needed.")
    if "cook both sides" in st:
        return ("Cook until each side is nicely browned and crisp edges form. Keep heat medium to avoid burning; drizzle oil where needed.")
    if "boil" in st and "vegetables" in st:
        return ("Boil the vegetables until fork-tender but not mushy. Drain and mash as required for the recipe — reserve some for texture.")
    if "mash" in st:
        return ("Mash the cooked vegetables with a sturdy masher to your preferred texture — some like it chunky, some prefer smooth. "
                "Adjust seasoning after mashing.")
    if "layer" in st or "layer rice" in st:
        return ("Layer the cooked rice and vegetables/meat alternately in a heavy-bottomed pot. Sprinkle fried onions, herbs, and warmed spices between layers.")
    if "steam cook" in st or "dum" in st:
        return ("Seal the pot with a tight lid (or cover with dough) and cook on low heat to allow flavors to meld and finish cooking gently.")
    if "spread sauce" in st or "add toppings" in st or "add cheese" in st:
        return ("Spread an even layer of tomato sauce on the base, arrange toppings to your liking, and finish with plenty of cheese. Bake in a preheated oven until crust is golden and cheese is bubbling.")
    if "fry" in st or "shape" in st:
        return ("Carefully shape and shallow- or deep-fry until golden and crisp. Maintain oil temperature to prevent soggy results.")
    return (f"{step_text}. Do this carefully: use medium heat, taste and adjust seasoning as you go, "
            f"and make sure the final texture suits your preference. For {dish}, follow this step patiently for best results.")

def _find_matches(dish_lower: str, recipes_list: List[Dict]):
    """
    Returns list of recipe dicts that match the dish_lower string.
    Matching order:
      1) substring (case-insensitive)
      2) startswith
      3) close matches using difflib (against recipe names)
    """
    if not dish_lower:
        return []

    # 1) substring match
    substring_matches = [r for r in recipes_list if dish_lower in (r.get("name","").lower())]
    if substring_matches:
        return substring_matches

    # 2) startswith match
    startswith_matches = [r for r in recipes_list if (r.get("name","").lower()).startswith(dish_lower)]
    if startswith_matches:
        return startswith_matches

    # 3) difflib close matches on recipe names
    names = [r.get("name","") for r in recipes_list]
    close = difflib.get_close_matches(dish_lower, [n.lower() for n in names], n=5, cutoff=0.6)
    if close:
        close_set = set(close)
        return [r for r in recipes_list if (r.get("name","").lower()) in close_set]

    return []

def generate_recipe(dish: str, servings: int, extra_recipes: Optional[List[Dict]] = None):
    """
    Generate recipe output using built-in RECIPES plus optional extra_recipes (user-saved).
    """
    dish_lower = (dish or "").lower().strip()
    recipes_all = list(RECIPES) + (list(extra_recipes) if extra_recipes else [])

    matches = _find_matches(dish_lower, recipes_all)

    if not matches:
        return {
            "name": dish.title() if dish else "Unknown",
            "serving_size": servings,
            "ingredients": {},
            "ingredients_detailed": {},
            "steps": ["Recipe not found."],
            "steps_detailed": ["We couldn't find a recipe matching that name. Try another search."],
            "funny_line": random.choice(_generate_funny_lines(dish or "Dish")),
            "good_message": random.choice(GOOD_MESSAGES)
        }

    # If multiple matches, pick the one with highest 'score' (default 1)
    best = max(matches, key=lambda r: r.get("score", 1))

    recipe = best

    factor = float(servings) / float(recipe.get("serving_size", 1))
    scaled_ing = scale_ingredients(recipe.get("ingredients", {}), factor)

    ingredients_detailed = {}
    for item, qty in scaled_ing.items():
        desc = _ingredient_description(item)
        qty_formatted = int(qty) if isinstance(qty, (int,)) or (isinstance(qty, float) and float(qty).is_integer()) else round(qty, 2)
        ingredients_detailed[item] = {
            "quantity": qty_formatted,
            "description": desc
        }

    steps = recipe.get("steps", [])
    steps_detailed = []
    for s in steps:
        steps_detailed.append(_expand_step(s, recipe.get("name", dish), servings))

    funny_lines = _generate_funny_lines(recipe.get("name", dish))
    funny_line = random.choice(funny_lines)
    good_message = random.choice(GOOD_MESSAGES)

    return {
        "name": recipe.get("name", dish),
        "serving_size": servings,
        "ingredients": scaled_ing,
        "ingredients_detailed": ingredients_detailed,
        "steps": steps,
        "steps_detailed": steps_detailed,
        "funny_line": funny_line,
        "good_message": good_message
    }
