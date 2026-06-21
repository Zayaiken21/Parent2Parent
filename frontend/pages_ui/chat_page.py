import streamlit as st

from config.age_bands import room_key_for, room_label_for
from core.chat_backend import send_message, fetch_recent_history, ceo_fetch_all_rooms_recent, ChatError
from core.moderation import list_open_flags, clear_flag, suspend_user, delete_user

# A small rotating palette so different senders get visually distinct
# initial badges without needing to store/fetch a real avatar per
# message (chat_message_log only keeps a denormalized first-name
# snapshot, not a live avatar reference — see core/chat_backend.py).
_INITIAL_COLORS = ["#5B3CC4", "#0F7A70", "#C73838", "#E8A33D", "#3B2680", "#8B6CE0"]


def _initial_badge_color(name: str) -> str:
    if not name:
        return _INITIAL_COLORS[0]
    return _INITIAL_COLORS[sum(ord(c) for c in name) % len(_INITIAL_COLORS)]


def _render_message_list(messages: list[dict]) -> None:
    if not messages:
        st.caption("No messages yet. Say hello! 👋")
        return
    for msg in messages:
        name = msg.get("sender_first_name", "Parent")
        initial = (name or "P")[0].upper()
        color = _initial_badge_color(name)
        st.markdown(
            f"""
            <div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:2px;">
                <div style="flex-shrink:0; width:30px; height:30px; border-radius:50%;
                            background:{color}; color:#fff; display:flex; align-items:center;
                            justify-content:center; font-weight:800; font-size:13px;
                            box-shadow:0 2px 6px rgba(0,0,0,0.15);">
                    {initial}
                </div>
                <div class="p2p-chat-bubble" style="border-left-color:{color};">
                    <span class="sender">{name}</span>
                    {msg.get('message_text','')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_user_chat() -> None:
    profile = st.session_state.get("profile", {})
    shard_id = st.session_state.get("shard_id", "shard_001")
    room_key = room_key_for(profile.get("age_band", "18_21"), profile.get("gender", "male"))

    st.markdown(
        f"""
        <section class="app-hero">
            <h1>{room_label_for(profile.get('age_band','18_21'), profile.get('gender','male'))}</h1>
            <p>💬 Your community chat — just first names, just your age range.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    history = fetch_recent_history(shard_id, room_key)
    chat_container = st.container(height=420)
    with chat_container:
        _render_message_list(history)

    with st.form("chat_send_form", clear_on_submit=True):
        text = st.text_input("Message", label_visibility="collapsed", placeholder="Type a message...")
        sent = st.form_submit_button("Send 💬", use_container_width=True, type="primary")
        if sent and text.strip():
            try:
                result = send_message(
                    shard_id=shard_id,
                    room_key=room_key,
                    sender_id=profile["id"],
                    sender_first_name=profile.get("first_name", "Parent"),
                    message_text=text,
                )
                if result["crisis"]:
                    st.warning(result["display_text"])
                elif not result["delivered"]:
                    st.error(result["display_text"])
                st.rerun()
            except ChatError as exc:
                st.error(str(exc))

    st.caption("Messages are filtered for explicit content. Flagged messages are reviewed and are not shown to other users.")


def _render_ceo_chat_oversight() -> None:
    shard_id = st.session_state.get("shard_id", "shard_001")

    st.markdown(
        """
        <section class="app-hero ceo">
            <h1>Chat Oversight</h1>
            <p>All community rooms, in one place.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    tab_rooms, tab_flags = st.tabs(["All Rooms", "Moderation Queue"])

    with tab_rooms:
        by_room = ceo_fetch_all_rooms_recent(shard_id)
        if not by_room:
            st.info("No chat activity yet.")
        for room_key, messages in sorted(by_room.items()):
            with st.expander(room_key.replace("_", " ").title(), expanded=False):
                for msg in messages:
                    flag_note = ""
                    if msg.get("was_filtered"):
                        flag_note = f" 🚩 _{', '.join(msg.get('filter_hits') or [])}_"
                    st.markdown(
                        f"**{msg['sender_first_name']}**{flag_note}: {msg['message_text']}  \n"
                        f"<span style='color:#8a93a1;font-size:11px;'>{msg['created_at']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.divider()

    with tab_flags:
        flags = list_open_flags(shard_id)
        if not flags:
            st.success("No open moderation flags. 🎉")
        for flag in flags:
            parent = flag.get("parent_profiles") or {}
            is_crisis = flag.get("reason") == "self_harm_risk"
            badge = "🆘 URGENT — possible self-harm risk" if is_crisis else f"🚩 {flag.get('reason')}"
            st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
            st.markdown(f"**{badge}**")
            st.write(f"User: {parent.get('first_name','Unknown')} ({parent.get('email','—')})")
            st.write(f"Age range: {parent.get('age_band','—')} · Status: {parent.get('account_status','—')}")
            if flag.get("detail"):
                st.caption(flag["detail"])
            st.caption(f"Flagged: {flag.get('created_at','')}")

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Clear flag", key=f"clear_{flag['id']}", use_container_width=True):
                    clear_flag(shard_id, flag["id"])
                    st.rerun()
            with c2:
                if st.button("Revoke access", key=f"revoke_{flag['id']}", use_container_width=True):
                    suspend_user(shard_id, flag["parent_id"], flag_id=flag["id"])
                    st.success("User access revoked. Account is suspended but data is kept — reversible.")
                    st.rerun()
            with c3:
                confirm_key = f"confirm_delete_{flag['id']}"
                if st.session_state.get(confirm_key):
                    if st.button("⚠️ Confirm delete", key=f"confirmed_{flag['id']}", type="primary", use_container_width=True):
                        delete_user(shard_id, flag["parent_id"], flag_id=flag["id"])
                        st.session_state.pop(confirm_key, None)
                        st.success("Account permanently deleted.")
                        st.rerun()
                else:
                    if st.button("Delete account", key=f"delete_{flag['id']}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_chat() -> None:
    role = st.session_state.get("role")
    if role == "ceo":
        _render_ceo_chat_oversight()
    else:
        _render_user_chat()
