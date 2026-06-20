"""
Parent access tokens — CEO generates a short code, a parent redeems
it once to create their account. Modeled directly on the eBay app's
client_licenses / token_store pattern, adapted for this app's
username/password (not Supabase Auth) signup flow.
"""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone

from core.supabase_clients import get_shard_client

TOKEN_LENGTH = 6
TOKEN_ALPHABET = string.ascii_uppercase + string.digits  # e.g. 'A3F9K2'


class TokenError(Exception):
    pass


def generate_token(shard_id: str = "shard_001") -> str:
    """CEO action: create a brand-new, unused access token."""
    client = get_shard_client(shard_id, use_service_role=True)

    # Retry a handful of times on the (very unlikely) chance of a
    # collision with an existing token, rather than trusting a single
    # random draw to always be unique.
    for _ in range(10):
        token = "".join(secrets.choice(TOKEN_ALPHABET) for _ in range(TOKEN_LENGTH))
        existing = (
            client.table("parent_access_tokens")
            .select("id")
            .eq("token", token)
            .limit(1)
            .execute()
        )
        if not (existing.data or []):
            client.table("parent_access_tokens").insert({"token": token}).execute()
            return token

    raise TokenError("Could not generate a unique token. Try again.")


def list_tokens(shard_id: str = "shard_001", limit: int = 100) -> list[dict]:
    client = get_shard_client(shard_id, use_service_role=True)
    resp = (
        client.table("parent_access_tokens")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


def deactivate_token(token: str, shard_id: str = "shard_001") -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("parent_access_tokens").update({"active": False}).eq(
        "token", token.strip().upper()
    ).execute()


def validate_token(token: str, shard_id: str = "shard_001") -> dict:
    """Raises TokenError if the token doesn't exist, is inactive, or
    has already been redeemed. Returns the token row if valid."""
    token = token.strip().upper()
    if not token:
        raise TokenError("Enter your access token.")

    client = get_shard_client(shard_id, use_service_role=True)
    resp = (
        client.table("parent_access_tokens")
        .select("*")
        .eq("token", token)
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        raise TokenError("That token wasn't found. Check it and try again.")

    row = rows[0]
    if not row.get("active", True):
        raise TokenError("That token is no longer active.")
    if row.get("redeemed"):
        raise TokenError("That token has already been used. Ask the CEO for a new one.")

    return row


def mark_token_redeemed(token: str, parent_id: str, shard_id: str = "shard_001") -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("parent_access_tokens").update({
        "redeemed": True,
        "redeemed_by": parent_id,
        "redeemed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("token", token.strip().upper()).execute()
