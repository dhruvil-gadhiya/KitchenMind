# main.py
from flask import Flask, render_template, request, redirect, url_for
from router import get_recipe_output
from utils_bg import get_background_image
import csv
from datetime import datetime
import os
from storage import save_user_recipe, load_user_recipes

app = Flask(__name__)
app.secret_key = "supersecretkey123"


@app.route("/")
def home():
    # Dashboard page
    return render_template("index.html")


@app.route("/get_recipe", methods=["POST"])
def get_recipe():
    recipe_name = request.form.get("dish", "").strip()
    try:
        serving = int(request.form.get("servings", 1))
        if serving <= 0:
            serving = 1
    except (ValueError, TypeError):
        serving = 1

    final_recipe = get_recipe_output(recipe_name, serving)

    # choose background image (dish-specific or default)
    bg = get_background_image(final_recipe.get("name", recipe_name))
    # no feedback message by default
    return render_template("result.html", recipe=final_recipe, bg=bg, feedback_thanks=None)


@app.route("/feedback", methods=["POST"])
def feedback():
    # feedback form sends: recipe_name, servings, rating (optional), message (optional)
    recipe_name = request.form.get("recipe_name", "").strip()
    servings = request.form.get("servings", "").strip()
    rating = request.form.get("rating", "").strip()  # may be empty
    message = request.form.get("message", "").strip()

    # Save feedback to CSV (append). Create file if not exists.
    feedback_file = "feedback.csv"
    exists = os.path.isfile(feedback_file)
    try:
        with open(feedback_file, mode="a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(["timestamp", "recipe_name", "servings", "rating", "message"])
            writer.writerow([datetime.utcnow().isoformat(), recipe_name, servings, rating, message])
        thanks = "Thanks! Your feedback was recorded — much appreciated. ⭐"
    except Exception as e:
        # if saving fails, still re-render recipe and show an error message
        thanks = f"Thanks — we tried to save your feedback but hit an error: {e}"

    # re-render the same recipe page so the user sees their feedback placement
    try:
        serving_int = int(servings) if servings else 1
    except Exception:
        serving_int = 1
    final_recipe = get_recipe_output(recipe_name, serving_int)
    bg = get_background_image(final_recipe.get("name", recipe_name))
    return render_template("result.html", recipe=final_recipe, bg=bg, feedback_thanks=thanks)


# -------------------- New: add recipe routes --------------------
@app.route("/add_recipe", methods=["GET"])
def add_recipe_form():
    """Show the Add Recipe form."""
    return render_template("add_recipe.html")


def _parse_ingredients(text: str):
    """
    Accepts multi-line text. Each line either:
      - "Ingredient|quantity"
      - "Ingredient - quantity"
      - "Ingredient : quantity"
      - "Ingredient" (no quantity)
    Returns dict { ingredient_name: quantity_or_empty_string }
    """
    ingredients = {}
    if not text:
        return ingredients
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # try separators
        for sep in ("|", "-", ":"):
            if sep in line:
                parts = [p.strip() for p in line.split(sep, 1)]
                name = parts[0]
                qty = parts[1] if len(parts) > 1 else ""
                ingredients[name] = qty
                break
        else:
            # no separator
            ingredients[line] = ""
    return ingredients


@app.route("/add_recipe", methods=["POST"])
def add_recipe_submit():
    """
    Save user-submitted recipe to disk and render it immediately.
    Expected fields in form:
      name, serving_size, ingredients (multiline), steps (multiline), score (optional)
    """
    name = request.form.get("name", "").strip()
    if not name:
        return render_template("add_recipe.html", error="Name is required")

    try:
        serving_size = int(request.form.get("serving_size", 5))
        if serving_size <= 0:
            serving_size = 1
    except Exception:
        serving_size = 5

    ingredients_text = request.form.get("ingredients", "").strip()
    steps_text = request.form.get("steps", "").strip()
    score_text = request.form.get("score", "").strip()

    ingredients = _parse_ingredients(ingredients_text)
    steps = [s.strip() for s in steps_text.splitlines() if s.strip()]

    try:
        score = int(score_text) if score_text else 5
    except Exception:
        score = 5

    recipe_obj = {
        "name": name,
        "serving_size": serving_size,
        "score": score,
        "ingredients": ingredients,
        "steps": steps
    }

    try:
        save_user_recipe(recipe_obj)
    except Exception as e:
        return render_template("add_recipe.html", error=f"Could not save recipe: {e}", form=request.form)

    # render the newly-saved recipe using the same result template
    final_recipe = get_recipe_output(name, serving_size)
    bg = get_background_image(final_recipe.get("name", name))
    thanks = "Your recipe was saved and is now available in searches. Thank you! 🎉"
    return render_template("result.html", recipe=final_recipe, bg=bg, feedback_thanks=thanks)


if __name__ == "__main__":
    app.run(debug=True)
