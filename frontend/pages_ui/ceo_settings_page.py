import os

import streamlit as st

from config.age_bands import AGE_BANDS
from core.moderation import list_all_users, suspend_user, reinstate_user, delete_user


def _status_badge(status: str) -> str:
    if status == "active":
        return '<span class="p2p-badge success">✅ Active &amp; set up</span>'
    if status == "suspended":
        return '<span class="p2p-badge warning">⏸️ Suspended</span>'
    if status == "flagged":
        return '<span class="p2p-badge warm">🚩 Flagged</span>'
    return f'<span class="p2p-badge">{status}</span>'


def render_ceo_settings() -> None:
    shard_id = st.session_state.get("shard_id", "shard_001")

    st.markdown(
        """
        <section class="app-hero ceo">
            <h1>Settings</h1>
            <p>Shared access code and account management.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # ---------------- Access code status ----------------
    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.markdown("### Parent Access Code")
    code_set = bool(os.environ.get("PARENT_ACCESS_CODE", "").strip())
    if code_set:
        st.success("A shared access code is configured and active.")
        st.caption(
            "This code is set in your environment variables (PARENT_ACCESS_CODE) and "
            "isn't shown here for security — check your .env file or Streamlit Cloud "
            "secrets if you need a reminder. Give this code to parents so they can "
            "reach the Create Account screen. It only unlocks the signup form — every "
            "parent still sets their own unique username and password, so sharing the "
            "code never gives anyone access to another person's account."
        )
        st.caption(
            "To change it: update PARENT_ACCESS_CODE in your .env file (local) or "
            "Streamlit Cloud Secrets, then redeploy. There's no in-app way to change "
            "it, by design — it keeps the code out of the database entirely."
        )
    else:
        st.error(
            "No PARENT_ACCESS_CODE is set. Parents won't be able to reach the signup "
            "form until you add PARENT_ACCESS_CODE to your environment variables."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ---------------- User management ----------------
    users = list_all_users(shard_id)

    total = len(users)
    active = sum(1 for u in users if u.get("account_status") == "active")
    suspended = sum(1 for u in users if u.get("account_status") == "suspended")

    st.markdown("### Parent Accounts")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total accounts", total)
    with col2:
        st.metric("Active & set up", active)
    with col3:
        st.metric("Suspended", suspended)

    if not users:
        st.info("No parent accounts yet. Share the access code to get your first signups.")
        return

    search = st.text_input("Search by username or first name", placeholder="Type to filter...")
    if search.strip():
        needle = search.strip().lower()
        users = [
            u for u in users
            if needle in (u.get("username") or "").lower()
            or needle in (u.get("first_name") or "").lower()
        ]

    st.caption(f"Showing {len(users)} account(s).")

    for user in users:
        st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown(f"**{user.get('first_name', '—')}**  ·  @{user.get('username', '—')}")
            band = user.get("age_band", "")
            band_label = AGE_BANDS.get(band, {}).get("label", band)
            gender = user.get("gender", "")
            st.caption(f"{band_label} · {'Dads' if gender == 'male' else 'Moms'} room")
            if user.get("email"):
                st.caption(f"Email: {user['email']} · Event emails: {'on' if user.get('events_opt_in') else 'off'}")
            else:
                st.caption("No email on file")
            st.caption(f"Joined: {(user.get('created_at') or '')[:10]}")
        with c2:
            st.markdown(_status_badge(user.get("account_status", "active")), unsafe_allow_html=True)

        status = user.get("account_status")
        action_cols = st.columns(3)
        with action_cols[0]:
            if status == "suspended":
                if st.button("Reinstate", key=f"reinstate_{user['id']}", use_container_width=True):
                    reinstate_user(shard_id, user["id"])
                    st.rerun()
            else:
                if st.button("Suspend", key=f"suspend_{user['id']}", use_container_width=True):
                    suspend_user(shard_id, user["id"])
                    st.success("Account suspended.")
                    st.rerun()
        with action_cols[1]:
            confirm_key = f"confirm_settings_delete_{user['id']}"
            if st.session_state.get(confirm_key):
                if st.button("⚠️ Confirm delete", key=f"confirmed_settings_{user['id']}", type="primary", use_container_width=True):
                    delete_user(shard_id, user["id"])
                    st.session_state.pop(confirm_key, None)
                    st.success("Account permanently deleted.")
                    st.rerun()
            else:
                if st.button("Delete", key=f"settings_delete_{user['id']}", use_container_width=True):
                    st.session_state[confirm_key] = True
                    st.rerun()
        with action_cols[2]:
            if st.session_state.get(confirm_key):
                if st.button("Cancel", key=f"cancel_settings_delete_{user['id']}", use_container_width=True):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
