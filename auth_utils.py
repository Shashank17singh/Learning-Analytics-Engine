import hashlib
import os


def hash_password(password):
    """Securely hash passwords for storage using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_default_admin_password():
    """Get the default admin password from environment variable, or fallback to 'admin123'."""
    return os.environ.get("ADMIN_PASSWORD", "admin123")

import json
from pathlib import Path
import streamlit as st

def sync_session_state():
    """Sync session state from query params to survive F5 refreshes."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""

    # Re-hydrate from URL if available
    token = st.query_params.get("session_token", None)
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
    """Log the user in and persist the session."""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.user_role = role
    
    # Create a simple session file
    import uuid
    token = str(uuid.uuid4())
    st.query_params["session_token"] = token
    
    with open(f".session_{token}.json", "w") as f:
        json.dump({"username": username, "user_role": role}, f)

def logout_user():
    """Log the user out and clear the session."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    
    token = st.query_params.get("session_token", None)
    if token:
        try:
            Path(f".session_{token}.json").unlink(missing_ok=True)
        except:
            pass
    
    if "session_token" in st.query_params:
        del st.query_params["session_token"]
