import streamlit as st

from core.parent_tokens import generate_token, list_tokens, deactivate_token, TokenError


def render_ceo_settings() -> None:
    shard_id = st.session_state.get("shard_id", "shard_001")

    st.markdown(
        """
        <section class="app-hero ceo">
            <h1>Settings</h1>
            <p>Generate and manage parent access tokens.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.markdown("### Generate a New Access Token")
    st.caption("Give this 6-character code to a parent. They'll use it once to create their account.")
    if st.button("Generate Token", type="primary", use_container_width=True):
        try:
            token = generate_token(shard_id)
            st.success("New token created:")
            st.code(token, language=None)
        except TokenError as exc:
            st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### All Tokens")

    tokens = list_tokens(shard_id)
    if not tokens:
        st.info("No tokens generated yet.")
        return

    for t in tokens:
        cols = st.columns([2, 2, 2, 1])
        with cols[0]:
            st.code(t["token"], language=None)
        with cols[1]:
            if t.get("redeemed"):
                st.markdown('<span class="p2p-badge success">Redeemed</span>', unsafe_allow_html=True)
            elif not t.get("active", True):
                st.markdown('<span class="p2p-badge warning">Inactive</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="p2p-badge">Available</span>', unsafe_allow_html=True)
        with cols[2]:
            st.caption(f"Created: {t.get('created_at', '')[:10]}")
        with cols[3]:
            if t.get("active", True) and not t.get("redeemed"):
                if st.button("Deactivate", key=f"deactivate_{t['token']}", use_container_width=True):
                    deactivate_token(t["token"], shard_id)
                    st.rerun()
