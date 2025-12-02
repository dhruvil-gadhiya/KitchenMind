def scale_ingredients(ingredients: dict, factor: float):
    """
    Safely scale ingredient quantities by the given factor.
    Automatically skips items that do not contain numeric quantities.
    """
    scaled = {}

    for item, qty in ingredients.items():
        try:
            # Try converting quantity to float
            val = float(qty) * float(factor)

            # Prefer integer display when it's close to integer
            if abs(val - round(val)) < 0.0001:
                val_to_store = int(round(val))
            else:
                val_to_store = round(val, 2)

            scaled[item] = val_to_store

        except (ValueError, TypeError):
            # If quantity is not numeric, keep it as-is (prevents crashes)
            scaled[item] = qty
            continue

    return scaled
