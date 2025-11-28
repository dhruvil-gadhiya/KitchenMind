def scale_ingredients(ingredients: dict, factor: float):
    """
    Scale the ingredient quantities by the given factor.
    Keep quantity precision human-friendly (2 decimals).
    """
    scaled = {}
    for item, qty in ingredients.items():
        # ensure safe arithmetic and rounding
        val = float(qty) * float(factor)
        # prefer integer display when it's close to integer
        if abs(val - round(val)) < 0.0001:
            val_to_store = int(round(val))
        else:
            val_to_store = round(val, 2)
        scaled[item] = val_to_store
    return scaled
