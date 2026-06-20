-- =================================================================
-- Parent2Parent — Shard Registry (run ONCE, on the CONTROL PLANE
-- Supabase project — a separate, small project from your data shards)
-- =================================================================
-- Why a separate project: when you're at 1M+ users across multiple
-- Supabase projects (shard 1, shard 2, shard 3, ...), something has
-- to answer "which shard does this email live on?" BEFORE you know
-- which shard's connection string to even use. That lookup table
-- has to live somewhere that isn't itself sharded. This tiny project
-- holds NO chat data, NO passwords, NO PII beyond email — just a
-- routing table. Treat it like DNS for your user base.
--
-- Until you actually need shard 2, this project can be the ONLY
-- Supabase project you have, and "shard_001" is just your one and
-- only database. Nothing in the app code needs to change later —
-- you only ever add rows here and a matching connection profile in
-- config/shards.py.
-- =================================================================

create table if not exists public.shard_registry (
    email text primary key,
    shard_id text not null,           -- e.g. 'shard_001', 'shard_002'
    created_at timestamptz not null default now()
);

create index if not exists idx_shard_registry_shard_id
    on public.shard_registry(shard_id);

alter table public.shard_registry enable row level security;
-- Service-role only. No anon/authenticated policies — this table is
-- read exclusively by the backend router before a session is
-- established for a given shard.

-- -----------------------------------------------------------------
-- Optional: a tiny table to track shard capacity so the router can
-- pick the least-full active shard when a brand-new email signs up.
-- -----------------------------------------------------------------
create table if not exists public.shard_capacity (
    shard_id text primary key,
    label text not null,              -- human label, e.g. 'Shard 1 (us-east)'
    is_active_for_signup boolean not null default true,
    approx_user_count int not null default 0,
    soft_cap int not null default 150000,  -- comfortably under Supabase practical limits per project
    created_at timestamptz not null default now()
);

insert into public.shard_capacity (shard_id, label, is_active_for_signup, soft_cap)
values ('shard_001', 'Shard 1 (primary)', true, 150000)
on conflict (shard_id) do nothing;
