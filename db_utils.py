"""
Database connection and schema initialization using psycopg2.
"""

import os
import time

import psycopg2
import streamlit as st

import auth_rules
import auth_utils


def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    db_url = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL"))
    if not db_url:
        st.error("DATABASE_URL not found in secrets.")
        return None
    return psycopg2.connect(db_url)


def _ensure_admin(cur, admin_password):
    """
    Create the admin account, and retire the old default password.

    Without ADMIN_PASSWORD no admin is created. An existing admin still using the old
    default gets the configured password, or is disabled if none is configured.
    """
    cur.execute("SELECT TRIM(password) FROM login WHERE username = 'admin'")
    row = cur.fetchone()
    if row is None:
        if admin_password:
            cur.execute(
                "INSERT INTO login VALUES ('admin', %s, 'admin', 'active')",
                (auth_utils.hash_password(admin_password),),
            )
        return
    if row[0] != auth_utils.legacy_hash("admin123"):
        return
    if admin_password:
        cur.execute(
            "UPDATE login SET password = %s WHERE username = 'admin'",
            (auth_utils.hash_password(admin_password),),
        )
    else:
        cur.execute("UPDATE login SET status = 'disabled' WHERE username = 'admin'")


def is_login_locked(cur, username):
    """Return True while an account is locked out after repeated failed logins."""
    cur.execute(
        "SELECT failures, last_failure FROM login_failures WHERE username = %s",
        (username,),
    )
    row = cur.fetchone()
    return bool(row) and auth_rules.is_locked_out(row[0], row[1], time.time())


def record_login_failure(cur, username):
    """Count a failed login, starting again if the last one was long enough ago."""
    now = time.time()
    cur.execute(
        """
        INSERT INTO login_failures (username, failures, last_failure)
        VALUES (%s, 1, %s)
        ON CONFLICT (username) DO UPDATE SET
            failures = CASE
                WHEN login_failures.last_failure < %s THEN 1
                ELSE login_failures.failures + 1
            END,
            last_failure = EXCLUDED.last_failure
        """,
        (username, now, now - auth_rules.LOCKOUT_SECONDS),
    )


def clear_login_failures(cur, username):
    cur.execute("DELETE FROM login_failures WHERE username = %s", (username,))


def init_db(conn):
    """Initialize the database schema if it doesn't already exist."""
    if not conn:
        return
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        status TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_failures (
        username TEXT PRIMARY KEY,
        failures INTEGER NOT NULL,
        last_failure DOUBLE PRECISION NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        name TEXT,
        score INTEGER,
        total_questions INTEGER,
        scoreper REAL,
        domain TEXT DEFAULT 'General',
        subject TEXT DEFAULT 'General'
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        attempt_id SERIAL PRIMARY KEY,
        student_name TEXT,
        score INTEGER,
        total_questions INTEGER,
        score_percentage REAL,
        time_taken_seconds INTEGER,
        reviews_used INTEGER,
        attempt_date TEXT,
        passed INTEGER,
        domain TEXT DEFAULT 'General',
        subject TEXT DEFAULT 'General',
        difficulty TEXT DEFAULT 'Medium'
    )""")

    cur.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name='attempts'"
    )
    columns = [col[0] for col in cur.fetchall()]
    if "difficulty" not in columns:
        cur.execute("ALTER TABLE attempts ADD COLUMN difficulty TEXT DEFAULT 'Medium'")

    _ensure_admin(cur, auth_utils.get_admin_password())

    conn.commit()
    cur.close()
