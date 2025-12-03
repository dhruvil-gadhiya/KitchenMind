# storage.py (replace or add these functions)

import json
import os
from typing import List, Dict
from datetime import datetime

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
        return []

def _write_file(data: List[Dict]):
    tmp = USER_RECIPES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USER_RECIPES_FILE)

def load_user_recipes() -> List[Dict]:
    """Return the list of user-saved recipe dicts (same shape as RECIPES entries)."""
    return _read_file()

def save_user_recipe(recipe: Dict) -> None:
    """
    Append a recipe to user recipes. If a variant with identical ingredients+steps exists,
    it will replace that variant (update metadata). Otherwise append a new variant.
    Ensures each recipe has metadata: usage_count, created_at, source(optional).
    """
    if not isinstance(recipe, dict):
        raise ValueError("Recipe must be a dict")

    data = _read_file()

    # sanitize/ensure metadata
    recipe = dict(recipe)  # copy to avoid mutating caller
    recipe.setdefault("score", int(recipe.get("score", 5)))
    recipe.setdefault("usage_count", int(recipe.get("usage_count", 0)))
    recipe.setdefault("created_at", recipe.get("created_at") or datetime.utcnow().isoformat())
    # optional: 'source' field

    # basic duplicate detection: exact match of name + ingredients + steps
    def signature(r):
        return (
            (r.get("name") or "").strip().lower(),
            json.dumps(r.get("ingredients", {}), sort_keys=True),
            json.dumps(r.get("steps", []), sort_keys=True)
        )

    sig_new = signature(recipe)
    replaced = False
    for i, r in enumerate(data):
        if signature(r) == sig_new:
            # Update existing: merge metadata (keep highest score, update created_at if missing)
            updated = dict(r)
            updated.update(recipe)
            # keep highest score and sum usage_count
            updated["score"] = max(int(r.get("score", 5)), int(recipe.get("score", 5)))
            updated["usage_count"] = int(r.get("usage_count", 0)) + int(recipe.get("usage_count", 0))
            data[i] = updated
            replaced = True
            break

    if not replaced:
        # Append as a new variant (allow same .name but different ingredients/steps)
        data.append(recipe)

    _write_file(data)


def increment_usage_for_variant(name: str, ingredients: Dict, steps: List[str]) -> None:
    """
    Try to find variant matching name+ingredients+steps and increment usage_count by 1.
    If not found, try to increment for the closest name match.
    """
    data = _read_file()
    sig_target = (
        (name or "").strip().lower(),
        json.dumps(ingredients or {}, sort_keys=True),
        json.dumps(steps or [], sort_keys=True)
    )
    for i, r in enumerate(data):
        sig_r = (
            (r.get("name") or "").strip().lower(),
            json.dumps(r.get("ingredients", {}), sort_keys=True),
            json.dumps(r.get("steps", []), sort_keys=True)
        )
        if sig_r == sig_target:
            data[i]["usage_count"] = int(r.get("usage_count", 0)) + 1
            _write_file(data)
            return

    # fallback: increment first item with same name (case-insensitive)
    lowered = (name or "").strip().lower()
    for i, r in enumerate(data):
        if (r.get("name") or "").strip().lower() == lowered:
            data[i]["usage_count"] = int(r.get("usage_count", 0)) + 1
            _write_file(data)
            return
    # if nothing found — do nothing
