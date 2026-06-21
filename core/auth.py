"""
Auth flows for Parent2Parent — shared access-code signup, username/
password login, no Supabase Auth dependency for parents.

Flow:
  1. The CEO sets one shared code in env (PARENT_ACCESS_CODE).
  2. A parent enters that code to unlock the signup form, then picks
     their own username + password, sets age/gender, optionally adds
     an email (events-only). There is no per-account token and no
     security question — the shared code only gates entry to the
     form, it is never an account identifier.
  3. From then on, the parent logs in with username + password,
     checked directly against a bcrypt hash stored in parent_profiles.
     Knowing the shared code never grants access to another person's
     account — accounts are looked up strictly by username, and the
     code isn't stored against any individual account at all.
  4. Forgotten password: there is no email-based reset currently. The
     parent re-enters the shared code and creates a new account under
     a different username, or contacts the CEO for manual help.

Passwords are hashed with bcrypt — never stored or compared in
plaintext, and never logged.
"""
from __future__ import annotations

import bcrypt

from config.age_bands import age_band_for_birth_year
from config.avatars import default_avatar_key
from config.ceo_settings import is_ceo_username, verify_parent_access_code
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
    access_code: str,
    username: str,
    password: str,
    first_name: str,
    birth_year: int,
    gender: str,
    email: str | None = None,
) -> dict:
    """Verify the shared access code, then create a parent account.
    Returns the new profile dict on success. The access_code is
    checked but never stored against the created account — it's a
    one-time gate to reach this form, not an account credential.
    """
    if not verify_parent_access_code(access_code):
        raise AuthError("That access code is incorrect.")

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

    if gender not in ("male", "female"):
        raise AuthError("Select an option for the chat-room setting.")

    shard_id = pick_shard_for_new_signup()
    client = get_shard_client(shard_id, use_service_role=True)

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

    profile = {
        "first_name": first_name.strip()[:40],
        "username": username,
        "password_hash": _hash_password(password),
        "email": clean_email,
        "avatar_key": default_avatar_key(age_band, gender),
        "gender": gender,
        "birth_year": birth_year,
        "age_band": age_band,
        "events_opt_in": False,
    }

    insert_resp = client.table("parent_profiles").insert(profile).execute()
    rows = insert_resp.data or []
    if not rows:
        raise AuthError("Account creation failed. Try again.")
    created = rows[0]

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
