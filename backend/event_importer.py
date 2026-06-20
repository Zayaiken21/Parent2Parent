"""
Event import-from-URL.

This is intentionally NOT a general-purpose scraper. Most event,
ticketing, and social platforms (Eventbrite, Meetup, Facebook Events)
actively block scrapers with the same kind of bot protection you've
already run into on the eBay project (PerimeterX/Akamai-class
defenses) — building a scraper that defeats that is out of scope,
same as it was there.

What this DOES reliably: most event pages publish Open Graph and
basic HTML meta tags specifically so links preview nicely when
shared (og:title, og:description, og:image) — that's public,
intended-for-parsing metadata, not a bypass of anything. We read
that, plus a best-effort scan for a date-shaped string in the page
text. The CEO always reviews/edits the result before it's saved, so
a wrong or missing field is just a review step, not a broken feature.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 8
USER_AGENT = "Mozilla/5.0 (compatible; Parent2ParentEventImporter/1.0)"

DATE_PATTERNS = [
    # "June 20, 2026" / "Jun 20, 2026" / "June 20th, 2026"
    r"(January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})",
    # "2026-06-20" / "2026/06/20"
    r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
    # "06/20/2026"
    r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})",
]

MONTH_LOOKUP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}


class EventImportError(Exception):
    pass


@dataclass
class EventDraft:
    title: str
    description: str
    event_date: str | None   # ISO 'YYYY-MM-DD' if found, else None
    image_url: str | None
    source_url: str


def _try_parse_date(match: re.Match, pattern_index: int) -> date | None:
    groups = match.groups()
    try:
        if pattern_index == 0:
            month_name, day, year = groups
            month = MONTH_LOOKUP.get(month_name.lower().rstrip("."))
            if not month:
                return None
            return date(int(year), month, int(day))
        elif pattern_index == 1:
            year, month, day = groups
            return date(int(year), int(month), int(day))
        elif pattern_index == 2:
            month, day, year = groups
            return date(int(year), int(month), int(day))
    except ValueError:
        return None
    return None


def _find_first_future_or_recent_date(text: str) -> str | None:
    """Scan visible page text for the first date-shaped string that
    parses to a real calendar date. Returns ISO format (YYYY-MM-DD)
    or None if nothing parseable was found.
    """
    today = date.today()
    candidates: list[date] = []
    for idx, pattern in enumerate(DATE_PATTERNS):
        for match in re.finditer(pattern, text):
            parsed = _try_parse_date(match, idx)
            if parsed:
                candidates.append(parsed)
    if not candidates:
        return None
    # Prefer the earliest date that isn't more than a year in the past
    # (event pages often also show a "posted on" date, which we want
    # to avoid picking over the actual event date when possible).
    upcoming = [d for d in candidates if d >= today]
    chosen = min(upcoming) if upcoming else min(candidates)
    return chosen.isoformat()


def import_event_from_url(url: str) -> EventDraft:
    """Fetch a URL and extract best-guess event fields, returned as an
    EventDraft for the CEO to review/edit before saving. Only raises
    for actual fetch failures (network error, HTTP error) — if a
    field simply isn't found on the page, it comes back as None/empty
    so the review form just shows a blank to fill in by hand.
    """
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise EventImportError(
            f"Couldn't load that page ({exc.__class__.__name__}). "
            "Some sites block automated fetching — you can still fill in the event by hand."
        ) from exc

    soup = BeautifulSoup(resp.text, "html.parser")

    def _meta(*names: str) -> str:
        for name in names:
            tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
            if tag and tag.get("content"):
                return tag["content"].strip()
        return ""

    title = _meta("og:title", "twitter:title")
    if not title and soup.title:
        title = soup.title.get_text(strip=True)
    if not title:
        title = "Untitled Event"

    description = _meta("og:description", "twitter:description", "description")
    image_url = _meta("og:image", "twitter:image") or None

    visible_text = soup.get_text(" ", strip=True)[:5000]  # cap scan size, most dates appear early
    detected_date = _find_first_future_or_recent_date(visible_text)

    return EventDraft(
        title=title[:200],
        description=description[:800],
        event_date=detected_date,
        image_url=image_url,
        source_url=url,
    )
