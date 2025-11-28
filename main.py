from flask import Flask, render_template, request, redirect, url_for
from router import get_recipe_output
from utils_bg import get_background_image
import csv
from datetime import datetime
import os

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
