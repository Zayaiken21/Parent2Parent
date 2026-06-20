"""
Auth flows for Parent2Parent — token-based signup, username/password
login, no Supabase Auth dependency for parents.

Flow:
  1. CEO generates a 6-character access token (core/parent_tokens.py).
  2. A parent redeems that token once: picks a username + password,
     sets age/gender (validated by a security question for their
     claimed age band), optionally adds an email (events-only).
  3. From then on, the parent logs in with username + password,
     checked directly against a bcrypt hash stored in parent_profiles.
  4. Forgotten password: there is no email-based reset. The parent
     asks the CEO for a new access token and redeems it again,
     exactly like your eBay app's original-token reset pattern.

Passwords are hashed with bcrypt — never stored or compared in
plaintext, and never logged.
"""
from __future__ import annotations

import bcrypt

from config.age_bands import age_band_for_birth_year, check_security_answer, SECURITY_QUESTIONS
from config.avatars import default_avatar_key
from config.ceo_settings import is_ceo_username
from core.parent_tokens import validate_token, mark_token_redeemed, TokenError
from core.supabase_clients import (
    get_shard_client,
    pick_shard_for_new_signup,
    register_username_to_shard,
    resolve_shard_for_username,
)


class AuthError(Exception):
    pass


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed/legacy hash — treat as no match rather than crashing.
        return False


def complete_signup(
    token: str,
    username: str,
    password: str,
    first_name: str,
    birth_year: int,
    gender: str,
    security_answer: str,
    email: str | None = None,
) -> dict:
    """Redeem an access token and create a parent account. Returns the
    new profile dict on success."""
    username = username.strip()
    if not username:
        raise AuthError("Choose a username.")
    if len(username) < 3:
        raise AuthError("Username must be at least 3 characters.")
    if is_ceo_username(username):
        raise AuthError("That username is reserved. Please choose a different one.")

    if len(password) < 8:
        raise AuthError("Password must be at least 8 characters.")

    if not first_name.strip():
        raise AuthError("Enter a first name.")

    age_band = age_band_for_birth_year(birth_year)
    if not age_band:
        raise AuthError("We couldn't match that birth year to a supported age range.")

    if not check_security_answer(age_band, security_answer):
        raise AuthError("That answer doesn't match what we'd expect for this age range.")

    if gender not in ("male", "female"):
        raise AuthError("Select an option for the chat-room setting.")

    shard_id = pick_shard_for_new_signup()
    client = get_shard_client(shard_id, use_service_role=True)

    # Validate the token against this shard before anything else.
    try:
        token_row = validate_token(token, shard_id)
    except TokenError as exc:
        raise AuthError(str(exc)) from exc

    # Username must be unique within this shard.
    existing = (
        client.table("parent_profiles")
        .select("id")
        .ilike("username", username)
        .limit(1)
        .execute()
    )
    if existing.data:
        raise AuthError("That username is already taken.")

    clean_email = (email or "").strip().lower() or None

    spec = SECURITY_QUESTIONS[age_band]
    profile = {
        "first_name": first_name.strip()[:40],
        "username": username,
        "password_hash": _hash_password(password),
        "token_used": token_row["token"],
        "email": clean_email,
        "avatar_key": default_avatar_key(age_band, gender),
        "gender": gender,
        "birth_year": birth_year,
        "age_band": age_band,
        "security_question_key": spec["key"],
        "security_answer_hash": _hash_password(security_answer.strip().lower()),
        "events_opt_in": False,
    }

    insert_resp = client.table("parent_profiles").insert(profile).execute()
    rows = insert_resp.data or []
    if not rows:
        raise AuthError("Account creation failed. Try again.")
    created = rows[0]

    mark_token_redeemed(token_row["token"], created["id"], shard_id)
    register_username_to_shard(username, shard_id)

    return created


def login(username: str, password: str) -> dict:
    username = username.strip()
    if not username or not password:
        raise AuthError("Enter both username and password.")

    shard_id = resolve_shard_for_username(username)
    client = get_shard_client(shard_id, use_service_role=True)

    resp = (
        client.table("parent_profiles")
        .select("*")
        .ilike("username", username)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        raise AuthError("Incorrect username or password.")

    profile = rows[0]
    if not _check_password(password, profile.get("password_hash") or ""):
        raise AuthError("Incorrect username or password.")

    status = profile.get("account_status")
    if status == "suspended":
        raise AuthError("This account has been suspended.")
    if status == "deleted":
        raise AuthError("This account no longer exists.")

    profile["_shard_id"] = shard_id
    return profile
