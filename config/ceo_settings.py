"""
CEO identity lives ONLY in environment variables — never in a
database table, never committed to git. This matches your eBay app's
existing pattern (CEO password in env) and your explicit requirement
here that the CEO sign-in is env-based.

Required in .env (or Streamlit Cloud secrets):
    CEO_USERNAME=your_ceo_username
    CEO_PASSWORD=choose-a-strong-one

CEO_EMAIL is still read as a fallback for backwards compatibility
with earlier setups, but CEO_USERNAME is preferred going forward
since parent accounts are now username/password-based too (no email
required), and the CEO sign-in form is the same single form parents
use — just checked against these env vars first.

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


def _ceo_username() -> str:
    # Read at call-time, not import-time. If this module gets imported
    # before bootstrap.py has populated os.environ (e.g. via Streamlit
    # Cloud secrets), a module-level constant would freeze as "" forever
    # for the life of the process — this avoids that entirely.
    username = os.environ.get("CEO_USERNAME", "").strip()
    if username:
        return username
    # Backwards-compat fallback for setups that only ever had CEO_EMAIL.
    return os.environ.get("CEO_EMAIL", "").strip()


def _ceo_password() -> str:
    return os.environ.get("CEO_PASSWORD", "")


def verify_ceo_login(username: str, password: str) -> bool:
    expected_username = _ceo_username().strip()
    expected_password = _ceo_password().strip()
    if not expected_username or not expected_password:
        return False
    return (
        username.strip().lower() == expected_username.lower()
        and password.strip() == expected_password
    )


def is_ceo_username(username: str) -> bool:
    """Used by signup to block someone from registering a parent
    account with the same username as the CEO login — that username
    is reserved for the env-var-based CEO sign-in only."""
    expected_username = _ceo_username().strip().lower()
    if not expected_username:
        return False
    return username.strip().lower() == expected_username
