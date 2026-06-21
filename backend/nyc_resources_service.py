"""
NYC Programs & Resources backend.

A CEO-curated directory of external programs, training apps, and
community resources. Persisted in Supabase (table: nyc_resources)
rather than local files, since Streamlit Cloud wipes local files on
every restart/redeploy -- anything the CEO adds through the app needs
to survive that, which only a real database does reliably.

This is explicitly a reference list, not an endorsement or sponsorship
relationship -- every page that displays this data must show the
disclaimer text (DISCLAIMER_TEXT below) alongside it.
"""
from __future__ import annotations

from core.supabase_clients import get_shard_client

CATEGORIES: dict[str, str] = {
    "fatherhood_parenting": "Fatherhood & Parenting Programs",
    "training_apps": "Training Apps",
    "community_resources": "Community Resources",
}

CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "fatherhood_parenting": "Organizations supporting fathers, mothers, and families -- parenting skills, advocacy, and family services.",
    "training_apps": "Apps and tools that help with job training and certifications, like CDL prep.",
    "community_resources": "Practical help -- clothing giveaways, food drives, and other community support.",
}

DISCLAIMER_TEXT = (
    "Parent2Parent is not sponsored by, affiliated with, or endorsed by any "
    "organization listed here. These are resources we've gathered to help "
    "mothers and fathers find support -- please verify details directly with "
    "each organization before relying on them."
)


class ResourceError(Exception):
    pass


def list_resources(shard_id: str, category: str | None = None) -> list[dict]:
    client = get_shard_client(shard_id, use_service_role=True)
    query = client.table("nyc_resources").select("*").order("name")
    if category:
        query = query.eq("category", category)
    resp = query.execute()
    return resp.data or []


def list_resources_by_category(shard_id: str) -> dict[str, list[dict]]:
    """All resources, grouped by category key -- convenient for
    rendering tabs/sections without the caller needing to bucket them.
    """
    all_resources = list_resources(shard_id)
    grouped: dict[str, list[dict]] = {key: [] for key in CATEGORIES}
    for r in all_resources:
        grouped.setdefault(r["category"], []).append(r)
    return grouped


def create_resource(
    shard_id: str,
    category: str,
    name: str,
    description: str = "",
    url: str = "",
    phone: str = "",
    address: str = "",
) -> dict:
    if category not in CATEGORIES:
        raise ResourceError(f"Unknown category: {category}")
    if not name.strip():
        raise ResourceError("Enter a name.")

    client = get_shard_client(shard_id, use_service_role=True)
    resp = client.table("nyc_resources").insert({
        "category": category,
        "name": name.strip(),
        "description": (description or "").strip() or None,
        "url": (url or "").strip() or None,
        "phone": (phone or "").strip() or None,
        "address": (address or "").strip() or None,
    }).execute()
    rows = resp.data or []
    if not rows:
        raise ResourceError("Could not create resource. Try again.")
    return rows[0]


def update_resource(shard_id: str, resource_id: int, **fields) -> dict:
    client = get_shard_client(shard_id, use_service_role=True)
    resp = client.table("nyc_resources").update(fields).eq("id", resource_id).execute()
    return (resp.data or [{}])[0]


def delete_resource(shard_id: str, resource_id: int) -> None:
    client = get_shard_client(shard_id, use_service_role=True)
    client.table("nyc_resources").delete().eq("id", resource_id).execute()
