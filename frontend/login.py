"""
Login page: a single Sign In form for everyone (username + password).
That form is checked against the CEO env-var credentials first; if it
doesn't match, it falls through to normal parent login against
Supabase. Signup lives in its own tab and now uses a CEO-issued
access token instead of email verification — the parent redeems the
token once to create a username + password.
"""
import streamlit as st

from core import auth
from core.parent_tokens import validate_token, TokenError
from config.age_bands import AGE_BANDS, SECURITY_QUESTIONS, age_band_for_birth_year
from config.ceo_settings import verify_ceo_login
from datetime import date


def _rerun():
    st.rerun()


def _clear_signup_flow():
    for key in ("signup_step", "signup_token"):
        st.session_state.pop(key, None)


def _render_signup() -> None:
    step = st.session_state.get("signup_step", "enter_token")

    if step == "enter_token":
        st.subheader("Create Your Account")
        st.caption("You'll need the access token the CEO gave you to get started.")
        with st.form("signup_token_form"):
            token = st.text_input("Access Token", placeholder="6-character code", max_chars=6)
            submitted = st.form_submit_button("Continue", use_container_width=True)
            if submitted:
                try:
                    validate_token(token)
                    st.session_state.signup_token = token.strip().upper()
                    st.session_state.signup_step = "details"
                    _rerun()
                except TokenError as exc:
                    st.error(str(exc))

    elif step == "details":
        token = st.session_state.get("signup_token", "")
        st.subheader("Set Up Your Profile")
        st.caption(f"Token accepted: **{token}**")

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

            gender = st.selectbox(
                "This sets which community chat room you'll see — choose the one that fits you",
                ["male", "female"],
                format_func=lambda g: "Male (Dads' room)" if g == "male" else "Female (Moms' room)",
            )

            if preview_band:
                spec = SECURITY_QUESTIONS[preview_band]
                st.info(f"Quick check for the **{AGE_BANDS[preview_band]['label']}** age range:")
                st.markdown(f"**{spec['question']}**")
                security_answer = st.text_input("Your answer")
            else:
                st.warning("That birth year doesn't match a supported age range yet.")
                security_answer = ""

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
                            token=token,
                            username=username,
                            password=password,
                            first_name=first_name,
                            birth_year=int(birth_year),
                            gender=gender,
                            security_answer=security_answer,
                            email=email,
                        )
                        st.success("Account created! Please sign in.")
                        _clear_signup_flow()
                        st.session_state.signup_step = "enter_token"
                        _rerun()
                    except auth.AuthError as exc:
                        st.error(str(exc))
                    except Exception:
                        st.error("Something went wrong creating your account. Please try again.")

        if st.button("← Use a different token"):
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

        st.caption("Forgot your password? Ask the CEO for a new access token and create your account again.")

    with tab_signup:
        _render_signup()
