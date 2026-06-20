"""
Supabase client factory. Centralizes how every other module gets a
client so the shard-routing logic lives in exactly one place.

Two kinds of clients:
- control plane client: tiny project, just the shard registry
- shard client: the actual data project a given user lives on

For now, with a single shard configured, `get_shard_client()` always
returns shard_001. Once you add a second shard, new signups route
through `pick_shard_for_new_signup()` and existing users route
through `resolve_shard_for_email()` — neither of those functions'
callers need to change.
"""
from __future__ import annotations

from functools import lru_cache

from supabase import create_client, Client

from config.shards import load_all_shards, CONTROL_PLANE_URL, CONTROL_PLANE_SERVICE_KEY, ShardProfile


@lru_cache(maxsize=1)
def get_control_client() -> Client | None:
    if not CONTROL_PLANE_URL or not CONTROL_PLANE_SERVICE_KEY:
        return None
    return create_client(CONTROL_PLANE_URL, CONTROL_PLANE_SERVICE_KEY)


@lru_cache(maxsize=None)
def _client_for_shard(shard_id: str, use_service_role: bool) -> Client:
    shards = load_all_shards()
    profile: ShardProfile | None = shards.get(shard_id)
    if not profile:
        raise RuntimeError(f"No connection profile configured for {shard_id}")
    key = profile.service_role_key if use_service_role else profile.anon_key
    return create_client(profile.url, key)


def get_shard_client(shard_id: str = "shard_001", use_service_role: bool = False) -> Client:
    return _client_for_shard(shard_id, use_service_role)


def resolve_shard_for_email(email: str) -> str:
    """Look up which shard an existing user's email lives on.

    Falls back to shard_001 if the control plane isn't configured
    yet (i.e. you're still on a single project) so the app keeps
    working with zero setup until you actually need multiple shards.
    """
    control = get_control_client()
    if control is None:
        return "shard_001"

    resp = (
        control.table("shard_registry")
        .select("shard_id")
        .eq("email", email.strip().lower())
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if rows:
        return rows[0]["shard_id"]
    return "shard_001"


def resolve_shard_for_username(username: str) -> str:
    """Same idea as resolve_shard_for_email, but keyed on username —
    parents no longer have emails as their login identifier, so
    username is the lookup key for the shard registry going forward.
    Uses the same shard_registry table (its 'email' column doubles as
    a generic identifier column; the name is legacy but the behavior
    is identical).
    """
    control = get_control_client()
    if control is None:
        return "shard_001"

    resp = (
        control.table("shard_registry")
        .select("shard_id")
        .eq("email", username.strip().lower())
        .limit(1)
        .execute()
    )
    rows = resp.data or []
    if rows:
        return rows[0]["shard_id"]
    return "shard_001"


def pick_shard_for_new_signup() -> str:
    """Pick the least-full active shard for a brand-new signup.

    With one shard configured this just returns shard_001. Once you
    register more shards in shard_capacity, this balances new
    signups across them automatically.
    """
    control = get_control_client()
    if control is None:
        return "shard_001"

    resp = (
        control.table("shard_capacity")
        .select("shard_id, approx_user_count, soft_cap")
        .eq("is_active_for_signup", True)
        .execute()
    )
    rows = resp.data or []
    if not rows:
        return "shard_001"

    eligible = [r for r in rows if r["approx_user_count"] < r["soft_cap"]]
    pool = eligible or rows
    pool.sort(key=lambda r: r["approx_user_count"])
    return pool[0]["shard_id"]


def register_email_to_shard(email: str, shard_id: str) -> None:
    control = get_control_client()
    if control is None:
        return  # single-shard mode, nothing to register
    control.table("shard_registry").upsert({
        "email": email.strip().lower(),
        "shard_id": shard_id,
    }).execute()


def register_username_to_shard(username: str, shard_id: str) -> None:
    control = get_control_client()
    if control is None:
        return  # single-shard mode, nothing to register
    control.table("shard_registry").upsert({
        "email": username.strip().lower(),
        "shard_id": shard_id,
    }).execute()
