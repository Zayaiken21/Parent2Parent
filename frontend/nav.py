"""
Main navigation.

Parents see 4 sticky primary tabs (Profile, Events, Chat, Logout) plus
a secondary "More" sub-menu for deeper parenting tools.

The CEO is a moderator role, not a parent profile, so they get a
4-tab bar of their own (Settings, Events, Chat, Logout) and no
parenting sub-menu — Settings is where the CEO generates/manages
parent access tokens; Events includes management controls
(create/import/delete) that parents don't see.

The nav bar renders at the TOP of the page, not the bottom.
"""
import streamlit as st


PARENT_TABS = ["Profile", "Events", "Chat", "Logout"]
CEO_TABS = ["Settings", "Events", "Chat", "Logout"]

ICONS = {"Profile": "👤", "Settings": "⚙️", "Events": "📅", "Chat": "💬", "Logout": "🚪"}

SUBMENU_ITEMS = {
    "Curriculum": "Browse the 0–21 child development guide",
    "Connection Builder": "Daily prompts for building emotional connection",
    "Structure & Routines": "Tools for building healthy household structure",
    "Connect Quiz": "A short reflection quiz on your child's learning style — kept private, not stored in our database",
    "CDL Study Tools": "Trucking/CDL study companion",  # kept per existing project scope
}

# Items in this map open an external site directly via st.link_button
# instead of routing to an internal page — clicking "Open" leaves the
# app immediately in a new tab, no in-between page.
SUBMENU_EXTERNAL_LINKS = {
    "CDL Study Tools": "https://nyccdlpro.streamlit.app/",
}


def render_top_nav(active_page: str, role: str = "parent") -> str | None:
    """Renders the sticky tab bar appropriate for the given role, at
    the top of the page. Returns the tab name if a new tab was
    clicked this run, else None. Caller is responsible for updating
    st.session_state.active_page and rerunning.
    """
    tabs = CEO_TABS if role == "ceo" else PARENT_TABS
    cols = st.columns(len(tabs))
    clicked = None
    for col, tab in zip(cols, tabs):
        with col:
            is_active = tab == active_page
            label = f"**{ICONS[tab]} {tab}**" if is_active else f"{ICONS[tab]} {tab}"
            if st.button(label, key=f"nav_{tab}", use_container_width=True):
                clicked = tab
    return clicked


def render_submenu(active_subpage: str | None) -> str | None:
    """Pro-style expandable secondary menu for deeper parenting tools.
    Parent-only — the CEO role never calls this. Returns the clicked
    item name for INTERNAL items (caller routes to a page), or None.
    Items listed in SUBMENU_EXTERNAL_LINKS render as a direct link
    button instead and never return a value — clicking them leaves
    the app immediately, there's nothing for the caller to route to.
    """
    clicked = None
    with st.expander("⚙️  More Parenting Tools", expanded=bool(active_subpage)):
        for item, desc in SUBMENU_ITEMS.items():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{item}**")
                st.caption(desc)
            with c2:
                external_url = SUBMENU_EXTERNAL_LINKS.get(item)
                if external_url:
                    st.link_button("Open ↗", external_url, use_container_width=True)
                else:
                    if st.button("Open", key=f"submenu_{item}", use_container_width=True):
                        clicked = item
            st.divider()
    return clicked
