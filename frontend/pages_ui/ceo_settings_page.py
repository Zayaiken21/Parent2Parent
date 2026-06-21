import os

import streamlit as st

from core.supabase_clients import get_shard_client


def render_ceo_settings() -> None:
    shard_id = st.session_state.get("shard_id", "shard_001")

    st.markdown(
        """
        <section class="app-hero ceo">
            <h1>Settings</h1>
            <p>Shared access code and account overview.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.markdown("### Parent Access Code")
    code_set = bool(os.environ.get("PARENT_ACCESS_CODE", "").strip())
    if code_set:
        st.success("A shared access code is configured.")
        st.caption(
            "This code is set in your environment variables (PARENT_ACCESS_CODE) and "
            "isn't shown here for security — check your .env file or Streamlit Cloud "
            "secrets if you need a reminder. Give this code to parents so they can "
            "reach the Create Account screen. It only unlocks the signup form — every "
            "parent still sets their own unique username and password, so sharing the "
            "code never gives anyone access to another person's account."
        )
        if st.button("Change the code"):
            st.info(
                "Update PARENT_ACCESS_CODE in your .env file (local) or Streamlit Cloud "
                "Secrets, then redeploy. There's no in-app way to change it, by design — "
                "it keeps the code out of the database entirely."
            )
    else:
        st.error(
            "No PARENT_ACCESS_CODE is set. Parents won't be able to reach the signup "
            "form until you add PARENT_ACCESS_CODE to your environment variables."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Account Overview")

    client = get_shard_client(shard_id, use_service_role=True)
    resp = (
        client.table("parent_profiles")
        .select("account_status")
        .execute()
    )
    rows = resp.data or []

    total = len(rows)
    active = sum(1 for r in rows if r.get("account_status") == "active")
    suspended = sum(1 for r in rows if r.get("account_status") == "suspended")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total accounts", total)
    with col2:
        st.metric("Active", active)
    with col3:
        st.metric("Suspended", suspended)
