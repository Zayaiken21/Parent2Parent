import streamlit as st

from config.age_bands import AGE_BANDS, GENDER_LABELS, room_label_for
from config.avatars import avatar_choices
from core.supabase_clients import get_shard_client
from styles.avatar_render import avatar_img_html


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

    band = profile.get("age_band", "")
    gender = profile.get("gender", "male")
    band_label = AGE_BANDS.get(band, {}).get("label", band)
    avatar_path = f"assets/avatars/{profile.get('avatar_key', 'default')}.svg"
    avatar_html = avatar_img_html(avatar_path, size_px=100)

    # ---------------- Profile header: framed avatar front and center ----------------
    st.markdown(
        f"""
        <section class="p2p-profile-header">
            <div class="p2p-avatar-frame">{avatar_html}</div>
            <p class="p2p-profile-name">{profile.get('first_name', 'Your Profile')}</p>
            <p class="p2p-profile-sub">@{profile.get('username', '—')} &middot; {room_label_for(band, gender)}</p>
            <div class="p2p-profile-badges">
                <span class="p2p-badge on-gradient">{band_label}</span>
                <span class="p2p-badge on-gradient">{GENDER_LABELS.get(gender, '')}</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.write(f"**First name:** {profile.get('first_name','—')}")
    st.write(f"**Username:** {profile.get('username','—')}")
    st.write(f"**Email:** {profile.get('email') or '— (none set)'}")
    st.write(f"**Age range:** {band_label}")
    st.write(f"**Chat room:** {room_label_for(band, gender)}" if band else "")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Choose Your Avatar")
    st.caption("Pick a style that matches your community — avatars are curated, not uploaded, to keep things simple and consistent.")

    choices = avatar_choices(band or "18_21", gender)
    cols = st.columns(len(choices))
    for col, choice in zip(cols, choices):
        with col:
            is_current = choice["key"] == profile.get("avatar_key")
            ring = "border:3px solid #5B3CC4;" if is_current else "border:3px solid transparent;"
            choice_html = avatar_img_html(choice["file"], size_px=64)
            st.markdown(
                f'<div style="text-align:center;padding:4px;border-radius:50%;{ring}">{choice_html}</div>',
                unsafe_allow_html=True,
            )
            if st.button("Selected ✓" if is_current else "Choose", key=f"avatar_{choice['key']}", disabled=is_current, use_container_width=True):
                client = get_shard_client(shard_id, use_service_role=True)
                client.table("parent_profiles").update({"avatar_key": choice["key"]}).eq("id", profile["id"]).execute()
                st.session_state.profile["avatar_key"] = choice["key"]
                st.rerun()

    st.divider()
    st.subheader("Event Emails")
    current_email = profile.get("email") or ""
    if not current_email:
        st.caption("Add an email to receive upcoming event details. This is never used for login.")
        new_email = st.text_input("Email", key="profile_email_input", placeholder="you@example.com")
        if st.button("Save Email", use_container_width=True):
            if new_email.strip():
                client = get_shard_client(shard_id, use_service_role=True)
                client.table("parent_profiles").update({"email": new_email.strip().lower()}).eq("id", profile["id"]).execute()
                st.session_state.profile["email"] = new_email.strip().lower()
                st.rerun()
    else:
        st.caption(f"Events will be sent to: {current_email}")

    current_opt_in = profile.get("events_opt_in", False)
    new_opt_in = st.toggle(
        "Send me upcoming event emails",
        value=current_opt_in,
        disabled=not current_email,
        help=None if current_email else "Add an email above first.",
    )
    if new_opt_in != current_opt_in:
        client = get_shard_client(shard_id, use_service_role=True)
        client.table("parent_profiles").update({"events_opt_in": new_opt_in}).eq("id", profile["id"]).execute()
        st.session_state.profile["events_opt_in"] = new_opt_in
        st.toast("Preference saved.")
