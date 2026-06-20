import streamlit as st

from config.age_bands import AGE_BANDS, GENDER_LABELS, room_label_for
from config.avatars import avatar_choices
from core.supabase_clients import get_shard_client


def render_profile() -> None:
    profile = st.session_state.get("profile", {})
    shard_id = st.session_state.get("shard_id", "shard_001")

    if not profile or "id" not in profile:
        # Defensive guard: this page should only ever be reached by a
        # logged-in parent with a real parent_profiles row. The CEO
        # role has no Profile tab at all (see frontend/nav.py), but if
        # this ever gets reached anyway (e.g. stale session state),
        # fail safely instead of crashing with a KeyError.
        st.info("No profile to show here.")
        return

    st.markdown(
        f"""
        <section class="app-hero">
            <h1>{profile.get('first_name', 'Your Profile')}</h1>
            <p>{room_label_for(profile.get('age_band','18_21'), profile.get('gender','male'))} community</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"![avatar](assets/avatars/{profile.get('avatar_key','default')}.svg)")
    with col2:
        st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
        st.write(f"**First name:** {profile.get('first_name','—')}")
        st.write(f"**Email:** {profile.get('email','—')}")
        band = profile.get("age_band", "")
        st.write(f"**Age range:** {AGE_BANDS.get(band, {}).get('label', band)}")
        st.write(f"**Chat room:** {room_label_for(band, profile.get('gender','male'))}" if band else "")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Choose Your Avatar")
    st.caption("Pick a style that matches your community — avatars are curated, not uploaded, to keep things simple and consistent.")

    choices = avatar_choices(profile.get("age_band", "18_21"), profile.get("gender", "male"))
    cols = st.columns(len(choices))
    for col, choice in zip(cols, choices):
        with col:
            st.markdown(f"![{choice['label']}](assets/avatars/{choice['key']}.svg)")
            is_current = choice["key"] == profile.get("avatar_key")
            if st.button("Selected ✓" if is_current else "Choose", key=f"avatar_{choice['key']}", disabled=is_current, use_container_width=True):
                client = get_shard_client(shard_id, use_service_role=True)
                client.table("parent_profiles").update({"avatar_key": choice["key"]}).eq("id", profile["id"]).execute()
                st.session_state.profile["avatar_key"] = choice["key"]
                st.rerun()

    st.divider()
    st.subheader("Event Emails")
    current_opt_in = profile.get("events_opt_in", False)
    new_opt_in = st.toggle("Send me upcoming event emails", value=current_opt_in)
    if new_opt_in != current_opt_in:
        client = get_shard_client(shard_id, use_service_role=True)
        client.table("parent_profiles").update({"events_opt_in": new_opt_in}).eq("id", profile["id"]).execute()
        st.session_state.profile["events_opt_in"] = new_opt_in
        st.toast("Preference saved.")
