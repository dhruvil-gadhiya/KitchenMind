# ai_engine.py
import random
import difflib
from recipes_data import RECIPES
from utils_scaling import scale_ingredients
from typing import List, Dict, Optional


def normalize_recipe(r):
    # 1. Fix serving_size key
    if "serving_size" not in r:
        if "servings" in r:
            r["serving_size"] = r["servings"]
        elif "persons" in r:
            r["serving_size"] = r["persons"]
        else:
            r["serving_size"] = 1  # fallback if missing

    # Ensure serving_size is numeric
    try:
        r["serving_size"] = float(r["serving_size"])
    except:
        r["serving_size"] = 1

    # 2. Fix ingredient quantities
    fixed_ing = {}
    for k, v in r.get("ingredients", {}).items():
        try:
            fixed_ing[k] = float(v)
        except:
            fixed_ing[k] = v  # allow text like "1 cup"
    r["ingredients"] = fixed_ing

    return r


# -----------------------------------------------------
# HIGH DETAIL INGREDIENT DESCRIPTIONS (YOURS + ADDED)
# -----------------------------------------------------
COMMON_ING_DESCRIPTIONS = {
    "besan": "finely ground gram/chickpea flour; rich in protein and gives dishes a nutty aroma, dense body, and crisp texture when fried.",
    "semolina": "coarse durum wheat granules (rava/sooji) used for structure; provides a firm bite and helps batter hold shape.",
    "sugar": "primary sweetener that also balances acidity and bitterness; quantity affects texture in syrups and desserts.",
    "lemon": "fresh citrus juice used for bright acidity; enhances flavors and helps balance richness.",
    "eno": "fast-acting fruit salt (sodium bicarbonate + citric acid); creates immediate aeration in batter for fluffy results.",
    "salt": "universal flavor enhancer; essential for balancing sweetness, acidity, and overall taste.",
    "turmeric": "earthy, mildly bitter root spice; used primarily for color, anti-inflammatory properties, and warm undertones.",
    "water": "primary liquid for hydration; affects consistency, dough elasticity, and cooking time.",
    "dosa batter": "fermented rice–urad dal batter; fermentation gives sourness, lightness, and characteristic crispness.",
    "oil": "neutral cooking fat used for sautéing, frying, or greasing; affects browning and moisture retention.",
    "potato": "starchy root vegetable that becomes soft and creamy when boiled; works as a natural thickener.",
    "tomato": "juicy, acidic fruit that adds tang, sweetness, and body when cooked down into a base.",
    "onion": "aromatic vegetable; caramelizes to bring sweetness and forms the backbone of many Indian gravies.",
    "rice": "long-grain basmati or other varieties; starch content and grain length influence fluffiness and aroma.",
    "mixed vegetables": "assortment of seasonal vegetables (carrot, beans, peas, corn); add nutrition, color, and texture variation.",
    "cheese": "melting cheese like mozzarella; adds stretch, creaminess, and mild savory flavor.",
    "bread slices": "refined or whole-wheat sandwich bread; absorbs fillings and toasts well for crisp texture.",
    "maida": "refined all-purpose flour; forms elastic gluten networks, ideal for breads, pastries, and thickening.",
    "peas": "sweet green legumes; add pop, color, and mild sweetness when cooked.",
    "ghee": "clarified butter with high smoke point; adds nutty aroma, richness, and authentic Indian depth.",

    # 20 NEW HIGH-QUALITY DESCRIPTIONS
    "curd": "fermented dairy with natural probiotics; adds tang, moisture, and tenderizes doughs/marinades.",
    "cumin seeds": "earthy, warm aromatic seeds; release nutty bitterness when tempered in hot oil.",
    "coriander powder": "ground coriander seeds; offers citrusy, warm notes that round out spice blends.",
    "garam masala": "blend of warming spices (cloves, cinnamon, cardamom); added at the end for aroma.",
    "green chilli": "fresh chillies adding sharp heat and brightness; flavor varies by variety.",
    "ginger": "pungent root with spicy heat; used to cut richness and enhance digestion.",
    "garlic": "strong aromatic; caramelizes into sweetness and forms flavor base with onions.",
    "curry leaves": "fragrant leaves with citrusy-spicy aroma; bloom when fried in oil.",
    "coconut": "fresh or desiccated; adds sweetness, creaminess, and coastal Indian flavor.",
    "mustard seeds": "pungent seeds that pop in hot oil; give a nutty, sharp flavor to tempering.",
    "kasuri methi": "dried fenugreek leaves; add aroma with slight bitterness and restaurant-style flavor.",
    "cardamom": "fragrant pod used in sweets and biryanis; adds floral, sweet notes.",
    "cloves": "strong, warming spice used sparingly for depth and aroma.",
    "cinnamon": "sweet woody spice; infuses warmth into gravies, biryanis, and desserts.",
    "bay leaf": "aromatic leaf releasing subtle herbal notes when simmered in curries or rice.",
    "milk": "provides creaminess and richness; also used to adjust consistency in sweets.",
    "cornflour": "fine starch used as thickener; gives glossy finish and binds mixtures.",
    "paneer": "fresh Indian cottage cheese; soft and mild, absorbs flavors while staying firm.",
    "mint": "cooling herb that lifts freshness; used in chutneys, biryani, and garnishing.",
    "coriander leaves": "fresh herb providing green, citrusy finish; added at the end for brightness."
}

