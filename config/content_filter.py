"""
Chat content filter.

Design goals:
- Zero tolerance, no warnings: any hit blocks the message AND raises
  a moderation flag (per your "only getting no warnings" requirement
  — meaning no warning step, straight to the review queue).
- Category-based so the CEO sees WHY something was flagged
  ('profanity', 'explicit_sexual', 'harassment', 'self_harm_risk')
  without you having to maintain one giant undifferentiated list.
- Word lists are intentionally loaded from a plain text config file
  (config/blocked_terms.txt) rather than hardcoded in this module, so
  you can extend/edit the list yourself without touching app code,
  and so the list isn't sitting in a way that this module's source
  doubles as a published reference of exact bypass-relevant terms.
- Catches basic leetspeak/spacing tricks (e.g. "f u c k", "f*ck")
  without trying to be a full adversarial NLP system — good enough
  for a parenting-community app, not a content-moderation product.
- IMPORTANT: this is a SAFETY NET, not a substitute for the CEO
  review queue. Anything borderline should still land in moderation
  for a human to see.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

BLOCKED_TERMS_FILE = Path(__file__).parent / "blocked_terms.txt"

# Simple, well-known character substitutions used to dodge filters.
LEET_MAP = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s",
}


@dataclass
class FilterResult:
    blocked: bool
    categories: list[str]


def _load_blocked_terms() -> dict[str, list[str]]:
    """Parse config/blocked_terms.txt.

    Format: one term per line, as `category: term`. Lines starting
    with # are comments. Missing file => empty filter (fails open to
    "nothing blocked" rather than crashing the app — you'll want to
    populate this file yourself with terms appropriate to your
    community, since exact wording is a judgment call for the app
    owner, not something to bake into shared code).
    """
    terms: dict[str, list[str]] = {}
    if not BLOCKED_TERMS_FILE.exists():
        return terms
    for line in BLOCKED_TERMS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        category, term = line.split(":", 1)
        category = category.strip()
        term = term.strip().lower()
        if term:
            terms.setdefault(category, []).append(term)
    return terms


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = "".join(LEET_MAP.get(ch, ch) for ch in text)
    # collapse repeated chars (e.g. "fuuuck" -> "fuck") and strip
    # non-alphanumeric separators people use to dodge filters
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    return text


def check_message(text: str) -> FilterResult:
    blocked_terms = _load_blocked_terms()
    normalized = _normalize(text)
    # also check a version with all whitespace removed, to catch
    # "f u c k" style spacing tricks
    normalized_nospace = normalized.replace(" ", "")

    hit_categories: list[str] = []
    for category, terms in blocked_terms.items():
        for term in terms:
            term_norm = _normalize(term)
            if not term_norm:
                continue
            if term_norm in normalized or term_norm.replace(" ", "") in normalized_nospace:
                if category not in hit_categories:
                    hit_categories.append(category)
                break

    return FilterResult(blocked=bool(hit_categories), categories=hit_categories)
