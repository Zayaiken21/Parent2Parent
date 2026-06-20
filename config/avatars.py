"""
Avatars are NOT user-uploaded. Per the product requirement, users
pick from a small curated set of icons that match their age band so
nothing arbitrary gets rendered in a youth-adjacent chat room and the
app never has to handle/store arbitrary image uploads (no crash risk,
no moderation burden on images).

Each entry points to a local SVG/PNG under assets/avatars/. Swap the
files later without touching any other code — this module is the
only place that knows the mapping.
"""
from __future__ import annotations

from config.age_bands import AGE_BAND_ORDER

ICONS_PER_BAND = 4  # how many style choices we offer within a band+gender

AVATAR_ASSET_DIR = "assets/avatars"


def avatar_choices(age_band: str, gender: str) -> list[dict]:
    """Return the list of selectable avatars for a given band+gender.

    Each item: {"key": "...", "file": "assets/avatars/....svg", "label": "..."}
    """
    choices = []
    for i in range(1, ICONS_PER_BAND + 1):
        key = f"{age_band}_{gender}_{i:02d}"
        choices.append({
            "key": key,
            "file": f"{AVATAR_ASSET_DIR}/{key}.svg",
            "label": f"Style {i}",
        })
    return choices


def default_avatar_key(age_band: str, gender: str) -> str:
    return f"{age_band}_{gender}_01"


def all_avatar_keys() -> list[str]:
    keys = []
    for band in AGE_BAND_ORDER:
        for gender in ("male", "female"):
            keys.extend(c["key"] for c in avatar_choices(band, gender))
    return keys
