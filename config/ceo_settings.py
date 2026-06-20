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


def _ceo_email() -> str:
    # Read at call-time, not import-time. If this module gets imported
    # before bootstrap.py has populated os.environ (e.g. via Streamlit
    # Cloud secrets), a module-level constant would freeze as "" forever
    # for the life of the process — this avoids that entirely.
    return os.environ.get("CEO_EMAIL", "")


def _ceo_password() -> str:
    return os.environ.get("CEO_PASSWORD", "")


def verify_ceo_login(email: str, password: str) -> bool:
    expected_email = _ceo_email().strip()
    expected_password = _ceo_password().strip()
    if not expected_email or not expected_password:
        return False
    return (
        email.strip().lower() == expected_email.lower()
        and password.strip() == expected_password
    )


def is_ceo_email(email: str) -> bool:
    """Used by signup to block someone from registering a parent
    account with the same email as the CEO login — that email is
    reserved for the env-var-based CEO sign-in only."""
    expected_email = _ceo_email().strip().lower()
    if not expected_email:
        return False
    return email.strip().lower() == expected_email
