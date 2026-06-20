import bootstrap  # noqa: F401  — must run first to populate os.environ

import streamlit as st

from styles.global_css import get_global_css
from frontend.login import render_login
from frontend.nav import render_bottom_nav, render_submenu
from frontend.pages_ui.profile_page import render_profile
from frontend.pages_ui.events_page import render_events
from frontend.pages_ui.chat_page import render_chat
from frontend.pages_ui.curriculum_page import render_curriculum
from frontend.pages_ui.connection_page import render_connection_builder
from frontend.pages_ui.structure_page import render_structure_tools

st.set_page_config(page_title="Parent2Parent", page_icon="💛", layout="centered")
st.markdown(get_global_css(), unsafe_allow_html=True)


def _logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def main() -> None:
    if not st.session_state.get("authenticated"):
        render_login()
        return

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Profile"

    active_page = st.session_state.active_page
    sub_page = st.session_state.get("active_subpage")

    # ---- route to the right view ----
    if sub_page == "Curriculum":
        render_curriculum()
    elif sub_page == "Connection Builder":
        render_connection_builder()
    elif sub_page == "Structure & Routines":
        render_structure_tools()
    elif active_page == "Profile":
        render_profile()
    elif active_page == "Events":
        render_events()
    elif active_page == "Chat":
        render_chat()
    else:
        render_profile()

    if sub_page:
        if st.button("← Back to main tabs"):
            st.session_state.active_subpage = None
            st.rerun()

    # CEO doesn't need the parenting sub-menu — keep their view focused on oversight.
    if st.session_state.get("role") != "ceo" and not sub_page:
        clicked_sub = render_submenu(sub_page)
        if clicked_sub:
            st.session_state.active_subpage = clicked_sub
            st.rerun()

    # ---- sticky bottom nav ----
    st.markdown('<div class="p2p-bottom-nav">', unsafe_allow_html=True)
    clicked = render_bottom_nav(active_page if not sub_page else "")
    st.markdown("</div>", unsafe_allow_html=True)

    if clicked == "Logout":
        _logout()
    elif clicked:
        st.session_state.active_page = clicked
        st.session_state.active_subpage = None
        st.rerun()


if __name__ == "__main__":
    main()
