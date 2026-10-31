"""
Authentication utilities for managing session state.
Handles cookie-based persistence of logins.
"""

import json
import os
import uuid
from pathlib import Path

import extra_streamlit_components as stx
import streamlit as st

from passwords import hash_password, legacy_hash, needs_upgrade, verify_password

__all__ = ["hash_password", "legacy_hash", "needs_upgrade", "verify_password"]


def get_admin_password():
    """Return the admin password from Streamlit secrets or the environment, if set."""
    return st.secrets.get("ADMIN_PASSWORD", os.getenv("ADMIN_PASSWORD")) or None


def _session_path(token):
    """Map a cookie token to its session file, rejecting anything but a UUID."""
    return Path(f".session_{uuid.UUID(str(token))}.json")


def get_cookie_manager():
    """Initialize and return a Streamlit cookie manager component."""
    return stx.CookieManager(key="auth_cookie_manager")


def sync_session_state():
    """Synchronize the application session state from cookies."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""

    token = st.context.cookies.get("session_token")
    if token:
        try:
            session_file = _session_path(token)
            if session_file.exists():
                with open(session_file, "r") as f:
                    data = json.load(f)
                st.session_state.authenticated = True
                st.session_state.username = data.get("username")
                st.session_state.user_role = data.get("user_role")
        except Exception:  # noqa: BLE001, S110
            pass


def login_user(username, role):
    """Authenticate a user and persist their session."""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.user_role = role

    token = str(uuid.uuid4())

    with open(_session_path(token), "w") as f:
        json.dump({"username": username, "user_role": role}, f)

    cm = get_cookie_manager()
    cm.set("session_token", token, max_age=86400)


def logout_user():
    """Terminate the user session and clear associated authentication data."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_role = ""

    cm = get_cookie_manager()
    token = cm.get("session_token")
    if token:
        try:
            _session_path(token).unlink(missing_ok=True)
        except ValueError:
            pass
        cm.delete("session_token")
