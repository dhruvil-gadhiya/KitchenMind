# utils_bg.py — FIXED VERSION

def get_background_image(dish_name: str):
    """
    Return a static image path for a dish. Matches exact filenames
    as they exist inside /static/images/.
    """
    if not dish_name:
        return "/static/images/default_bg.png"

    d = dish_name.lower().strip()

    # exact filenames from your static/images folder (case-sensitive in some OS)
    mapping = {
        "khaman": "/static/images/Khaman.png",
        "upma": "/static/images/Upma.png",
        "dosa": "/static/images/Dosa.png",
        "biryani": "/static/images/Biryani.png",
        "pav bhaji": "/static/images/Pav Bhaji.png",
        "pizza": "/static/images/Pizza.png",
        "sandwich": "/static/images/Sandwich.png",
        "garlic bread": "/static/images/Garlic Bread.png",
        "pani puri": "/static/images/Pani Puri.png",
        "aloo paratha": "/static/images/Aloo Paratha.png",
        "aloo puri": "/static/images/Aloo Puri.png",
        "dabeli": "/static/images/Dabeli.png",
        "idli": "/static/images/Idli.png",
        "jalebi-fafda": "/static/images/Jalebi-Fafda.png",
        "samosa": "/static/images/Samosa.png",
        "vada pav": "/static/images/Vada Pav.png",
        "chhole kulche": "/static/images/Chhole Kulche.png",
        "poha": "/static/images/Poha.png",
        "veg momos": "/static/images/Veg Momos.png",
        "masala khichdi": "/static/images/Masala Khichdi.png",
    }

    # substring match
    for key, path in mapping.items():
        if key in d:
            return path

    # fallback default
    return "/static/images/default_bg.png"
