"""
Avatars are NOT user-uploaded. Per the product requirement, users
pick from a small curated set of icons that match their age band so
nothing arbitrary gets rendered in a youth-adjacent chat room and the
app never has to handle/store arbitrary image uploads (no crash risk,
no moderation burden on images).

Each entry points to a local SVG/PNG under assets/avatars/. Swap the
files later without touching any other code — this module is the
only place that knows the mapping.

The original 7 bands (11_13 through 25_27) each have their own
generated icon set. Bands added later (27_32 through 62_65) reuse an
existing band's actual image files rather than needing 32 more SVGs
generated — ASSET_BAND_FALLBACK maps a band with no dedicated art to
the band whose files it borrows. The avatar_key stored per-user is
still unique to their actual band (so "27_32_male_01" is tracked
distinctly from "25_27_male_01" in the database), only the *file on
disk* it points to is shared.
"""
from __future__ import annotations

from config.age_bands import AGE_BAND_ORDER

ICONS_PER_BAND = 4  # how many style choices we offer within a band+gender

AVATAR_ASSET_DIR = "assets/avatars"

# Bands with their own dedicated generated icon files.
BANDS_WITH_OWN_ART = {"11_13", "13_15", "15_17", "18_21", "21_23", "23_25", "25_27"}

# Every band NOT in BANDS_WITH_OWN_ART borrows its image files from
# the oldest band that does have art (25_27), since that's the
# closest visual "adult" style already on hand. If you generate real
# art for the older bands later, just remove them from this mapping
# (or add per-band entries) — avatar_choices() below checks this
# automatically.
ASSET_BAND_FALLBACK: dict[str, str] = {
    band: "25_27" for band in AGE_BAND_ORDER if band not in BANDS_WITH_OWN_ART
}


def _asset_band_for(age_band: str) -> str:
    return ASSET_BAND_FALLBACK.get(age_band, age_band)


def avatar_choices(age_band: str, gender: str) -> list[dict]:
    """Return the list of selectable avatars for a given band+gender.

    Each item: {"key": "...", "file": "assets/avatars/....svg", "label": "..."}
    The `key` is always specific to the real age_band (for accurate
    per-user storage); `file` may point at a borrowed asset band's
    files if this band has no dedicated art yet.
    """
    asset_band = _asset_band_for(age_band)
    choices = []
    for i in range(1, ICONS_PER_BAND + 1):
        key = f"{age_band}_{gender}_{i:02d}"
        asset_file_key = f"{asset_band}_{gender}_{i:02d}"
        choices.append({
            "key": key,
            "file": f"{AVATAR_ASSET_DIR}/{asset_file_key}.svg",
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
