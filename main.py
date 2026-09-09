import os
import random
import sqlite3 as db
from datetime import datetime, timedelta

import admin
import auth_utils
import ds_dashboard
import leaderboard
import assessment_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "telemetry.db")


def seed_sample_attempts(conn):
    """Seed initial realistic historical attempt data for Data Science analytics if empty."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM attempts")
    count = cur.fetchone()[0]
    if count >= 20:
        return

    print("[*] Initializing historical dataset for Data Science analytics...")
    random.seed(42)

    names = [
        "Jane D.",
        "Priya S.",
        "Rohan V.",
        "Ananya M.",
        "Vikram R.",
        "Sneha P.",
        "Rahul K.",
        "Neha D.",
        "Aditya J.",
        "Pooja T.",
        "Kunal B.",
        "Divya N.",
        "Amit G.",
        "Ritu C.",
        "Manish L.",
        "Simran H.",
        "Suresh W.",
        "Kavita S.",
        "Gaurav E.",
        "Tanvi K.",
        "Harsh Y.",
        "Meera B.",
        "Nitin F.",
        "Aarav P.",
        "Shreya T.",
    ]

    records = []
    base_date = datetime.now() - timedelta(days=45)

    for i in range(250):
        name = random.choice(names)
        days_offset = random.randint(0, 45)
        attempt_time = base_date + timedelta(
            days=days_offset, minutes=random.randint(10, 1400)
        )
        date_str = attempt_time.strftime("%Y-%m-%d %H:%M:%S")

        tier = random.choices(["high", "medium", "low"], weights=[0.35, 0.45, 0.20])[0]

        if tier == "high":
            score = random.randint(8, 10)
            total = 10
            time_sec = random.randint(50, 120)
        elif tier == "medium":
            score = random.randint(5, 7)
            total = 10
            time_sec = random.randint(90, 180)
        else:
            score = random.randint(2, 4)
            total = 10
            time_sec = random.randint(130, 240)

        score_per = (score / total) * 100.0
        passed = 1 if score_per >= 50.0 else 0

        records.append(
            (name, score, total, score_per, time_sec, date_str, passed)
        )

    cur.executemany(
        """
        INSERT INTO attempts (
            student_name, score, total_questions, score_percentage,
            time_taken_seconds, attempt_date, passed
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        records,
    )
    conn.commit()
    print(
        f"[+] Loaded {len(records)} historical assessment attempts for Data Science & ML analysis."
    )


def init_db(conn):
    """Ensure essential tables exist."""
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
        explanation TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        name TEXT,
        score INTEGER,
        total_questions INTEGER,
        scoreper REAL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        score INTEGER,
        total_questions INTEGER,
        score_percentage REAL,
        time_taken_seconds INTEGER,
        attempt_date TEXT,
        passed INTEGER
    )""")
    # Ensure default admin exists
    cur.execute("SELECT username FROM login WHERE username = 'admin'")
    if not cur.fetchone():
        admin_pass = auth_utils.get_default_admin_password()
        pwd_hash = auth_utils.hash_password(admin_pass)
        cur.execute(
            "INSERT INTO login VALUES ('admin', ?, 'admin', 'active')", (pwd_hash,)
        )
    conn.commit()

    # Seed analytics attempts if not already present
    seed_sample_attempts(conn)


def main():
    conn = db.connect(DB_PATH)
    init_db(conn)

    print("=" * 45)
    print("   Learning Analytics Engine & Data Science")
    print("=" * 45)
    while True:
        try:
            choice = int(input("""
Main Menu
1) Login (Admin)
2) Take Assessment
3) Show Leaderboard
4) Data Science & Analytics Dashboard
5) Exit
Enter your choice (1-5) -> """).strip())
        except ValueError:
            print("\n[!] Invalid choice. Please enter a valid number (1-5).")
            continue

        if choice == 1:
            admin.auth(conn)
        elif choice == 2:
            assessment_engine.play_assessment(conn)
        elif choice == 3:
            leaderboard.show_leaderboard(conn)
        elif choice == 4:
            ds_dashboard.dashboard_menu(conn)
        elif choice == 5:
            print("\nThank you for using Learning Analytics Engine. Goodbye!")
            conn.close()
            return
        else:
            print("\n[!] Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