# -----------------------------------------------------
# GOOD MESSAGES
# -----------------------------------------------------
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
    "Enjoy your delicious creation! 🔥🤩",
    "Hope every bite makes you happier! 😋💛",
    "Enjoy the flavors and the moment! 🍽️✨",
    "Savor it slow — you deserve it! 😌🍛",
    "Good food, good life — enjoy! 😄🍲",
    "May your meal be as awesome as you are! 🌟🍴",
    "Warm food, warm heart — enjoy! ❤️🔥",
    "Hope your taste buds have a great day! 😋🎉",
    "Time to feast and smile big! 😁🍽️",
    "May this dish bring joy to your soul! ✨😄",
    "Enjoy the magic on your plate! 🪄🍛",
    "Wishing you the sweetest bites today! 🍬😊",
    "Take a moment to enjoy the goodness! 😌🍴",
    "Here’s to good food and great vibes! 🎉🍲",
    "Hope your meal feels like a warm hug! 🤗🍛",
    "May your plate overflow with happiness! 😄🍽️",
    "Eat happily, live joyfully! 😊🌟",
    "Your tasty moment starts now — enjoy! 🤤🍴",
    "Hope your meal brings a smile to your heart! 💛😌",
    "Good food incoming — enjoy every second! 🚀🍛",
    "Wishing you the most delicious moment today! 🍽️✨",
    "Enjoy the taste, enjoy the day! 🌞😋",
    "A happy meal for a happy mood! 😀🍲",
    "Hope your plate is full and your heart fuller! ❤️🍽️",
    "Treat yourself to every tasty bite! 😋🌟",
    "May your meal be bursting with flavor! 💥🍛",
    "Enjoy your well-earned deliciousness! 😄🍴",
    "Good vibes and great food — enjoy! ✨🍽️",
    "May every flavor make your day brighter! 🌞😋",
    "Wishing you a meal that delights every bite! 🤩🍛",
    "Enjoy your tasty masterpiece! 👨‍🍳👏"
]

