import bootstrap  # noqa: F401  — must run first to populate os.environ

import streamlit as st

from styles.global_css import get_global_css
from styles.time_of_day_scenes import maybe_render_time_of_day_scene
from frontend.login import render_login
from frontend.nav import render_top_nav, render_submenu
from frontend.pages_ui.profile_page import render_profile
from frontend.pages_ui.events_page import render_events
from frontend.pages_ui.chat_page import render_chat
from frontend.pages_ui.curriculum_page import render_curriculum
from frontend.pages_ui.connection_page import render_connection_builder
from frontend.pages_ui.structure_page import render_structure_tools
from frontend.pages_ui.connect_quiz_page import render_connect_quiz
from frontend.pages_ui.ceo_settings_page import render_ceo_settings
from frontend.pages_ui.nyc_resources_page import render_nyc_resources

st.set_page_config(page_title="Parent2Parent", page_icon="💛", layout="wide")
st.markdown(get_global_css(), unsafe_allow_html=True)


def _logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def main() -> None:
    if not st.session_state.get("authenticated"):
        render_login()
        return

    maybe_render_time_of_day_scene()

    role = st.session_state.get("role", "parent")

    if "active_page" not in st.session_state:
        st.session_state.active_page = "Settings" if role == "ceo" else "Profile"

    active_page = st.session_state.active_page
    sub_page = st.session_state.get("active_subpage")

    # CEO is a moderator role, not a parent profile — Profile simply
    # isn't a valid destination for that role.
    if role == "ceo" and active_page == "Profile":
        active_page = "Settings"
        st.session_state.active_page = "Settings"
    # Settings only exists for the CEO.
    if role != "ceo" and active_page == "Settings":
        active_page = "Profile"
        st.session_state.active_page = "Profile"

    # ---- sticky top nav (rendered first so it stays at the top) ----
    st.markdown('<div class="p2p-top-nav">', unsafe_allow_html=True)
    clicked = render_top_nav(active_page if not sub_page else "", role=role)
    st.markdown("</div>", unsafe_allow_html=True)

    if clicked == "Logout":
        _logout()
        return
    elif clicked:
        st.session_state.active_page = clicked
        st.session_state.active_subpage = None
        st.rerun()

    # ---- route to the right view ----
    if sub_page == "Curriculum":
        render_curriculum()
    elif sub_page == "Connection Builder":
        render_connection_builder()
    elif sub_page == "Structure & Routines":
        render_structure_tools()
    elif sub_page == "Connect Quiz":
        render_connect_quiz()
    elif sub_page == "NYC Programs & Resources":
        render_nyc_resources()
    elif active_page == "Settings":
        render_ceo_settings()
    elif active_page == "Profile":
        render_profile()
    elif active_page == "Events":
        render_events()
    elif active_page == "Chat":
        render_chat()
    else:
        render_ceo_settings() if role == "ceo" else render_profile()

    if sub_page:
        if st.button("← Back to main tabs"):
            st.session_state.active_subpage = None
            st.rerun()

    # CEO doesn't get the parenting sub-menu — keep their view focused on oversight.
    if role != "ceo" and not sub_page:
        clicked_sub = render_submenu(sub_page)
        if clicked_sub:
            st.session_state.active_subpage = clicked_sub
            st.rerun()


if __name__ == "__main__":
    main()
