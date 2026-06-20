"""
CEO identity lives ONLY in environment variables — never in a
database table, never committed to git. This matches your eBay app's
existing pattern (CEO password in env) and your explicit requirement
here that the CEO sign-in is env-based.

Required in .env (or Streamlit Cloud secrets):
    CEO_EMAIL=you@example.com
    CEO_PASSWORD=choose-a-strong-one

.env must be in .gitignore — see the .gitignore written alongside
this file.
"""
import os

APP_SETTINGS = {
    "platform_name": "Parent2Parent",
    "tagline": "Real people. Real problems. Real education.",
    "max_flags_per_page": 10,
    "max_events_per_page": 6,
}

CEO_EMAIL = os.environ.get("CEO_EMAIL", "")
CEO_PASSWORD = os.environ.get("CEO_PASSWORD", "")


def verify_ceo_login(email: str, password: str) -> bool:
    if not CEO_EMAIL or not CEO_PASSWORD:
        return False
    return (
        email.strip().lower() == CEO_EMAIL.strip().lower()
        and password == CEO_PASSWORD
    )