# -----------------------------------------------------
# FUNNY LINES
# -----------------------------------------------------
FUNNY_LINE_TEMPLATES = [
    "If {dish} had a fan club, I'd be the president! 🤩👑",
    "{dish}: the reason forks walk with confidence. 🍴😎",
    "Caution: {dish} may cause extreme happiness. 🍴🔥",
    "Leftovers of {dish}? More like tomorrow’s treasure. 🍴🍲",
    "{dish} is basically edible therapy. 🍽️🧠💖",
    "If hugs were food, they’d taste like {dish}. 🤗🍛",
    "{dish} is so good, even the calories clap for it. 👏😋",
    "Pro tip: eat {dish}, become unstoppable. 💪😄",
    "{dish} + you = a perfect love story. 💘🍴",
    "One bite of {dish} can fix almost anything. 🛠️😄",
    "{dish} is proof that magic exists. ✨🪄",
    "Today’s vibe: {dish} and zero stress. 😌🍛",
    "Breaking: {dish} officially voted 'Best Life Decision'. 🗳️🍲",
    "Craving {dish}? Congratulations, you have great taste. 😎🍴",
    "{dish} — because happiness starts in the kitchen. 🧑‍🍳💛",
    "{dish} is basically a warm handshake for your taste buds. 🤝😋",
    "{dish} is so good, it deserves its own national holiday. 🎉🍛",
    "Warning: {dish} may cause uncontrollable happy dancing. 💃😄",
    "If dreams had flavors, they'd taste like {dish}. 😴✨🍴",
    "Proof I'm winning at life? I'm eating {dish}. 😎🏆",
    "{dish} is my love language. 💕🍽️",
    "My therapist said, 'Find joy' — so I found {dish}. 😌🍲",
    "If {dish} was a person, I'd marry it. 💍😂",
    "Life is short, take a bigger bite of {dish}. 😋🍛",
    "Who needs motivation when you have {dish}? 🚀🍽️",
    "{dish}: because adulting is easier with good food. 🧑‍💼🍲",
    "Plot twist: {dish} makes everything better. 🔄😄",
    "{dish} doesn’t ask silly questions, {dish} understands. 🤝🍛",
    "My mood depends on how soon I get {dish}. ⏳😋",
    "{dish} is my superpower source. ⚡🍴",
    "Eating {dish} is my favorite form of self-care. 💆‍♂️🍽️",
    "If {dish} had a ringtone, it’d be pure happiness. 🎶😄",
    "Believe in yourself… and in the magic of {dish}. ✨🍛",
    "{dish} is the best wingman for any bad day. 🪽🍴",
    "Current status: emotionally supported by {dish}. 😌🍲",
    "{dish} — because life’s too short for boring food. 🎯😋",
    "Dear universe, send {dish}… and maybe some luck too. 🌌🍽️",
    "When in doubt, choose {dish}. It never disappoints. 💯🍛",
    "{dish} is the reason my smile is extra wide today. 😁🍲",
    "I followed my heart… it led me straight to {dish}. ❤️🍴",
    "Breaking news: {dish} reduces stress by 99%. (Scientifically delicious.) 📢😂🍛",
    "Not all heroes wear capes — some are called {dish}. 🦸‍♂️🍽️",
    "Me + {dish} = a relationship approved by destiny. 🔮💘",
    "If joy had a smell, it would be fresh {dish}. 👃😄",
    "Be right back, having a moment with {dish}. 😌🍛",
    "{dish} is basically happiness served on a plate. 😄🍽️"
]


def _generate_funny_lines(dish_name: str):
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

# -----------------------------------------------------
# INGREDIENT DESCRIPTION MATCHER
# -----------------------------------------------------
def _ingredient_description(item_name: str):
    key = item_name.lower()
    if "(" in key:
        key = key.split("(")[0].strip()
    for k, desc in COMMON_ING_DESCRIPTIONS.items():
        if k in key:
            return desc
    return f"{item_name.split('(')[0].strip()} — a common ingredient used to build flavor and texture."

