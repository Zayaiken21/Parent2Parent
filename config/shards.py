"""
Shard connection profiles. Today this almost certainly has exactly
ONE entry ("shard_001"). When you outgrow one Supabase project,
spin up a new Supabase project, add its credentials as a new shard
here (via env vars, same pattern), and add a row to shard_capacity
in the control-plane project. No other code changes.

Required env vars per shard (1-indexed by SHARD_N):
    SHARD_1_SUPABASE_URL
    SHARD_1_SUPABASE_ANON_KEY
    SHARD_1_SUPABASE_SERVICE_ROLE_KEY
    SHARD_2_SUPABASE_URL          (only once you add shard 2)
    ...

Plus the control-plane project (separate, tiny project, see
sql/002_shard_registry.sql):
    CONTROL_SUPABASE_URL
    CONTROL_SUPABASE_SERVICE_ROLE_KEY
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ShardProfile:
    shard_id: str
    url: str
    anon_key: str
    service_role_key: str


def _load_shard(n: int) -> ShardProfile | None:
    url = os.environ.get(f"SHARD_{n}_SUPABASE_URL")
    if not url:
        return None
    return ShardProfile(
        shard_id=f"shard_{n:03d}",
        url=url,
        anon_key=os.environ.get(f"SHARD_{n}_SUPABASE_ANON_KEY", ""),
        service_role_key=os.environ.get(f"SHARD_{n}_SUPABASE_SERVICE_ROLE_KEY", ""),
    )


def load_all_shards() -> dict[str, ShardProfile]:
    """Scan env vars for SHARD_1, SHARD_2, ... up to a generous ceiling
    so adding a new shard is just adding env vars — no code edits."""
    shards: dict[str, ShardProfile] = {}
    for n in range(1, 51):  # supports up to 50 shards (~7.5M users at 150k/shard) without touching this file
        profile = _load_shard(n)
        if profile:
            shards[profile.shard_id] = profile
    return shards


CONTROL_PLANE_URL = os.environ.get("CONTROL_SUPABASE_URL", "")
CONTROL_PLANE_SERVICE_KEY = os.environ.get("CONTROL_SUPABASE_SERVICE_ROLE_KEY", "")
