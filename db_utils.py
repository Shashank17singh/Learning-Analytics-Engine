import os
import sqlite3

import pandas as pd

import auth_utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "telemetry.db")


def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS login (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        status TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        qno INTEGER PRIMARY KEY AUTOINCREMENT,
        ques TEXT,
        a TEXT,
        b TEXT,
        c TEXT,
        d TEXT,
        correct TEXT,
        review TEXT,
        explanation TEXT,
        domain TEXT DEFAULT 'General',
        subject TEXT DEFAULT 'General'
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
        attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        score INTEGER,
        total_questions INTEGER,
        score_percentage REAL,
        time_taken_seconds INTEGER,
        reviews_used INTEGER,
        attempt_date TEXT,
        passed INTEGER,
        domain TEXT DEFAULT 'General',
        subject TEXT DEFAULT 'General'
    )""")

    cur.execute("SELECT username FROM login WHERE username = 'admin'")
    if not cur.fetchone():
        admin_pass = auth_utils.get_default_admin_password()
        pwd_hash = auth_utils.hash_password(admin_pass)
        cur.execute(
            "INSERT INTO login VALUES ('admin', ?, 'admin', 'active')", (pwd_hash,)
        )

    # Auto-seed database for Streamlit Cloud portfolio demonstration
    cur.execute("SELECT COUNT(*) FROM questions")
    if cur.fetchone()[0] == 0:
        try:
            df_q = pd.read_csv(os.path.join(BASE_DIR, "assessment_bank.csv"))
            for _, r in df_q.iterrows():
                # Add default domain and subject if they don't exist in CSV
                domain = str(r.get("Domain", "General"))
                subject = str(r.get("Subject", "General"))
                cur.execute(
                    "INSERT INTO questions (ques, a, b, c, d, correct, review, explanation, domain, subject) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(r.get("Question", "")),
                        str(r.get("Option1", "")),
                        str(r.get("Option2", "")),
                        str(r.get("Option3", "")),
                        str(r.get("Option4", "")),
                        str(r.get("CorrectAnswer", "")),
                        str(r.get("review", "")),
                        str(r.get("explanation", "")),
                        domain,
                        subject,
                    ),
                )
            conn.commit()
        except Exception as e:
            print(f"Failed to seed questions: {e}")
    conn.commit()
