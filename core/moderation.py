"""
Moderation queue backend — what powers the CEO's "needs review" panel.

Per your spec: no warnings, the CEO directly chooses to clear the
flag (give access back / dismiss as a false positive) or revoke the
user's access (suspend the account, which immediately cuts off their
ability to sign in or post).
"""
from __future__ import annotations

from datetime import datetime, timezone

from core.supabase_clients import get_shard_client


def list_open_flags(shard_id: str, limit: int = 50) -> list[dict]:
    client = get_shard_client(shard_id, use_service_role=True)
    resp = (
        client.table("moderation_flags")
        .select("*, parent_profiles(first_name, email, age_band, gender, account_status)")
        .eq("status", "open")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


def clear_flag(shard_id: str, flag_id: int, resolved_by: str = "ceo") -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("moderation_flags").update({
        "status": "cleared",
        "resolved_by": resolved_by,
        "resolved_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", flag_id).execute()


def suspend_user(shard_id: str, parent_id: str, flag_id: int | None = None, resolved_by: str = "ceo") -> None:
    """Revoke a user's access. This sets account_status='suspended',
    which both blocks future login (core/auth.py checks this) and can
    be paired with revoking their current Supabase session.
    """
    client = get_shard_client(shard_id, use_service_role=True)
    now = datetime.now(timezone.utc).isoformat()

    client.table("parent_profiles").update({
        "account_status": "suspended",
        "suspended_at": now,
        "suspended_by": resolved_by,
    }).eq("id", parent_id).execute()

    # Best-effort: kick any active sessions immediately rather than
    # waiting for token expiry.
    try:
        client.auth.admin.sign_out(parent_id)
    except Exception:
        pass

    if flag_id is not None:
        client.table("moderation_flags").update({
            "status": "actioned",
            "resolved_by": resolved_by,
            "resolved_at": now,
        }).eq("id", flag_id).execute()


def reinstate_user(shard_id: str, parent_id: str) -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("parent_profiles").update({
        "account_status": "active",
        "suspended_at": None,
        "suspended_by": None,
        "flagged_reason": None,
        "flagged_at": None,
    }).eq("id", parent_id).execute()
