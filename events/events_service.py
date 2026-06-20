"""
Events backend.

"3 months at a time" is implemented as: fetch a rolling window
covering the current month plus the next two, with pagination so a
user can page forward/back across windows (current, +3mo, +6mo...)
without ever loading the entire events table at once.
"""
from __future__ import annotations

import calendar
from datetime import date

from core.supabase_clients import get_shard_client
from backend.email_service import send_event_digest_email


def _add_months(d: date, months: int) -> date:
    """Stdlib-only month arithmetic (no python-dateutil dependency)."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _window_bounds(window_offset: int = 0) -> tuple[date, date]:
    """window_offset=0 -> this month through +2 months.
    window_offset=1 -> +3 through +5 months. etc."""
    today = date.today().replace(day=1)
    start = _add_months(today, 3 * window_offset)
    end_month_start = _add_months(start, 3)
    prev_month = _add_months(end_month_start, -1)
    last_day_prev = calendar.monthrange(prev_month.year, prev_month.month)[1]
    end = date(prev_month.year, prev_month.month, last_day_prev)
    return start, end


def list_events_in_window(shard_id: str, window_offset: int = 0, age_band: str | None = None) -> list[dict]:
    start, end = _window_bounds(window_offset)
    client = get_shard_client(shard_id, use_service_role=True)
    query = (
        client.table("events")
        .select("*")
        .gte("event_date", start.isoformat())
        .lte("event_date", end.isoformat())
        .order("event_date")
    )
    resp = query.execute()
    rows = resp.data or []
    if age_band:
        rows = [
            r for r in rows
            if not r.get("audience_age_bands") or age_band in r["audience_age_bands"]
        ]
    return rows


def create_event(
    shard_id: str,
    title: str,
    description: str,
    event_date: str,
    event_time: str | None = None,
    audience_age_bands: list[str] | None = None,
    image_url: str | None = None,
    source_url: str | None = None,
) -> dict:
    client = get_shard_client(shard_id, use_service_role=True)
    resp = client.table("events").insert({
        "title": title.strip(),
        "description": description.strip(),
        "event_date": event_date,
        "event_time": event_time,
        "audience_age_bands": audience_age_bands or None,
        "image_url": (image_url or "").strip() or None,
        "source_url": (source_url or "").strip() or None,
    }).execute()
    return (resp.data or [{}])[0]


def update_event(shard_id: str, event_id: int, **fields) -> dict:
    """Partial update — pass only the fields you want to change."""
    client = get_shard_client(shard_id, use_service_role=True)
    resp = client.table("events").update(fields).eq("id", event_id).execute()
    return (resp.data or [{}])[0]


def delete_event(shard_id: str, event_id: int) -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("events").delete().eq("id", event_id).execute()


def list_all_upcoming_events(shard_id: str, limit: int = 200) -> list[dict]:
    """Unfiltered, unwindowed list — used by the CEO's calendar view so
    they can see/manage everything at once rather than paging by
    3-month windows (that windowing is a parent-facing UX choice, not
    a CEO management constraint).
    """
    client = get_shard_client(shard_id, use_service_role=True)
    today = date.today().isoformat()
    resp = (
        client.table("events")
        .select("*")
        .gte("event_date", today)
        .order("event_date")
        .limit(limit)
        .execute()
    )
    return resp.data or []


def send_digest_to_opted_in_users(shard_id: str, window_offset: int = 0) -> int:
    """Send the event digest email to every user who opted in. Returns
    the number of emails sent. Intended to be called from a scheduled
    job (e.g. Streamlit Cloud cron-style trigger or an external
    scheduler hitting a small backend endpoint), not from request
    paths in the UI.
    """
    client = get_shard_client(shard_id, use_service_role=True)
    users_resp = (
        client.table("parent_profiles")
        .select("first_name, email, age_band")
        .eq("events_opt_in", True)
        .eq("account_status", "active")
        .execute()
    )
    users = users_resp.data or []
    if not users:
        return 0

    sent = 0
    for user in users:
        events = list_events_in_window(shard_id, window_offset, age_band=user.get("age_band"))
        if events:
            send_event_digest_email(user["email"], user["first_name"], events)
            sent += 1
    return sent
