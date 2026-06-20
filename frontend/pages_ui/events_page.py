import streamlit as st

from events.events_service import list_events_in_window, _window_bounds


def render_events() -> None:
    profile = st.session_state.get("profile", {})
    shard_id = st.session_state.get("shard_id", "shard_001")

    st.markdown(
        """
        <section class="app-hero">
            <h1>Upcoming Events</h1>
            <p>Browse what's happening, three months at a time.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if "events_window_offset" not in st.session_state:
        st.session_state.events_window_offset = 0

    start, end = _window_bounds(st.session_state.events_window_offset)
    st.caption(f"Showing: {start.strftime('%B %Y')} – {end.strftime('%B %Y')}")

    events = list_events_in_window(
        shard_id,
        st.session_state.events_window_offset,
        age_band=profile.get("age_band"),
    )

    if not events:
        st.info("No events scheduled in this window yet.")
    else:
        for ev in events:
            st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
            st.markdown(f"### {ev['title']}")
            time_str = f" · {ev['event_time']}" if ev.get("event_time") else ""
            st.caption(f"{ev['event_date']}{time_str}")
            if ev.get("description"):
                st.write(ev["description"])
            st.markdown("</div>", unsafe_allow_html=True)

    left, mid, right = st.columns([1, 2, 1])
    with left:
        if st.button("← Earlier", disabled=st.session_state.events_window_offset <= 0):
            st.session_state.events_window_offset -= 1
            st.rerun()
    with right:
        if st.button("Later →"):
            st.session_state.events_window_offset += 1
            st.rerun()
