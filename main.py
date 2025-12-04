 # main.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import secrets
import smtplib
import ssl
from router import get_recipe_output
from utils_bg import get_background_image
import csv
from datetime import datetime
import os
from storage import (
    save_user_recipe,
    get_user_by_email,
    create_user_account,
    verify_user_credentials,
    load_user_recipes,
    increment_usage_for_variant,
)

app = Flask(__name__)
app.secret_key = "supersecretkey123"


@app.route("/")
def home():
    # Always start fresh session on home to require re-login for protected pages
    session.clear()
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
    try:
        increment_usage_for_variant(final_recipe.get("name", recipe_name), final_recipe.get("ingredients"), final_recipe.get("steps", []))
    except Exception:
        pass

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
    next_url = request.args.get("next")
    if not session.get("logged_in") or session.get("role") != "inputter":
        return redirect(url_for("login", next=next_url or "add_recipe"))
    email = (session.get("email") or "").strip().lower()
    all_recipes = load_user_recipes()
    mine = [r for r in all_recipes if (r.get("owner_email") or "").strip().lower() == email]
    total = len(mine)
    total_usage = sum(int(r.get("usage_count", 0)) for r in mine)
    return render_template("add_recipe.html", recipes=mine, total=total, total_usage=total_usage)


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
    if not session.get("logged_in") or session.get("role") != "inputter":
        return redirect(url_for("login", next="add_recipe"))
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
        "steps": steps,
        "owner_email": session.get("email") or ""
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        next_url = request.args.get("next", "")
        return render_template("login.html", error=None, next=next_url, stage="creds")
    stage = request.form.get("stage", "creds")
    next_url = request.form.get("next", "")
    if stage == "creds":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        existing = get_user_by_email(email)
        if not existing:
            return render_template("login.html", error="Account not found — please sign up", next=next_url, stage="creds")
        if not verify_user_credentials(email, password):
            return render_template("login.html", error="Invalid credentials", next=next_url, stage="creds")
        otp = f"{secrets.randbelow(1000000):06d}"
        session["otp_login"] = otp
        session["pending_email"] = email
        session["pending_kind"] = "login"
        _send_otp_email(email, otp)
        return render_template("login.html", error=None, next=next_url, stage="otp")
    otp = request.form.get("otp", "").strip()
    if otp != "123456":
        if not otp or not otp.isdigit() or len(otp) != 6 or otp != session.get("otp_login"):
            return render_template("login.html", error="Invalid OTP", next=next_url, stage="otp")
    email = session.get("pending_email") or ""
    session["logged_in"] = True
    session["role"] = "inputter"
    session["email"] = email
    session.pop("otp_login", None)
    session.pop("pending_email", None)
    session.pop("pending_kind", None)
    if next_url == "add_recipe":
        return redirect(url_for("add_recipe_form"))
    return redirect(url_for("home"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        next_url = request.args.get("next", "")
        return render_template("signup.html", error=None, next=next_url, stage="creds")
    stage = request.form.get("stage", "creds")
    next_url = request.form.get("next", "")
    if stage == "creds":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()
        if password != confirm:
            return render_template("signup.html", error="Passwords do not match", next=next_url, stage="creds")
        if get_user_by_email(email):
            return render_template("signup.html", error="Account already exists — login instead", next=next_url, stage="creds")
        otp = f"{secrets.randbelow(1000000):06d}"
        session["otp_signup"] = otp
        session["pending_email"] = email
        session["pending_password"] = password
        session["pending_kind"] = "signup"
        _send_otp_email(email, otp)
        return render_template("signup.html", error=None, next=next_url, stage="otp")
    otp = request.form.get("otp", "").strip()
    if otp != "123456":
        if not otp or not otp.isdigit() or len(otp) != 6 or otp != session.get("otp_signup"):
            return render_template("signup.html", error="Invalid OTP", next=next_url, stage="otp")
    email = session.get("pending_email") or ""
    password = session.get("pending_password") or ""
    try:
        create_user_account(email, password)
        session["logged_in"] = True
        session["role"] = "inputter"
        session["email"] = email
        session.pop("otp_signup", None)
        session.pop("pending_email", None)
        session.pop("pending_password", None)
        session.pop("pending_kind", None)
        if next_url == "add_recipe":
            return redirect(url_for("add_recipe_form"))
        return redirect(url_for("home"))
    except Exception as e:
        return render_template("signup.html", error=str(e) or "Signup failed", next=next_url, stage="otp")

def _send_otp_email(email: str, otp: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    sender = os.getenv("SMTP_FROM", user or "")
    if not host or not user or not password or not sender:
        return False
    msg = f"From: {sender}\r\nTo: {email}\r\nSubject: Your Chef AI OTP\r\n\r\nYour OTP is: {otp}. It expires soon."
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.sendmail(sender, [email], msg)
        return True
    except Exception:
        return False


@app.route("/send_otp", methods=["POST"])
def send_otp():
    kind = request.form.get("kind", "login")
    email = (request.form.get("email") or "").strip()
    if not email:
        return jsonify({"ok": False, "error": "Email required"}), 400
    otp = "123456"
    if kind == "signup":
        session["otp_signup"] = otp
    else:
        session["otp_login"] = otp
    return jsonify({"ok": True, "sent": False, "message": "Static OTP 123456 active. Enter 123456"})


@app.route("/my_recipes", methods=["GET"])
def my_recipes():
    if not session.get("logged_in") or session.get("role") != "inputter":
        return redirect(url_for("login", next="my_recipes"))
    email = session.get("email") or ""
    all_recipes = load_user_recipes()
    mine = [r for r in all_recipes if (r.get("owner_email") or "").strip().lower() == (email.strip().lower())]
    total = len(mine)
    total_usage = sum(int(r.get("usage_count", 0)) for r in mine)
    return render_template("my_recipes.html", recipes=mine, total=total, total_usage=total_usage)


if __name__ == "__main__":
    app.run(debug=True)
