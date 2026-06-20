"""
Main navigation: 4 sticky primary tabs (Profile, Events, Chat, Logout)
plus a secondary "More" sub-menu that expands to reveal the deeper
curriculum/parenting tools, so the primary bar stays uncluttered.
"""
import streamlit as st


PRIMARY_TABS = ["Profile", "Events", "Chat", "Logout"]

SUBMENU_ITEMS = {
    "Curriculum": "Browse the 0–21 child development guide",
    "Connection Builder": "Daily prompts for building emotional connection",
    "Structure & Routines": "Tools for building healthy household structure",
    "CDL Study Tools": "Trucking/CDL study companion",  # kept per existing project scope
}


def render_bottom_nav(active_page: str) -> str | None:
    """Renders the 4 sticky tabs. Returns the tab name if a new tab
    was clicked this run, else None. Caller is responsible for
    updating st.session_state.active_page and rerunning.
    """
    cols = st.columns(4)
    clicked = None
    icons = {"Profile": "👤", "Events": "📅", "Chat": "💬", "Logout": "🚪"}
    for col, tab in zip(cols, PRIMARY_TABS):
        with col:
            is_active = tab == active_page
            label = f"**{icons[tab]} {tab}**" if is_active else f"{icons[tab]} {tab}"
            if st.button(label, key=f"nav_{tab}", use_container_width=True):
                clicked = tab
    return clicked


def render_submenu(active_subpage: str | None) -> str | None:
    """Pro-style expandable secondary menu for deeper tools. Returns
    the clicked item name, or None.
    """
    clicked = None
    with st.expander("⚙️  More Parenting Tools", expanded=bool(active_subpage)):
        for item, desc in SUBMENU_ITEMS.items():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{item}**")
                st.caption(desc)
            with c2:
                if st.button("Open", key=f"submenu_{item}", use_container_width=True):
                    clicked = item
            st.divider()
    return clicked
