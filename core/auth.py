"""
Auth flows for Parent2Parent.

Password storage/verification is delegated entirely to Supabase Auth
(auth.users) — we never hash or store passwords ourselves. What we
add on top:
  - first-name + age + gender + security-question capture at signup
  - 6-digit email verification codes (signup + password reset),
    sent via the email backend, hashed at rest
  - shard routing so signup/login work the same whether you have
    1 Supabase project or 50
"""
from __future__ import annotations

import hashlib
import random
import secrets
from datetime import datetime, timedelta, timezone

from config.age_bands import age_band_for_birth_year, check_security_answer, SECURITY_QUESTIONS
from config.avatars import default_avatar_key
from core.supabase_clients import (
    get_shard_client,
    pick_shard_for_new_signup,
    register_email_to_shard,
    resolve_shard_for_email,
)
from backend.email_service import send_verification_email, send_password_reset_email

CODE_TTL_MINUTES = 15


class AuthError(Exception):
    pass


def _hash_code(code: str, email: str) -> str:
    # Salted with the email so two users who happen to get the same
    # code can't be confused with each other.
    return hashlib.sha256(f"{email.strip().lower()}:{code}".encode()).hexdigest()


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def request_signup_code(email: str) -> None:
    """Step 1 of signup: send a 6-digit code to the email address."""
    email = email.strip().lower()
    if not email or "@" not in email:
        raise AuthError("Enter a valid email address.")

    shard_id = pick_shard_for_new_signup()
    client = get_shard_client(shard_id, use_service_role=True)

    code = _generate_code()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)).isoformat()

    client.table("verification_codes").insert({
        "email": email,
        "code_hash": _hash_code(code, email),
        "purpose": "signup_verify",
        "expires_at": expires_at,
    }).execute()

    send_verification_email(to_email=email, code=code, purpose="signup")


def _verify_code(client, email: str, code: str, purpose: str) -> bool:
    email = email.strip().lower()
    resp = (
        client.table("verification_codes")
        .select("id, code_hash, expires_at, consumed_at")
        .eq("email", email)
        .eq("purpose", purpose)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        return False
    row = rows[0]
    if row.get("consumed_at"):
        return False
    expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > expires_at:
        return False
    if row["code_hash"] != _hash_code(code, email):
        return False

    client.table("verification_codes").update({
        "consumed_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", row["id"]).execute()
    return True


def complete_signup(
    email: str,
    code: str,
    password: str,
    first_name: str,
    birth_year: int,
    gender: str,
    security_answer: str,
) -> dict:
    """Step 2 of signup: verify the code, create the auth user, and
    create the parent_profiles row. Returns the new profile dict."""
    email = email.strip().lower()
    shard_id = pick_shard_for_new_signup()
    client = get_shard_client(shard_id, use_service_role=True)

    if not _verify_code(client, email, code, "signup_verify"):
        raise AuthError("That code is invalid or expired. Request a new one.")

    age_band = age_band_for_birth_year(birth_year)
    if not age_band:
        raise AuthError("We couldn't match that birth year to a supported age range.")

    if not check_security_answer(age_band, security_answer):
        raise AuthError("That answer doesn't match what we'd expect for this age range.")

    if gender not in ("male", "female"):
        raise AuthError("Select an option for the chat-room setting.")

    if len(password) < 8:
        raise AuthError("Password must be at least 8 characters.")

    if not first_name.strip():
        raise AuthError("Enter a first name.")

    # Create the actual auth user (Supabase Auth owns password hashing).
    auth_resp = client.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,  # we already verified ownership via our own 6-digit code
    })
    user = auth_resp.user
    if not user:
        raise AuthError("Account creation failed. Try again.")

    spec = SECURITY_QUESTIONS[age_band]
    profile = {
        "id": user.id,
        "first_name": first_name.strip()[:40],
        "email": email,
        "avatar_key": default_avatar_key(age_band, gender),
        "gender": gender,
        "birth_year": birth_year,
        "age_band": age_band,
        "security_question_key": spec["key"],
        "security_answer_hash": hashlib.sha256(security_answer.strip().lower().encode()).hexdigest(),
        "events_opt_in": False,
    }
    client.table("parent_profiles").insert(profile).execute()
    register_email_to_shard(email, shard_id)

    return profile


def login(email: str, password: str) -> dict:
    email = email.strip().lower()
    shard_id = resolve_shard_for_email(email)
    client = get_shard_client(shard_id, use_service_role=False)

    try:
        auth_resp = client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as exc:
        raise AuthError("Incorrect email or password.") from exc

    user = auth_resp.user
    if not user:
        raise AuthError("Incorrect email or password.")

    service_client = get_shard_client(shard_id, use_service_role=True)
    profile_resp = (
        service_client.table("parent_profiles")
        .select("*")
        .eq("id", user.id)
        .limit(1)
        .execute()
    )
    rows = profile_resp.data or []
    if not rows:
        raise AuthError("Account profile not found. Contact support.")

    profile = rows[0]
    status = profile.get("account_status")
    if status == "suspended":
        raise AuthError("This account has been suspended.")
    if status == "deleted":
        raise AuthError("This account no longer exists.")

    profile["_shard_id"] = shard_id
    profile["_access_token"] = auth_resp.session.access_token if auth_resp.session else None
    return profile


def request_password_reset_code(email: str) -> None:
    email = email.strip().lower()
    shard_id = resolve_shard_for_email(email)
    client = get_shard_client(shard_id, use_service_role=True)

    code = _generate_code()
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES)).isoformat()
    client.table("verification_codes").insert({
        "email": email,
        "code_hash": _hash_code(code, email),
        "purpose": "password_reset",
        "expires_at": expires_at,
    }).execute()

    send_password_reset_email(to_email=email, code=code)


def complete_password_reset(email: str, code: str, new_password: str) -> None:
    email = email.strip().lower()
    shard_id = resolve_shard_for_email(email)
    client = get_shard_client(shard_id, use_service_role=True)

    if not _verify_code(client, email, code, "password_reset"):
        raise AuthError("That code is invalid or expired. Request a new one.")

    if len(new_password) < 8:
        raise AuthError("Password must be at least 8 characters.")

    profile_resp = (
        client.table("parent_profiles").select("id").eq("email", email).limit(1).execute()
    )
    rows = profile_resp.data or []
    if not rows:
        raise AuthError("Account not found.")
    user_id = rows[0]["id"]

    client.auth.admin.update_user_by_id(user_id, {"password": new_password})
