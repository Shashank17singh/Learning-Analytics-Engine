"""
Main entry point for the Streamlit web application.
Handles routing, database initialization, and user authentication.
Architecture note: Relies on `auth_utils` and `db_utils` to keep state sync and auth routing decoupled from UI code.
"""

import streamlit as st

import auth_utils
from db_utils import get_db_connection, init_db

st.set_page_config(
    page_title="Assessment & Analytics Portal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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
        <div style='text-align: center; margin-bottom: 25px;'>
            <h1 style='color: #1E3A8A; font-weight: 800; margin-bottom: 4px;'> Learning Analytics Portal</h1>
        </div>
        """,
            unsafe_allow_html=True,
        )

        auth_tab1, auth_tab2 = st.tabs(
            [" Student / Admin Login", " Create Student Account"]
        )

        with auth_tab1:
            st.markdown(
                "<div style='margin-bottom: 15px; color: #4B5563; font-size: 0.95rem;'>Log in with your registered username & password:</div>",
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
                        "Sign In ", type="primary", use_container_width=True
                    )

                if btn_login:
                    if not login_user or not login_pwd:
                        st.error("Please enter both username and password.")
                    else:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        pwd_hash = auth_utils.hash_password(login_pwd)
                        cur.execute(
                            "SELECT username, role FROM login WHERE LOWER(TRIM(username)) = %s AND TRIM(password) = %s AND status = 'active'",
                            (login_user, pwd_hash),
                        )
                        row = cur.fetchone()

                        if row:
                            auth_utils.login_user(row[0], row[1])
                            st.success(f"Welcome back, {row[0]}!")
                            st.rerun()
                        else:
                            st.error(
                                "Invalid credentials. If you are a new student, please create an account."
                            )

            st.markdown(
                """
            <div style='background-color: #F1F5F9; border-radius: 8px; padding: 10px 14px; margin-top: 15px; font-size: 0.85rem; color: #475569;'>
                 <b>Administrator Credentials:</b> Username: <code>admin</code> | Password is set via <code>ADMIN_PASSWORD</code> environment variable.
            </div>
            """,
                unsafe_allow_html=True,
            )

        with auth_tab2:
            st.markdown(
                "<div style='margin-bottom: 15px; color: #4B5563; font-size: 0.95rem;'>New student? Create your account in 10 seconds:</div>",
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
                    placeholder="At least 4 characters",
                ).strip()
                reg_pwd2 = st.text_input(
                    "Confirm Password:", type="password", placeholder="Retype password"
                ).strip()
                st.write("")
                _, btn_col2, _ = st.columns([1, 2, 1])
                with btn_col2:
                    btn_register = st.form_submit_button(
                        "Create Account ", type="primary", use_container_width=True
                    )

                if btn_register:
                    if not reg_name or not reg_user or not reg_pwd:
                        st.error("Please fill in all fields.")
                    elif len(reg_pwd) < 4:
                        st.error("Password must be at least 4 characters long.")
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
                                " Account created successfully! Please switch to the Login tab and sign in."
                            )

else:
    if st.session_state.user_role != "admin":
        st.switch_page("pages/Student_Portal.py")
    else:
        st.switch_page("pages/Admin_Portal.py")
