-- =================================================================
-- Parent2Parent — Core Schema (run on EACH Supabase shard)
-- =================================================================
-- This file is designed to be applied to shard #1 today and to any
-- future shard (#2, #3, ...) tomorrow with zero changes. The shard
-- a given user lives on is tracked separately in the CONTROL PLANE
-- project (see 002_shard_registry.sql) — that project never stores
-- chat or user PII, only "which shard is this email on."
-- =================================================================

create extension if not exists pgcrypto;

-- -----------------------------------------------------------------
-- 1. PARENT USERS  (replaces / extends your client_licenses table)
-- -----------------------------------------------------------------
-- We deliberately do NOT store last name, address, or any PII beyond
-- email + first name. Password handling is delegated to Supabase
-- Auth (auth.users) — this table is the app-level PROFILE that hangs
-- off of auth.users.id, not a parallel password store.
-- -----------------------------------------------------------------
create table if not exists public.parent_profiles (
    id uuid primary key references auth.users(id) on delete cascade,

    first_name text not null,
    email text not null,                       -- mirrors auth.users.email for easy joins/admin queries
    avatar_key text not null default 'default', -- e.g. 'band_18_21_female_01' -> maps to a local/static icon, never a free-form upload

    gender text not null check (gender in ('male', 'female')),
    birth_year int not null,                    -- used to derive age band; we store year only (not full DOB) to minimize PII
    age_band text not null,                     -- derived + stored, e.g. '18_21' — see CHECK below

    security_question_key text not null,        -- which canned question was asked at signup for their claimed age band
    security_answer_hash text not null,          -- hashed, never plaintext

    account_status text not null default 'active'
        check (account_status in ('active', 'flagged', 'suspended', 'deleted')),
    flagged_reason text,
    flagged_at timestamptz,
    suspended_at timestamptz,
    suspended_by text,                          -- 'ceo' (kept generic in case of future admin roles)

    events_opt_in boolean not null default false,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    constraint chk_age_band check (
        age_band in ('11_13','13_15','15_17','18_21','21_23','23_25','25_27')
    )
);

create index if not exists idx_parent_profiles_age_band_gender
    on public.parent_profiles(age_band, gender);
create index if not exists idx_parent_profiles_status
    on public.parent_profiles(account_status);
create unique index if not exists idx_parent_profiles_email_lower
    on public.parent_profiles(lower(email));

alter table public.parent_profiles enable row level security;

-- A user may read/update only their own profile.
create policy "parent_profiles_select_own"
    on public.parent_profiles for select
    using (auth.uid() = id);

create policy "parent_profiles_update_own"
    on public.parent_profiles for update
    using (auth.uid() = id);

-- Inserts happen via the signup flow using the authenticated user's own id.
create policy "parent_profiles_insert_own"
    on public.parent_profiles for insert
    with check (auth.uid() = id);

-- NOTE: CEO oversight reads happen through the service_role key from the
-- backend (bypasses RLS by design), never through an RLS "is ceo" policy
-- tied to a password-in-a-table. The CEO identity lives in env vars, not
-- in this table, per your requirement.


-- -----------------------------------------------------------------
-- 2. CHAT ROOMS  (derived, not user-creatable)
-- -----------------------------------------------------------------
-- Exactly 14 rooms total: 7 age bands x 2 genders. Rows are seeded
-- once below and the app never lets a user create a new one.
-- -----------------------------------------------------------------
create table if not exists public.chat_rooms (
    room_key text primary key,        -- e.g. '18_21_female'
    age_band text not null,
    gender text not null check (gender in ('male', 'female')),
    display_label text not null       -- e.g. '18–21 (Women)'
);

insert into public.chat_rooms (room_key, age_band, gender, display_label) values
    ('11_13_male',   '11_13', 'male',   '11–13 (Dads)'),
    ('11_13_female', '11_13', 'female', '11–13 (Moms)'),
    ('13_15_male',   '13_15', 'male',   '13–15 (Dads)'),
    ('13_15_female', '13_15', 'female', '13–15 (Moms)'),
    ('15_17_male',   '15_17', 'male',   '15–17 (Dads)'),
    ('15_17_female', '15_17', 'female', '15–17 (Moms)'),
    ('18_21_male',   '18_21', 'male',   '18–21 (Dads)'),
    ('18_21_female', '18_21', 'female', '18–21 (Moms)'),
    ('21_23_male',   '21_23', 'male',   '21–23 (Dads)'),
    ('21_23_female', '21_23', 'female', '21–23 (Moms)'),
    ('23_25_male',   '23_25', 'male',   '23–25 (Dads)'),
    ('23_25_female', '23_25', 'female', '23–25 (Moms)'),
    ('25_27_male',   '25_27', 'male',   '25–27 (Dads)'),
    ('25_27_female', '25_27', 'female', '25–27 (Moms)')
on conflict (room_key) do nothing;


-- -----------------------------------------------------------------
-- 3. CHAT MESSAGE LOG (for moderation only — NOT the live transport)
-- -----------------------------------------------------------------
-- Live message delivery happens over Supabase Realtime Broadcast,
-- which never touches a table (per your "don't store live chat,
-- don't run out of storage" requirement). This table is a thin,
-- auto-expiring AUDIT log so the CEO can review flagged messages
-- and so the filter has something to log a hit against. A daily
-- job (see 003_retention.sql) purges rows past retention_days.
-- -----------------------------------------------------------------
create table if not exists public.chat_message_log (
    id bigint generated by default as identity primary key,
    room_key text not null references public.chat_rooms(room_key),
    sender_id uuid not null references public.parent_profiles(id) on delete cascade,
    sender_first_name text not null,   -- denormalized snapshot, first name only
    message_text text not null,
    was_filtered boolean not null default false,
    filter_hits text[],                 -- which categories tripped, not the raw banned words
    created_at timestamptz not null default now()
);

create index if not exists idx_chat_log_room_created
    on public.chat_message_log(room_key, created_at desc);
create index if not exists idx_chat_log_flagged
    on public.chat_message_log(was_filtered) where was_filtered = true;

alter table public.chat_message_log enable row level security;
-- No public select/insert policies: all writes/reads to this audit
-- table go through the backend using the service_role key. Regular
-- users never query this table directly — they only see Realtime
-- broadcast events, which is how privacy + storage limits are kept.


-- -----------------------------------------------------------------
-- 4. MODERATION QUEUE  (what the CEO sees under "needs review")
-- -----------------------------------------------------------------
create table if not exists public.moderation_flags (
    id bigint generated by default as identity primary key,
    parent_id uuid not null references public.parent_profiles(id) on delete cascade,
    room_key text references public.chat_rooms(room_key),
    chat_message_log_id bigint references public.chat_message_log(id) on delete set null,
    reason text not null,              -- e.g. 'profanity_filter', 'explicit_content', 'manual_report'
    detail text,                       -- short human-readable context for the CEO
    status text not null default 'open' check (status in ('open', 'cleared', 'actioned')),
    resolved_by text,
    resolved_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_mod_flags_status on public.moderation_flags(status);
alter table public.moderation_flags enable row level security;
-- Service-role only, same rationale as chat_message_log.


-- -----------------------------------------------------------------
-- 5. EVENTS  (rolling 3-month windows, opt-in email digest)
-- -----------------------------------------------------------------
create table if not exists public.events (
    id bigint generated by default as identity primary key,
    title text not null,
    description text,
    event_date date not null,
    event_time text,                   -- display string, e.g. '6:00 PM ET'
    audience_age_bands text[],          -- null/empty = all bands
    created_at timestamptz not null default now()
);

create index if not exists idx_events_date on public.events(event_date);
alter table public.events enable row level security;

create policy "events_select_all_authenticated"
    on public.events for select
    using (auth.role() = 'authenticated');
-- Inserts/updates are service_role only (CEO creates events via backend).


-- -----------------------------------------------------------------
-- 6. PASSWORD / EMAIL VERIFICATION CODES (6-digit, short-lived)
-- -----------------------------------------------------------------
-- Used for both "verify your email at signup" and "reset password."
-- We store a HASH of the code, never the code itself.
-- -----------------------------------------------------------------
create table if not exists public.verification_codes (
    id bigint generated by default as identity primary key,
    email text not null,
    code_hash text not null,
    purpose text not null check (purpose in ('signup_verify', 'password_reset')),
    expires_at timestamptz not null,
    consumed_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_verif_codes_email on public.verification_codes(lower(email));
alter table public.verification_codes enable row level security;
-- Service-role only — never exposed to the client directly.


-- -----------------------------------------------------------------
-- 7. updated_at trigger helper
-- -----------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_parent_profiles_updated_at on public.parent_profiles;
create trigger trg_parent_profiles_updated_at
    before update on public.parent_profiles
    for each row execute function public.set_updated_at();
