"""
Chat backend.

IMPORTANT: an earlier version of this module tried to use Supabase
Realtime Broadcast for instant message delivery. That doesn't work —
the Supabase Python SYNC client (which this whole app uses) raises
NotImplementedError for any realtime/channel call; Realtime is only
available in Supabase's ASYNC Python client, which would require a
much larger rework of the whole app (every Streamlit page would need
to run inside an event loop). So instead: messages are written to
chat_message_log (already required for moderation anyway) and the
chat page re-fetches that log every few seconds via a refresh timer.
This means a few seconds of delay instead of instant push — accepted
tradeoff, confirmed acceptable, much simpler and it actually works.

What we DO persist:
  - chat_message_log: every message (filtered or not), used both as
    the moderation audit trail AND as the actual chat history source
    now that there's no separate broadcast channel. Purged after N
    days by sql/003_retention.sql so storage doesn't grow forever.
  - moderation_flags: durable until a human clears/actions them
"""
from __future__ import annotations

from core.supabase_clients import get_shard_client
from config.content_filter import check_message

CRISIS_RESPONSE_TEXT = (
    "We're not able to post that message, but we want you to know support is "
    "available right now. If you or someone you know is in crisis, you can call "
    "or text 988 (Suicide & Crisis Lifeline) anytime, free and confidential. "
    "You don't have to go through this alone."
)


class ChatError(Exception):
    pass


def send_message(
    shard_id: str,
    room_key: str,
    sender_id: str,
    sender_first_name: str,
    message_text: str,
    sender_avatar_key: str | None = None,
) -> dict:
    """Filter and log a message. Returns a dict describing the outcome
    so the UI knows whether to show the message, a block notice, or
    the crisis-support notice. There is no separate broadcast step —
    the chat page re-reads chat_message_log on its own refresh timer.
    """
    message_text = message_text.strip()
    if not message_text:
        raise ChatError("Message is empty.")
    if len(message_text) > 1000:
        raise ChatError("Message is too long (max 1000 characters).")

    result = check_message(message_text)
    client = get_shard_client(shard_id, use_service_role=True)

    if result.blocked:
        # Log it regardless of category — the CEO needs visibility either way.
        log_resp = client.table("chat_message_log").insert({
            "room_key": room_key,
            "sender_id": sender_id,
            "sender_first_name": sender_first_name,
            "sender_avatar_key": sender_avatar_key,
            "message_text": message_text,
            "was_filtered": True,
            "filter_hits": result.categories,
        }).execute()
        log_row = (log_resp.data or [{}])[0]

        is_crisis = "self_harm_risk" in result.categories

        client.table("moderation_flags").insert({
            "parent_id": sender_id,
            "room_key": room_key,
            "chat_message_log_id": log_row.get("id"),
            "reason": "self_harm_risk" if is_crisis else "content_filter",
            "detail": f"Categories: {', '.join(result.categories)}",
            "status": "open",
        }).execute()

        if is_crisis:
            return {"delivered": False, "crisis": True, "display_text": CRISIS_RESPONSE_TEXT}
        return {"delivered": False, "crisis": False, "display_text": "That message can't be sent. It's been sent to moderators for review."}

    # Clean message: log it. This IS the chat history now (see module
    # docstring) — no separate broadcast call.
    client.table("chat_message_log").insert({
        "room_key": room_key,
        "sender_id": sender_id,
        "sender_first_name": sender_first_name,
        "sender_avatar_key": sender_avatar_key,
        "message_text": message_text,
        "was_filtered": False,
    }).execute()

    return {"delivered": True, "crisis": False, "display_text": message_text}


def fetch_recent_history(shard_id: str, room_key: str, limit: int = 30) -> list[dict]:
    """Recent clean messages for a room — this is now the only source
    of chat history (no realtime broadcast), so the chat page calls
    this on every rerun/refresh to pick up new messages.
    """
    client = get_shard_client(shard_id, use_service_role=True)
    resp = (
        client.table("chat_message_log")
        .select("sender_first_name, sender_avatar_key, message_text, created_at")
        .eq("room_key", room_key)
        .eq("was_filtered", False)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    rows = resp.data or []
    return list(reversed(rows))


def ceo_fetch_all_rooms_recent(shard_id: str, limit_per_room: int = 20) -> dict[str, list[dict]]:
    """CEO oversight view: recent messages across every room, grouped
    by room_key, so the CEO sees 'one chat per room' while regular
    users only ever see their own single room.
    """
    client = get_shard_client(shard_id, use_service_role=True)
    resp = (
        client.table("chat_message_log")
        .select("room_key, sender_first_name, sender_avatar_key, message_text, was_filtered, filter_hits, created_at")
        .order("created_at", desc=True)
        .limit(limit_per_room * 20)  # generous fetch, then bucket below
        .execute()
    )
    rows = resp.data or []
    by_room: dict[str, list[dict]] = {}
    for row in rows:
        bucket = by_room.setdefault(row["room_key"], [])
        if len(bucket) < limit_per_room:
            bucket.append(row)
    return by_room
