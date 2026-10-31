"""
Session lifetime and login throttling rules, kept free of Streamlit and the database.
"""

SESSION_SECONDS = 86400
MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 900
MIN_PASSWORD_LENGTH = 8


def session_is_active(session: dict, now: float) -> bool:
    """A session is live until its expiry. Sessions saved without one have expired."""
    return now < session.get("expires_at", 0)


def is_locked_out(failures: int, last_failure: float, now: float) -> bool:
    """Lock an account once it reaches the limit, until the lockout time has passed."""
    return failures >= MAX_FAILED_LOGINS and now - last_failure < LOCKOUT_SECONDS
