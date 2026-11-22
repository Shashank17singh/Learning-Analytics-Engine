"""
Main entry point for the Streamlit web application.
Handles routing, database initialization, and user authentication.
Architecture note: Relies on `auth_utils` and `db_utils` to keep state sync and auth routing decoupled from UI code.
"""

import streamlit as st

import auth_rules
import auth_utils
from db_utils import (
    clear_login_failures,
    get_db_connection,
    init_db,
    is_login_locked,
    record_login_failure,
)
import theme_utils

st.set_page_config(
    page_title="Assessment & Analytics Portal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

theme_utils.inject_custom_theme()


_init_conn = get_db_connection()
init_db(_init_conn)
_init_conn.close()


auth_utils.sync_session_state()


if not st.session_state.authenticated:
    st.write("")
    st.write("")
    col_center, _ = st.columns([1, 0.01])

    with col_center:
        st.markdown(
            """
        <div class="portal-header">
            <div class="portal-badge">Assessment Engine</div>
            <h1 class="portal-title">Learning Analytics Portal</h1>
            <p class="portal-subtitle">Adaptive evaluation, cohort diagnostics, and predictive academic intelligence.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        auth_tab1, auth_tab2 = st.tabs(
            ["Sign In", "Create Student Account"]
        )

        with auth_tab1:
            st.markdown(
                "<div style='margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.95rem;'>Sign in with your registered username and password:</div>",
                unsafe_allow_html=True,
            )
            with st.form("login_form"):
                login_user = (
                    st.text_input("Username:", placeholder="Enter your username")
                    .strip()
                    .lower()
                )
                login_pwd = st.text_input(
                    "Password:", type="password", placeholder="Enter your password"
                ).strip()
                st.write("")
                _, btn_col1, _ = st.columns([1, 2, 1])
                with btn_col1:
                    btn_login = st.form_submit_button(
                        "Sign In", type="primary", use_container_width=True
                    )

                if btn_login:
                    if not login_user or not login_pwd:
                        st.error("Please enter both username and password.")
                    else:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT username, role, TRIM(password) FROM login WHERE LOWER(TRIM(username)) = %s AND status = 'active'",
                            (login_user,),
                        )
                        row = cur.fetchone()

                        # Only real accounts are counted, so made-up names add no rows.
                        if row and is_login_locked(cur, row[0]):
                            st.error(
                                "Too many failed attempts. Please try again in 15 minutes."
                            )
                        elif row and auth_utils.verify_password(login_pwd, row[2]):
                            clear_login_failures(cur, row[0])
                            conn.commit()
                            if auth_utils.needs_upgrade(row[2]):
                                cur.execute(
                                    "UPDATE login SET password = %s WHERE username = %s",
                                    (auth_utils.hash_password(login_pwd), row[0]),
                                )
                                conn.commit()
                            auth_utils.login_user(row[0], row[1])
                            st.success(f"Welcome back, {row[0]}!")
                            st.rerun()
                        else:
                            if row:
                                record_login_failure(cur, row[0])
                                conn.commit()
                            st.error(
                                "Invalid credentials. If you are a new student, please create an account."
                            )

            st.markdown(
                """
            <div class="info-callout">
                <strong>Administrator Access:</strong> Username: <code>admin</code> | Password is set via <code>ADMIN_PASSWORD</code> environment variable.
            </div>
            """,
                unsafe_allow_html=True,
            )

        with auth_tab2:
            st.markdown(
                "<div style='margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.95rem;'>New student? Create your account in seconds:</div>",
                unsafe_allow_html=True,
            )
            with st.form("register_form"):
                reg_name = st.text_input(
                    "Full Name:", placeholder="e.g. Enter your Full Name"
                ).strip()
                reg_user = (
                    st.text_input(
                        "Choose Username:", placeholder="e.g. Enter your User Name"
                    )
                    .strip()
                    .lower()
                )
                reg_pwd = st.text_input(
                    "Create Password:",
                    type="password",
                    placeholder=f"At least {auth_rules.MIN_PASSWORD_LENGTH} characters",
                ).strip()
                reg_pwd2 = st.text_input(
                    "Confirm Password:", type="password", placeholder="Retype password"
                ).strip()
                st.write("")
                _, btn_col2, _ = st.columns([1, 2, 1])
                with btn_col2:
                    btn_register = st.form_submit_button(
                        "Create Account", type="primary", use_container_width=True
                    )

                if btn_register:
                    if not reg_name or not reg_user or not reg_pwd:
                        st.error("Please fill in all fields.")
                    elif len(reg_pwd) < auth_rules.MIN_PASSWORD_LENGTH:
                        st.error(
                            f"Password must be at least {auth_rules.MIN_PASSWORD_LENGTH} characters long."
                        )
                    elif reg_pwd != reg_pwd2:
                        st.error("Passwords do not match. Please recheck.")
                    else:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT username FROM login WHERE LOWER(TRIM(username)) = %s",
                            (reg_user,),
                        )
                        if cur.fetchone():
                            st.error(
                                f"Username '{reg_user}' is already taken. Please choose another."
                            )
                        else:
                            pwd_hash = auth_utils.hash_password(reg_pwd)
                            cur.execute(
                                "INSERT INTO login VALUES (%s, %s, 'student', 'active')",
                                (reg_user, pwd_hash),
                            )
                            conn.commit()
                            st.success(
                                "Account created successfully! Please switch to the Sign In tab."
                            )

else:
    if st.session_state.user_role != "admin":
        st.switch_page("pages/Student_Portal.py")
    else:
        st.switch_page("pages/Admin_Portal.py")
