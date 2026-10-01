import hashlib
import os


def hash_password(password):
    """Securely hash passwords for storage using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_default_admin_password():
    """Get the default admin password from environment variable, or fallback to 'admin123'."""
    return os.environ.get("ADMIN_PASSWORD", "admin123")

import json
import uuid
from pathlib import Path
import streamlit as st
import extra_streamlit_components as stx

@st.cache_resource
def get_cookie_manager():
    return stx.CookieManager(key="auth_cookie_manager")

def sync_session_state():
    """Sync session state from cookies to survive F5 refreshes."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""

    # Synchronously read cookie avoiding first-load rerun issues
    token = st.context.cookies.get("session_token")
    if token:
        try:
            session_file = Path(f".session_{token}.json")
            if session_file.exists():
                with open(session_file, "r") as f:
                    data = json.load(f)
                st.session_state.authenticated = True
                st.session_state.username = data.get("username")
                st.session_state.user_role = data.get("user_role")
        except Exception:
            pass

def login_user(username, role):
    """Log the user in and persist the session via cookie."""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.user_role = role
    
    token = str(uuid.uuid4())
    
    with open(f".session_{token}.json", "w") as f:
        json.dump({"username": username, "user_role": role}, f)
        
    cm = get_cookie_manager()
    cm.set("session_token", token, max_age=86400) # 1 day

def logout_user():
    """Log the user out and clear the session."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    
    cm = get_cookie_manager()
    token = cm.get("session_token")
    if token:
        try:
            Path(f".session_{token}.json").unlink(missing_ok=True)
        except:
            pass
        cm.delete("session_token")
