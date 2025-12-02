# storage.py
import json
import os
from typing import List, Dict

USER_RECIPES_FILE = "user_recipes.json"


def _read_file() -> List[Dict]:
    if not os.path.isfile(USER_RECIPES_FILE):
        return []
    try:
        with open(USER_RECIPES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        # corrupted or unreadable file -> treat as empty
        return []


def _write_file(data: List[Dict]):
    # atomic-ish write (write full file in one go)
    tmp = USER_RECIPES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USER_RECIPES_FILE)


def load_user_recipes() -> List[Dict]:
    """Return the list of user-saved recipe dicts (same shape as RECIPES entries)."""
    return _read_file()


def save_user_recipe(recipe: Dict) -> None:
    """
    Append a recipe to user recipes. Recipe should be a dict similar to RECIPES entries:
      { "name": str, "serving_size": int, "ingredients": { ... }, "steps": [...], "score": int (optional) }
    """
    data = _read_file()
    # basic dedupe by name (case-insensitive) — if exists, replace
    name = (recipe.get("name") or "").strip()
    if not name:
        raise ValueError("Recipe must have a name")
    lowered = name.lower()
    replaced = False
    for i, r in enumerate(data):
        if (r.get("name") or "").lower() == lowered:
            data[i] = recipe
            replaced = True
            break
    if not replaced:
        data.append(recipe)
    _write_file(data)