# -----------------------------------------------------
# STEP EXPANSION LOGIC
# -----------------------------------------------------
def _expand_step(step_text: str, dish_name: str, serving: int):
    st = step_text.lower().strip()
    dish = dish_name.title()

    if "mix" in st and "dry" in st:
        return ("Combine all dry ingredients in a large bowl. Sift together to remove lumps "
                "and ensure even distribution — this helps texture stay uniform.")

    if "mix" in st and "add" in st:
        return ("Gently combine the wet and dry components. Avoid overmixing; fold until smooth.")

    if "add water" in st:
        return ("Add water slowly while stirring to avoid lumps. Adjust consistency as needed.")

    if "eno" in st:
        return ("Add Eno just before cooking. Fold gently — bubbles create a fluffy texture.")

    if "steam" in st:
        return ("Steam in a preheated steamer until a toothpick comes out clean. Rest before unmolding.")

    if "tempering" in st:
        return ("Heat oil/ghee, add mustard seeds & curry leaves until they pop. Pour over the dish.")

    if "heat pan" in st:
        return ("Heat a tawa on medium flame; a drop of water should sizzle instantly.")

    if "spread batter" in st:
        return ("Spread batter in a circular motion to desired thickness. Cook until edges crisp.")

    if "cook both sides" in st:
        return ("Flip and cook until both sides are golden-brown and crisp.")

    if "boil" in st and "vegetables" in st:
        return ("Boil vegetables until tender but not mushy. Drain and mash if needed.")

    if "mash" in st:
        return ("Mash cooked vegetables to preferred texture. Adjust seasoning.")

    if "layer" in st:
        return ("Layer rice and masala alternately. Add fried onions, herbs, and spices.")

    if "dum" in st:
        return ("Seal the pot and cook on low heat to allow flavors to meld.")

    if "fry" in st or "shape" in st:
        return ("Shape and fry until golden and crisp. Maintain oil temperature steadily.")

    return (f"{step_text}. Do this carefully and adjust seasoning as needed. "
            f"For {dish}, follow patiently for best results.")

# -----------------------------------------------------
# MATCHING ALGORITHM
# -----------------------------------------------------
def _find_matches(dish_lower: str, recipes_list: List[Dict]):
    if not dish_lower:
        return []

    substring_matches = [r for r in recipes_list if dish_lower in r.get("name", "").lower()]
    if substring_matches:
        return substring_matches

    startswith_matches = [r for r in recipes_list if r.get("name", "").lower().startswith(dish_lower)]
    if startswith_matches:
        return startswith_matches

    names = [r.get("name", "") for r in recipes_list]
    close = difflib.get_close_matches(dish_lower, [n.lower() for n in names], n=5, cutoff=0.6)
    if close:
        close_set = set(close)
        return [r for r in recipes_list if r.get("name", "").lower() in close_set]

    return []

# -----------------------------------------------------
# MAIN RECIPE GENERATOR
# -----------------------------------------------------
def generate_recipe(dish: str, servings: int, extra_recipes: Optional[List[Dict]] = None):
    dish_lower = (dish or "").lower().strip()
    # recipes_all = list(RECIPES) + (list(extra_recipes) if extra_recipes else [])
    raw_list = list(RECIPES) + (list(extra_recipes) if extra_recipes else [])
    recipes_all = [normalize_recipe(r) for r in raw_list]


    matches = _find_matches(dish_lower, recipes_all)

    if not matches:
        return {
            "name": dish.title() if dish else "Unknown",
            "serving_size": servings,
            "ingredients": {},
            "ingredients_detailed": {},
            "steps": ["Recipe not found."],
            "steps_detailed": ["We couldn't find a recipe matching that name."],
            "funny_line": random.choice(_generate_funny_lines(dish or "Dish")),
            "good_message": random.choice(GOOD_MESSAGES)
        }

    best = max(matches, key=lambda r: r.get("score", 1))
    recipe = best

    factor = float(servings) / float(recipe.get("serving_size", 1))
    scaled_ing = scale_ingredients(recipe.get("ingredients", {}), factor)

    ingredients_detailed = {}
    for item, qty in scaled_ing.items():
        desc = _ingredient_description(item)
        qty_formatted = (
            int(qty) if isinstance(qty, (int,)) or (isinstance(qty, float) and qty.is_integer())
            else round(qty, 2)
        )
        ingredients_detailed[item] = {
            "quantity": qty_formatted,
            "description": desc
        }

    steps = recipe.get("steps", [])
    steps_detailed = [_expand_step(s, recipe.get("name", dish), servings) for s in steps]

    funny_line = random.choice(_generate_funny_lines(recipe.get("name", dish)))
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
