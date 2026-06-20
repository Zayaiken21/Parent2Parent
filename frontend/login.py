"""
Login page: a single Sign In form for everyone. The email/password
entered is checked against the CEO env-var credentials first (a
local, no-network comparison); if that doesn't match, it falls
through to normal parent login against Supabase Auth. Signup (with
6-digit email verification) lives in its own tab.
"""
import streamlit as st

from core import auth
from config.age_bands import AGE_BAND_ORDER, AGE_BANDS, SECURITY_QUESTIONS, age_band_for_birth_year
from config.ceo_settings import verify_ceo_login
from datetime import date


def _rerun():
    st.rerun()


def _clear_signup_flow():
    for key in ("signup_step", "signup_email", "signup_birth_year", "signup_age_band"):
        st.session_state.pop(key, None)


def _render_signup() -> None:
    step = st.session_state.get("signup_step", "request_code")

    if step == "request_code":
        st.subheader("Create Your Account")
        with st.form("signup_request_form"):
            email = st.text_input("Email address")
            submitted = st.form_submit_button("Send Verification Code", use_container_width=True)
            if submitted:
                try:
                    auth.request_signup_code(email)
                    st.session_state.signup_email = email.strip().lower()
                    st.session_state.signup_step = "verify_and_details"
                    _rerun()
                except auth.AuthError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Couldn't send a code right now. Please try again shortly.")

    elif step == "verify_and_details":
        email = st.session_state.get("signup_email", "")
        st.subheader("Verify & Finish Your Profile")
        st.caption(f"We sent a 6-digit code to **{email}**.")

        with st.form("signup_details_form"):
            code = st.text_input("6-digit code", max_chars=6)
            first_name = st.text_input("First name only", help="For privacy, only your first name is ever shown to other users.")

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

            password = st.text_input("Create a password", type="password")
            confirm = st.text_input("Confirm password", type="password")

            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        profile = auth.complete_signup(
                            email=email,
                            code=code,
                            password=password,
                            first_name=first_name,
                            birth_year=int(birth_year),
                            gender=gender,
                            security_answer=security_answer,
                        )
                        st.success("Account created! Please sign in.")
                        _clear_signup_flow()
                        st.session_state.signup_step = "request_code"
                        _rerun()
                    except auth.AuthError as exc:
                        st.error(str(exc))
                    except Exception:
                        st.error("Something went wrong creating your account. Please try again.")

        if st.button("← Use a different email"):
            _clear_signup_flow()
            _rerun()


def _render_password_reset() -> None:
    step = st.session_state.get("reset_step", "request_code")

    if step == "request_code":
        st.subheader("Reset Password")
        with st.form("reset_request_form"):
            email = st.text_input("Account email")
            submitted = st.form_submit_button("Send Reset Code", use_container_width=True)
            if submitted:
                try:
                    auth.request_password_reset_code(email)
                    st.session_state.reset_email = email.strip().lower()
                    st.session_state.reset_step = "verify"
                    _rerun()
                except Exception:
                    st.error("Couldn't send a code right now. Please try again shortly.")

        if st.button("← Back to login"):
            st.session_state.pop("reset_mode", None)
            _rerun()

    elif step == "verify":
        email = st.session_state.get("reset_email", "")
        st.subheader("Enter Your Reset Code")
        st.caption(f"We sent a 6-digit code to **{email}**.")
        with st.form("reset_verify_form"):
            code = st.text_input("6-digit code", max_chars=6)
            new_password = st.text_input("New password", type="password")
            confirm = st.text_input("Confirm new password", type="password")
            submitted = st.form_submit_button("Reset Password", use_container_width=True)
            if submitted:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        auth.complete_password_reset(email, code, new_password)
                        st.success("Password updated. You can now sign in.")
                        st.session_state.pop("reset_mode", None)
                        st.session_state.pop("reset_step", None)
                        st.session_state.pop("reset_email", None)
                        _rerun()
                    except auth.AuthError as exc:
                        st.error(str(exc))


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
        if st.session_state.get("reset_mode"):
            _render_password_reset()
        else:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted:
                    if not email.strip() or not password:
                        st.error("Enter both email and password.")
                    elif verify_ceo_login(email, password):
                        # CEO check happens first and is purely local
                        # (env-var comparison, no network call), so a
                        # correct CEO login never touches Supabase at
                        # all and can't collide with parent_profiles.
                        st.session_state.authenticated = True
                        st.session_state.role = "ceo"
                        st.session_state.active_page = "Chat"
                        _rerun()
                    else:
                        try:
                            profile = auth.login(email, password)
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

            if st.button("Forgot your password?"):
                st.session_state.reset_mode = True
                _rerun()

    with tab_signup:
        _render_signup()
