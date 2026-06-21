"""
Login page: a single Sign In form for everyone (username + password).
That form is checked against the CEO env-var credentials first; if it
doesn't match, it falls through to normal parent login against
Supabase.

Signup lives in its own tab and is gated by ONE shared access code
(env var PARENT_ACCESS_CODE) rather than a per-account token. The
code only unlocks the signup FORM — it is never stored against the
created account and is never a login credential. Every account still
gets its own unique username + password, and logging in afterward
only ever checks username + password, so knowing the shared code
never grants access to someone else's account.
"""
import streamlit as st

from core import auth
from config.age_bands import age_band_for_birth_year
from config.ceo_settings import verify_ceo_login, verify_parent_access_code
from datetime import date


def _rerun():
    st.rerun()


def _clear_signup_flow():
    for key in ("signup_step", "signup_verified_code"):
        st.session_state.pop(key, None)


def _render_signup() -> None:
    step = st.session_state.get("signup_step", "enter_code")

    if step == "enter_code":
        st.subheader("Create Your Account")
        st.caption("Enter the access code to get started.")
        with st.form("signup_code_form"):
            code = st.text_input("Access Code", placeholder="Enter the code")
            submitted = st.form_submit_button("Continue", use_container_width=True)
            if submitted:
                if verify_parent_access_code(code):
                    st.session_state.signup_verified_code = code.strip()
                    st.session_state.signup_step = "details"
                    _rerun()
                else:
                    st.error("That access code is incorrect.")

    elif step == "details":
        st.subheader("Set Up Your Profile")

        with st.form("signup_details_form"):
            first_name = st.text_input("First name only", help="For privacy, only your first name is ever shown to other users.")
            username = st.text_input("Choose a username")
            password = st.text_input("Create a password", type="password")
            confirm = st.text_input("Confirm password", type="password")

            this_year = date.today().year
            birth_year = st.number_input(
                "Birth year",
                min_value=this_year - 90,
                max_value=this_year - 11,
                value=this_year - 25,
                step=1,
            )
            preview_band = age_band_for_birth_year(int(birth_year))
            if not preview_band:
                st.warning("That birth year doesn't match a supported age range yet.")

            gender = st.selectbox(
                "This sets which community chat room you'll see — choose the one that fits you",
                ["male", "female"],
                format_func=lambda g: "Male (Dads' room)" if g == "male" else "Female (Moms' room)",
            )

            email = st.text_input(
                "Email (optional)",
                placeholder="Only used if you opt in to event emails later",
            )

            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        auth.complete_signup(
                            access_code=st.session_state.get("signup_verified_code", ""),
                            username=username,
                            password=password,
                            first_name=first_name,
                            birth_year=int(birth_year),
                            gender=gender,
                            email=email,
                        )
                        st.success("Account created! Please sign in.")
                        _clear_signup_flow()
                        st.session_state.signup_step = "enter_code"
                        _rerun()
                    except auth.AuthError as exc:
                        st.error(str(exc))
                    except Exception:
                        st.error("Something went wrong creating your account. Please try again.")

        if st.button("← Start over"):
            _clear_signup_flow()
            _rerun()


def render_login() -> None:
    st.markdown(
        """
        <section class="app-hero">
            <h1>Parent2Parent</h1>
            <p>Real people. Real problems. Real education.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            if submitted:
                if not username.strip() or not password:
                    st.error("Enter both username and password.")
                elif verify_ceo_login(username, password):
                    # CEO check happens first and is purely local
                    # (env-var comparison, no network call), so a
                    # correct CEO login never touches Supabase at all
                    # and can't collide with a parent username.
                    st.session_state.authenticated = True
                    st.session_state.role = "ceo"
                    st.session_state.active_page = "Settings"
                    _rerun()
                else:
                    try:
                        profile = auth.login(username, password)
                        st.session_state.authenticated = True
                        st.session_state.role = "parent"
                        st.session_state.profile = profile
                        st.session_state.shard_id = profile["_shard_id"]
                        st.session_state.active_page = "Profile"
                        _rerun()
                    except auth.AuthError as exc:
                        st.error(str(exc))
                    except Exception:
                        st.error("Couldn't sign in right now. Please try again.")

        st.caption("Forgot your password? Contact the CEO for help recovering your account.")

    with tab_signup:
        _render_signup()
