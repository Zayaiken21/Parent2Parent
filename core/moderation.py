"""
Moderation queue backend — what powers the CEO's "needs review" panel.

Per your spec: no warnings, the CEO directly chooses to clear the
flag (give access back / dismiss as a false positive) or revoke the
user's access (suspend the account, which immediately cuts off their
ability to sign in or post) — or permanently delete the account,
which removes the row from Supabase entirely.
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
    """Revoke a user's access without deleting their data. Sets
    account_status='suspended', which blocks future login
    (core/auth.py checks this). Reversible via reinstate_user — use
    this when you want to be able to undo the action later. For a
    permanent removal, use delete_user instead.
    """
    client = get_shard_client(shard_id, use_service_role=True)
    now = datetime.now(timezone.utc).isoformat()

    client.table("parent_profiles").update({
        "account_status": "suspended",
        "suspended_at": now,
        "suspended_by": resolved_by,
    }).eq("id", parent_id).execute()

    if flag_id is not None:
        client.table("moderation_flags").update({
            "status": "actioned",
            "resolved_by": resolved_by,
            "resolved_at": now,
        }).eq("id", flag_id).execute()


def delete_user(shard_id: str, parent_id: str, flag_id: int | None = None, resolved_by: str = "ceo") -> None:
    """Permanently delete a parent's account and all data tied to it.
    This actually removes the row from Supabase (not just a status
    flag) — irreversible, unlike suspend_user.

    Deletion order matters: child rows referencing parent_profiles.id
    must go first, or the foreign key constraints would block the
    parent_profiles delete. chat_message_log and moderation_flags
    both reference parent_profiles with ON DELETE CASCADE in the
    schema, so Postgres would handle this automatically even without
    the explicit deletes below — but being explicit here means this
    function doesn't silently depend on that cascade still being
    configured correctly if the schema ever changes.
    """
    client = get_shard_client(shard_id, use_service_role=True)

    client.table("moderation_flags").delete().eq("parent_id", parent_id).execute()
    client.table("chat_message_log").delete().eq("sender_id", parent_id).execute()
    client.table("parent_profiles").delete().eq("id", parent_id).execute()

    if flag_id is not None:
        # The flag row itself was just deleted above (it referenced
        # this parent_id), so there's nothing further to update here —
        # this branch only exists for call-site symmetry with
        # suspend_user, in case a caller passes flag_id expecting the
        # same signature.
        pass


def reinstate_user(shard_id: str, parent_id: str) -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("parent_profiles").update({
        "account_status": "active",
        "suspended_at": None,
        "suspended_by": None,
        "flagged_reason": None,
        "flagged_at": None,
    }).eq("id", parent_id).execute()
