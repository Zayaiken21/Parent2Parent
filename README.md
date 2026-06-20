# Parent2Parent

Real people. Real problems. Real education.

A community app for parents raising kids 0–21, with age-banded peer
chat, a child-development curriculum, connection/structure tools,
events, and CEO moderation oversight.

## Project structure

```
core/          auth, Supabase client/shard routing, chat backend, moderation
profiles/      child development curriculum content (0–21)
events/        rolling 3-month events logic + email digests
frontend/      Streamlit pages (login, profile, events, chat, etc.)
backend/       email sending (Resend)
styles/        theme + global CSS
config/        age bands, avatars, CEO settings, shard config, content filter
sql/           run these in order on your Supabase project(s)
assets/avatars placeholder avatar icon set (swap with real art anytime)
```

## 1. Set up Supabase

1. Create a Supabase project (this is "shard 1" — you only need one
   to start; the app supports adding more later without code changes).
2. In the SQL Editor, run, in order:
   - `sql/001_core_schema.sql`
   - `sql/003_retention.sql` (and optionally register the cron job
     described in its comments)
3. **Important:** Auth -> Providers -> Email — make sure "Confirm
   email" can be left as-is; this app handles its own 6-digit
   verification before calling `auth.admin.create_user(..., email_confirm=True)`,
   so Supabase won't send its own duplicate confirmation email.
4. Copy your Project URL, anon key, and service_role key from
   Project Settings -> API.

You do **not** need to run `sql/002_shard_registry.sql` yet — that's
for a *second*, separate, tiny Supabase project you'd only create
once you're scaling past one project's capacity.

## 2. Set up email (Resend)

1. Create a free account at https://resend.com
2. Verify a sending domain (or use their test domain while developing)
3. Grab an API key

If you skip this, the app still runs — verification codes get logged
to the console instead of emailed, which is fine for local testing
but not for real users.

## 3. Configure secrets

**Local development:** copy `.env.example` to `.env` and fill in real
values. `.env` is already in `.gitignore`.

**Streamlit Cloud:** open your app -> Settings -> Secrets, and paste
in the contents of `.streamlit/secrets.toml.example` with real values.
`bootstrap.py` automatically bridges Streamlit Cloud secrets into the
same environment-variable interface the rest of the app uses, so no
code changes are needed between local and cloud.

## 4. Install & run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 5. Deploy to Streamlit Cloud

1. Push this repo to GitHub (`.env` will NOT be pushed — verify it's
   gitignored before your first commit).
2. On share.streamlit.io, create a new app pointing at this repo,
   main file `streamlit_app.py`.
3. Paste secrets as described in step 3.
4. Deploy.

If a deploy doesn't reflect your latest code, it's almost always a
GitHub push gap, not a code bug — confirm `git push` actually went
through before debugging the app itself.

## 6. CEO access

The CEO account is **not** a database row — it's two environment
variables, `CEO_EMAIL` and `CEO_PASSWORD`. Whoever has those values
can sign in via the "CEO Access" tab on the login screen and gets:
- a combined view across every age/gender chat room
- the moderation queue (clear a flag, or revoke a user's access)

## 7. Content filter

`config/blocked_terms.txt` ships lightly seeded with example terms in
each category (`profanity`, `explicit_sexual`, `harassment`,
`self_harm_risk`). **You should expand this list yourself** — exact
wording is a judgment call for your community, not something to bake
into shared code. The matching logic already handles basic spacing
tricks and leetspeak substitutions, so you don't need to list every
variant of a word — the base word is usually enough.

One category, `self_harm_risk`, is handled differently on purpose:
those messages are blocked from the room and the user sees a crisis
resource (988 Suicide & Crisis Lifeline) instead of a generic "your
message was blocked" notice, and the flag is marked urgent rather
than being a strike toward suspension. Don't move terms out of that
category without keeping that behavior somewhere — auto-suspending
someone who may be in crisis is the wrong response.

## 8. Scaling past one Supabase project

When you're approaching ~150k users on one project:
1. Create a new (tiny) "control plane" Supabase project and run
   `sql/002_shard_registry.sql` on it.
2. Create Supabase project #2 ("shard 2") and run `001` + `003` on it,
   same as shard 1.
3. Add `SHARD_2_SUPABASE_*` and `CONTROL_SUPABASE_*` env vars.

No application code changes are required — `core/supabase_clients.py`
already reads however many `SHARD_N_*` env vars exist.

## Known gaps / next steps

- Avatars are generated placeholder SVGs (geometric shapes + a
  letter), not final art — swap files in `assets/avatars/` anytime,
  filenames are documented in `config/avatars.py`.
- The event-digest email send (`events/events_service.py ->
  send_digest_to_opted_in_users`) is written to be called from a
  scheduled job, but no scheduler is wired up yet — you'd trigger it
  via a cron-like service (e.g. GitHub Actions on a schedule, or
  Supabase Edge Function cron) hitting a small script that calls it.
- This has been checked for syntax errors and internal import
  correctness, but has **not** been run end-to-end against a live
  Supabase project from this environment (no network access here) —
  test it against your real project before treating it as
  production-verified.
