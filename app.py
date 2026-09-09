import os
import random
import sqlite3
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

import analytics
import auth_utils
import ml_models

# -------------------------------------------------------------
# PAGE CONFIGURATION (NO SIDEBAR, FULL BROWSER APP LAYOUT)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Quiz Assessment & Analytics Portal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "qms.db")


def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db(conn):
    """Ensure essential tables exist (cold-start safety for Streamlit Cloud)."""
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
        hint TEXT,
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
        hints_used INTEGER,
        attempt_date TEXT,
        passed INTEGER
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
            import pandas as pd

            df_q = pd.read_csv(os.path.join(BASE_DIR, "quiz.csv"))
            for _, r in df_q.iterrows():
                cur.execute(
                    "INSERT INTO questions (ques, a, b, c, d, correct, hint, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(r.get("Question", "")),
                        str(r.get("Option1", "")),
                        str(r.get("Option2", "")),
                        str(r.get("Option3", "")),
                        str(r.get("Option4", "")),
                        str(r.get("CorrectAnswer", "")),
                        str(r.get("hint", "")),
                        str(r.get("explanation", "")),
                    ),
                )
        except Exception:
            pass

    cur.execute("SELECT COUNT(*) FROM attempts")
    if cur.fetchone()[0] < 20:
        import random

        for i in range(100):
            score = random.randint(3, 10)
            score_per = (score / 10) * 100
            time_sec = random.randint(30, 200)
            hints = random.randint(0, 4)
            passed = 1 if score_per >= 50 else 0
            cur.execute(
                """
                INSERT INTO attempts (student_name, score, total_questions, score_percentage, time_taken_seconds, hints_used, attempt_date, passed)
                VALUES (?, ?, 10, ?, ?, ?, datetime('now', '-' || abs(random() % 30) || ' days'), ?)
            """,
                (f"demo_user_{i}", score, score_per, time_sec, hints, passed),
            )

    conn.commit()


# Initialize database on app startup
_init_conn = get_db_connection()
init_db(_init_conn)
_init_conn.close()

# -------------------------------------------------------------
# CUSTOM CSS: REMOVES SIDEBAR & ADDS MODERN PORTAL STYLING
# -------------------------------------------------------------
st.markdown(
    """
<style>
    /* Completely hide sidebar and collapse button */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    /* Modern Header */
    .portal-navbar {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 18px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);
    }
    .portal-title {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: white;
    }
    .portal-subtitle {
        font-size: 0.85rem;
        opacity: 0.9;
        margin: 0;
        color: #DBEAFE;
    }
    .badge-iitk {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 10px;
    }
    .auth-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        max-width: 480px;
        margin: 0 auto;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1E3A8A;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# -------------------------------------------------------------
# SCREEN 1: LOGIN & REGISTRATION (IF NOT LOGGED IN)
# -------------------------------------------------------------
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

        # TAB 1: LOGIN
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
                            "SELECT username, role FROM login WHERE LOWER(TRIM(username)) = ? AND TRIM(password) = ? AND status = 'active'",
                            (login_user, pwd_hash),
                        )
                        row = cur.fetchone()

                        if row:
                            st.session_state.authenticated = True
                            st.session_state.username = row[0]
                            st.session_state.user_role = row[1]
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

        # TAB 2: REGISTER (CREATE ACCOUNT)
        with auth_tab2:
            st.markdown(
                "<div style='margin-bottom: 15px; color: #4B5563; font-size: 0.95rem;'>New student? Create your account in 10 seconds:</div>",
                unsafe_allow_html=True,
            )
            with st.form("register_form"):
                reg_name = st.text_input(
                    "Full Name:", placeholder="e.g. Jane Doe"
                ).strip()
                reg_user = (
                    st.text_input("Choose Username:", placeholder="e.g. jane_doe")
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
                            "SELECT username FROM login WHERE LOWER(TRIM(username)) = ?",
                            (reg_user,),
                        )
                        if cur.fetchone():
                            st.error(
                                f"Username '{reg_user}' is already taken. Please choose another."
                            )
                        else:
                            pwd_hash = auth_utils.hash_password(reg_pwd)
                            cur.execute(
                                "INSERT INTO login VALUES (?, ?, 'student', 'active')",
                                (reg_user, pwd_hash),
                            )
                            conn.commit()
                            st.success(
                                " Account created successfully! Please switch to the Login tab and sign in."
                            )

# -------------------------------------------------------------
# SCREEN 2: AUTHENTICATED PORTAL (STUDENT & ADMIN VIEWS)
# -------------------------------------------------------------
else:
    col_nav1, col_nav2 = st.columns([3, 1])

    with col_nav1:
        st.markdown(
            f"""
        <div style='display: flex; align-items: center; gap: 12px;'>
            <h2 style='color: #1E3A8A; margin: 0; font-weight: 800;'>Learning Analytics Portal</h2>
        </div>
        <div style='color: #64748B; font-size: 0.9rem;'>Welcome, <b>{st.session_state.username.title()}</b></div>
        """,
            unsafe_allow_html=True,
        )

    with col_nav2:
        st.write("")
        if st.button(" Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_role = ""
            st.rerun()

    st.divider()

    conn = get_db_connection()

    # =========================================================
    # ROLE A: STUDENT DASHBOARD
    # =========================================================
    if st.session_state.user_role != "admin":
        student_tabs = st.tabs(
            [
                " Take Assessment",
                " My Performance & Analytics",
                " Hall of Fame (Leaderboard)",
            ]
        )

        # TAB 1: TAKE ASSESSMENT
        with student_tabs[0]:
            st.markdown("###  Active Assessment: General Knowledge & Data Foundations")
            cur = conn.cursor()
            cur.execute(
                "SELECT qno, ques, a, b, c, d, correct, hint, explanation FROM questions ORDER BY qno ASC"
            )
            all_questions = cur.fetchall()

            if not all_questions:
                st.warning(
                    "No questions available right now. Please contact the administrator."
                )
            else:
                if "student_quiz_started" not in st.session_state:
                    st.session_state.student_quiz_started = False
                if "quiz_start_time" not in st.session_state:
                    st.session_state.quiz_start_time = 0
                if "quiz_set" not in st.session_state:
                    st.session_state.quiz_set = None

                if not st.session_state.student_quiz_started:
                    total_available = len(all_questions)
                    q_options = (
                        [5, 10, 15, 20, 25]
                        if total_available >= 25
                        else (
                            [5, 10, 15]
                            if total_available >= 15
                            else [min(5, total_available), total_available]
                        )
                    )
                    num_questions_chosen = st.select_slider(
                        " Choose Number of Questions to Attempt:",
                        options=q_options,
                        value=10 if 10 in q_options else q_options[-1],
                    )

                    if st.button(
                        "Start Assessment Now ",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.session_state.student_quiz_started = True
                        st.session_state.quiz_start_time = time.time()
                        # Randomize questions so a new unique set appears every single time!
                        st.session_state.quiz_set = random.sample(
                            all_questions, min(num_questions_chosen, total_available)
                        )
                        st.rerun()
                else:
                    quiz_set = st.session_state.get("quiz_set", all_questions[:10])
                    user_choices = {}

                    with st.form("student_assessment_form"):
                        st.markdown(
                            f"**Answering {len(quiz_set)} Randomized Questions:**"
                        )
                        for idx, (
                            qno,
                            ques,
                            a,
                            b,
                            c,
                            d,
                            correct,
                            hint,
                            explanation,
                        ) in enumerate(quiz_set, 1):
                            st.markdown(f"**Q{idx}. {ques}**")
                            opts = [
                                f"a) {a}",
                                f"b) {b}",
                                f"c) {c}",
                                f"d) {d}",
                            ]
                            c_val = st.radio(
                                f"Select answer for Q{idx}:",
                                opts,
                                key=f"sq_{qno}",
                                index=None,
                                label_visibility="collapsed",
                            )
                            user_choices[qno] = (
                                c_val,
                                correct,
                                a,
                                b,
                                c,
                                d,
                                explanation,
                            )

                            st.write("")

                        submit_assessment = st.form_submit_button(
                            " Finish & Submit Assessment",
                            type="primary",
                            use_container_width=True,
                        )

                    if submit_assessment:
                        duration = max(
                            1, int(time.time() - st.session_state.quiz_start_time)
                        )
                        correct_count = 0
                        total_q = len(quiz_set)
                        hints_used_count = sum(
                            1
                            for qno in user_choices
                            if st.session_state.get(f"hint_{qno}", False)
                        )

                        for qno, (
                            c_val,
                            correct,
                            a,
                            b,
                            c,
                            d,
                            exp,
                        ) in user_choices.items():
                            if c_val:
                                letter = c_val[0].lower()
                                opt_map = {
                                    "a": str(a).strip().lower(),
                                    "b": str(b).strip().lower(),
                                    "c": str(c).strip().lower(),
                                    "d": str(d).strip().lower(),
                                }
                                clean_corr = str(correct).strip().lower()

                                if letter in ["a", "b", "c", "d"]:
                                    if (
                                        letter == clean_corr
                                        or opt_map.get(letter) == clean_corr
                                    ):
                                        correct_count += 1
                                elif c_val == clean_corr:
                                    correct_count += 1

                        score_percentage = (correct_count / total_q) * 100.0
                        passed = 1 if score_percentage >= 50.0 else 0

                        # Save attempt
                        cur.execute(
                            """
                            INSERT INTO attempts (
                                student_name, score, total_questions, score_percentage,
                                time_taken_seconds, hints_used, attempt_date, passed
                            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
                        """,
                            (
                                st.session_state.username,
                                correct_count,
                                total_q,
                                score_percentage,
                                duration,
                                hints_used_count,
                                passed,
                            ),
                        )

                        # Save leaderboard
                        cur.execute("PRAGMA table_info(leaderboard)")
                        cols = [r[1] for r in cur.fetchall()]
                        t_col = (
                            "total_questions" if "total_questions" in cols else "limit"
                        )
                        cur.execute(
                            f"INSERT INTO leaderboard (name, score, [{t_col}], scoreper) VALUES (?, ?, ?, ?)",
                            (
                                st.session_state.username,
                                correct_count,
                                total_q,
                                score_percentage,
                            ),
                        )
                        conn.commit()

                        if score_percentage >= 75.0:
                            st.balloons()
                            st.success(
                                f" **Outstanding Performance, {st.session_state.username.title()}!** You scored **{correct_count} out of {total_q}** ({score_percentage:.1f}%)."
                            )
                        elif score_percentage >= 50.0:
                            st.balloons()
                            st.success(
                                f" **Great Job, {st.session_state.username.title()}!** You successfully completed the assessment with **{correct_count}/{total_q}** ({score_percentage:.1f}%)."
                            )
                        else:
                            st.success(
                                f" **Assessment Completed Successfully!** Good effort, **{st.session_state.username.title()}**! Score: **{correct_count}/{total_q}** ({score_percentage:.1f}%)."
                            )

                        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                        col_res1.metric("Your Score", f"{correct_count} / {total_q}")
                        col_res2.metric("Accuracy", f"{score_percentage:.1f}%")
                        col_res3.metric("Duration", f"{duration}s")
                        col_res4.metric("Status", "Passed " if passed else "Completed ")

                        st.session_state.student_quiz_started = False
                        st.session_state.quiz_set = None
                        if st.button(" Take Another Assessment"):
                            st.rerun()

        # TAB 2: MY PERFORMANCE & ANALYTICS
        with student_tabs[1]:
            st.markdown(
                f"###  Personal Learning Analytics for: **{st.session_state.username.title()}**"
            )
            df_my = pd.read_sql_query(
                "SELECT * FROM attempts WHERE LOWER(TRIM(student_name)) = ? ORDER BY attempt_date DESC",
                conn,
                params=(st.session_state.username.lower(),),
            )

            if df_my.empty:
                st.info(
                    "You haven't completed any assessments yet. Take an assessment in Tab 1 to see your personal learning analytics here!"
                )
            else:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Assessments", len(df_my))
                m2.metric("Average Score", f"{df_my['score_percentage'].mean():.1f}%")
                m3.metric("Highest Score", f"{df_my['score_percentage'].max():.1f}%")
                m4.metric(
                    "Success Rate", f"{(df_my['passed'].sum() / len(df_my)) * 100:.1f}%"
                )

                st.divider()
                st.markdown("#### Assessment History")
                st.dataframe(
                    df_my[
                        [
                            "attempt_date",
                            "score",
                            "total_questions",
                            "score_percentage",
                            "time_taken_seconds",
                            "hints_used",
                            "passed",
                        ]
                    ],
                    use_container_width=True,
                    column_config={
                        "score_percentage": st.column_config.ProgressColumn(
                            "Score %", format="%.1f%%", min_value=0, max_value=100
                        ),
                        "passed": st.column_config.CheckboxColumn("Passed"),
                    },
                )

        # TAB 3: LEADERBOARD
        with student_tabs[2]:
            st.markdown("###  Real-Time Hall of Fame")
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(leaderboard)")
            cols = [r[1] for r in cur.fetchall()]
            t_col = "total_questions" if "total_questions" in cols else "limit"

            df_lb = pd.read_sql_query(
                f"SELECT name as 'Student', score as 'Score', [{t_col}] as 'Total', scoreper as 'Score %' FROM leaderboard ORDER BY scoreper DESC, score DESC LIMIT 50",
                conn,
            )
            if not df_lb.empty:
                ranks = [
                    (
                        f" 1st"
                        if i == 0
                        else f" 2nd" if i == 1 else f" 3rd" if i == 2 else f"{i+1}th"
                    )
                    for i in range(len(df_lb))
                ]
                df_lb.insert(0, "Rank", ranks)
                st.dataframe(df_lb, use_container_width=True)
            else:
                st.info("Leaderboard is currently empty.")

    # =========================================================
    # ROLE B: ADMINISTRATOR DASHBOARD
    # =========================================================
    else:
        admin_tabs = st.tabs(
            [
                " Cohort Analytics & BI Dashboard",
                " ML & Predictive Analytics",
                " Question Bank Management",
                " Registered Accounts",
                " Leaderboard",
            ]
        )

        # TAB 1: COHORT ANALYTICS & BI DASHBOARD
        with admin_tabs[0]:
            st.markdown("###  Assessment Cohort Analytics (Pandas & Seaborn)")
            df_cohort = pd.read_sql_query(
                "SELECT * FROM attempts ORDER BY attempt_date DESC", conn
            )

            if df_cohort.empty:
                st.warning("No assessment attempt records found.")
            else:
                df_cohort["Performance Tier"] = pd.cut(
                    df_cohort["score_percentage"],
                    bins=[-np.inf, 49.99, 74.99, 100],
                    labels=[
                        "Needs Improvement (<50%)",
                        "Competent (50-74%)",
                        "Distinction (75-100%)",
                    ],
                )

                # KPIs
                k1, k2, k3, k4, k5 = st.columns(5)
                tot = len(df_cohort)
                pass_cnt = int(df_cohort["passed"].sum())
                k1.metric("Total Attempts", tot)
                k2.metric("Cohort Pass Rate", f"{(pass_cnt / tot) * 100:.1f}%")
                k3.metric("Mean Score", f"{df_cohort['score_percentage'].mean():.1f}%")
                k4.metric(
                    "Avg Completion Time",
                    f"{df_cohort['time_taken_seconds'].mean():.0f}s",
                )
                k5.metric(
                    "Avg Hints Requested", f"{df_cohort['hints_used'].mean():.1f}"
                )

                st.divider()

                # Visual Grid (2x2)
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
                    sns.histplot(
                        df_cohort["score_percentage"],
                        kde=True,
                        color="#1E40AF",
                        bins=12,
                        ax=ax1,
                    )
                    ax1.axvline(
                        df_cohort["score_percentage"].mean(),
                        color="red",
                        linestyle="--",
                        label=f"Mean: {df_cohort['score_percentage'].mean():.1f}%",
                    )
                    ax1.axvline(
                        df_cohort["score_percentage"].median(),
                        color="green",
                        linestyle="-.",
                        label=f"Median: {df_cohort['score_percentage'].median():.1f}%",
                    )
                    ax1.set_title(
                        "Cohort Score Distribution (Histogram & KDE)", fontweight="bold"
                    )
                    ax1.set_xlabel("Score %")
                    ax1.legend()
                    st.pyplot(fig1)

                with row1_col2:
                    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
                    sns.scatterplot(
                        data=df_cohort,
                        x="time_taken_seconds",
                        y="score_percentage",
                        hue="passed",
                        palette={1: "#2ca02c", 0: "#d62728"},
                        s=60,
                        alpha=0.85,
                        ax=ax2,
                    )
                    sns.regplot(
                        data=df_cohort,
                        x="time_taken_seconds",
                        y="score_percentage",
                        scatter=False,
                        color="black",
                        line_kws={"linestyle": "--", "linewidth": 1.5},
                        ax=ax2,
                    )
                    ax2.set_title(
                        "Completion Duration vs. Score Performance", fontweight="bold"
                    )
                    ax2.set_xlabel("Time Taken (Seconds)")
                    ax2.set_ylabel("Score %")
                    st.pyplot(fig2)

                row2_col1, row2_col2 = st.columns(2)
                with row2_col1:
                    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
                    sns.boxplot(
                        data=df_cohort,
                        x="hints_used",
                        y="score_percentage",
                        hue="hints_used",
                        legend=False,
                        palette="Blues_r",
                        showmeans=True,
                        ax=ax3,
                    )
                    ax3.set_title(
                        "Hint Requests Impact on Score Spread", fontweight="bold"
                    )
                    ax3.set_xlabel("Hints Requested")
                    ax3.set_ylabel("Score %")
                    st.pyplot(fig3)

                with row2_col2:
                    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
                    t_counts = df_cohort["Performance Tier"].value_counts()
                    ax4.pie(
                        t_counts,
                        labels=t_counts.index,
                        autopct="%1.1f%%",
                        startangle=140,
                        colors=["#99ff99", "#66b3ff", "#ff9999"],
                        wedgeprops=dict(width=0.4, edgecolor="white"),
                    )
                    ax4.set_title("Cohort Competency Breakdown", fontweight="bold")
                    st.pyplot(fig4)

                st.markdown("#### Complete Cohort Attempt Records")
                st.dataframe(df_cohort, use_container_width=True)
                csv_bytes = df_cohort.to_csv(index=False).encode("utf-8")
                st.download_button(
                    " Export Cohort Data to CSV",
                    data=csv_bytes,
                    file_name="cohort_analytics.csv",
                    mime="text/csv",
                )

        # TAB 2: ML & PREDICTIVE ANALYTICS (Scikit-learn)
        with admin_tabs[1]:
            st.markdown("###  Machine Learning & Predictive Analytics (Scikit-learn)")
            df_ml = pd.read_sql_query(
                "SELECT * FROM attempts ORDER BY attempt_date ASC", conn
            )

            if df_ml.empty or len(df_ml) < 20:
                st.warning(
                    "Need at least 20 assessment records for ML analysis. Current records: "
                    + str(len(df_ml))
                )
            else:
                ml_sub_tabs = st.tabs(
                    [
                        " Classification",
                        " Regression",
                        " Clustering",
                        " Feature Engineering",
                        " Advanced SQL",
                    ]
                )

                # --- Classification Tab ---
                with ml_sub_tabs[0]:
                    st.markdown("#### Binary Classification: Pass/Fail Prediction")
                    st.caption(
                        "Models: Logistic Regression & Random Forest | Features: time, hints, speed, hint_ratio"
                    )

                    with st.spinner("Training classifiers..."):
                        clf = ml_models.train_classifiers(df_ml)

                    if "error" in clf:
                        st.error(clf["error"])
                    else:
                        # Metrics comparison table
                        metrics_data = []
                        for name, key in [
                            ("Logistic Regression", "logistic_regression"),
                            ("Random Forest", "random_forest"),
                        ]:
                            r = clf[key]
                            metrics_data.append(
                                {
                                    "Model": name,
                                    "Accuracy": f"{r['accuracy']:.4f}",
                                    "Precision": f"{r['precision']:.4f}",
                                    "Recall": f"{r['recall']:.4f}",
                                    "F1-Score": f"{r['f1']:.4f}",
                                    "CV Mean (5-fold)": f"{r['cv_mean']:.4f} ± {r['cv_std']:.4f}",
                                }
                            )
                        st.dataframe(
                            pd.DataFrame(metrics_data),
                            use_container_width=True,
                            hide_index=True,
                        )

                        clf_col1, clf_col2 = st.columns(2)

                        with clf_col1:
                            st.markdown("**Confusion Matrix (Random Forest)**")
                            fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
                            cm = clf["random_forest"]["confusion_matrix"]
                            sns.heatmap(
                                cm,
                                annot=True,
                                fmt="d",
                                cmap="Blues",
                                xticklabels=["Fail", "Pass"],
                                yticklabels=["Fail", "Pass"],
                                ax=ax_cm,
                            )
                            ax_cm.set_xlabel("Predicted")
                            ax_cm.set_ylabel("Actual")
                            ax_cm.set_title("Confusion Matrix", fontweight="bold")
                            st.pyplot(fig_cm)

                        with clf_col2:
                            st.markdown("**Feature Importances (Random Forest)**")
                            fig_fi, ax_fi = plt.subplots(figsize=(5, 4))
                            imp = clf["random_forest"]["feature_importances"]
                            colors = sns.color_palette("Blues_r", len(imp))
                            imp.plot(kind="barh", ax=ax_fi, color=colors)
                            ax_fi.set_xlabel("Importance")
                            ax_fi.set_title("Feature Importances", fontweight="bold")
                            ax_fi.invert_yaxis()
                            st.pyplot(fig_fi)

                # --- Regression Tab ---
                with ml_sub_tabs[1]:
                    st.markdown("#### Linear Regression: Score Prediction")
                    st.caption("Predicting score_percentage from engagement features")

                    with st.spinner("Training regression model..."):
                        reg = ml_models.train_regression(df_ml)

                    reg_m1, reg_m2, reg_m3, reg_m4 = st.columns(4)
                    reg_m1.metric("MAE", f"{reg['mae']:.2f}")
                    reg_m2.metric("RMSE", f"{reg['rmse']:.2f}")
                    reg_m3.metric("R² Score", f"{reg['r2']:.4f}")
                    reg_m4.metric("Intercept", f"{reg['intercept']:.2f}")

                    reg_col1, reg_col2 = st.columns(2)

                    with reg_col1:
                        st.markdown("**Actual vs Predicted Scores**")
                        fig_reg, ax_reg = plt.subplots(figsize=(6, 5))
                        ax_reg.scatter(
                            reg["y_test"],
                            reg["predictions"],
                            alpha=0.6,
                            color="#2563EB",
                            s=30,
                        )
                        min_val = min(reg["y_test"].min(), reg["predictions"].min())
                        max_val = max(reg["y_test"].max(), reg["predictions"].max())
                        ax_reg.plot(
                            [min_val, max_val],
                            [min_val, max_val],
                            "r--",
                            linewidth=1.5,
                            label="Perfect Prediction",
                        )
                        ax_reg.set_xlabel("Actual Score %")
                        ax_reg.set_ylabel("Predicted Score %")
                        ax_reg.set_title("Actual vs Predicted", fontweight="bold")
                        ax_reg.legend()
                        st.pyplot(fig_reg)

                    with reg_col2:
                        st.markdown("**Regression Coefficients**")
                        fig_coef, ax_coef = plt.subplots(figsize=(6, 5))
                        coefs = reg["coefficients"].sort_values()
                        bar_colors = ["#DC2626" if c < 0 else "#16A34A" for c in coefs]
                        coefs.plot(kind="barh", ax=ax_coef, color=bar_colors)
                        ax_coef.axvline(0, color="black", linewidth=0.8)
                        ax_coef.set_xlabel("Coefficient Value")
                        ax_coef.set_title("Feature Coefficients", fontweight="bold")
                        st.pyplot(fig_coef)

                # --- Clustering Tab ---
                with ml_sub_tabs[2]:
                    st.markdown("#### K-Means Clustering: Learner Segmentation")
                    st.caption(
                        "Unsupervised grouping of learners by score, time, and hint usage"
                    )

                    n_clusters = st.slider(
                        "Number of Clusters (K):", min_value=2, max_value=6, value=3
                    )

                    with st.spinner("Running K-Means..."):
                        clust = ml_models.train_clustering(df_ml, n_clusters=n_clusters)

                    st.metric(
                        "Silhouette Score",
                        f"{clust['silhouette_score']:.4f}",
                        help="Ranges from -1 to 1. Higher is better — indicates well-separated clusters.",
                    )

                    st.markdown("**Cluster Summary**")
                    summary_display = clust["cluster_summary"][
                        ["segment", "count", "avg_score", "avg_time", "avg_hints"]
                    ].copy()
                    summary_display.columns = [
                        "Segment",
                        "Count",
                        "Avg Score %",
                        "Avg Time (s)",
                        "Avg Hints",
                    ]
                    st.dataframe(
                        summary_display, use_container_width=True, hide_index=True
                    )

                    clust_col1, clust_col2 = st.columns(2)

                    with clust_col1:
                        st.markdown("**Cluster Visualization (Score vs Time)**")
                        fig_cl, ax_cl = plt.subplots(figsize=(6, 5))
                        df_c = clust["df_clustered"]
                        scatter = ax_cl.scatter(
                            df_c["time_taken_seconds"],
                            df_c["score_percentage"],
                            c=df_c["cluster"],
                            cmap="Set2",
                            alpha=0.7,
                            s=40,
                            edgecolors="white",
                            linewidth=0.5,
                        )
                        ax_cl.set_xlabel("Time Taken (seconds)")
                        ax_cl.set_ylabel("Score %")
                        ax_cl.set_title("K-Means Clusters", fontweight="bold")
                        plt.colorbar(scatter, ax=ax_cl, label="Cluster")
                        st.pyplot(fig_cl)

                    with clust_col2:
                        st.markdown("**Elbow Method (Optimal K)**")
                        fig_el, ax_el = plt.subplots(figsize=(6, 5))
                        ax_el.plot(
                            clust["elbow_data"]["k_range"],
                            clust["elbow_data"]["inertias"],
                            "bo-",
                            linewidth=2,
                            markersize=8,
                        )
                        ax_el.axvline(
                            n_clusters,
                            color="red",
                            linestyle="--",
                            label=f"Selected K={n_clusters}",
                        )
                        ax_el.set_xlabel("Number of Clusters (K)")
                        ax_el.set_ylabel("Inertia (Within-Cluster Sum of Squares)")
                        ax_el.set_title("Elbow Method", fontweight="bold")
                        ax_el.legend()
                        st.pyplot(fig_el)

                # --- Feature Engineering Tab ---
                with ml_sub_tabs[3]:
                    st.markdown("#### Feature Engineering: Derived Features")
                    st.caption(
                        "New features computed from raw attempt data for ML modeling"
                    )

                    df_feat = ml_models.engineer_features(df_ml)
                    feature_cols = [
                        "student_name",
                        "score_percentage",
                        "time_taken_seconds",
                        "hints_used",
                        "speed",
                        "hint_ratio",
                        "is_fast",
                        "attempt_number",
                        "score_improvement",
                    ]
                    st.dataframe(
                        df_feat[feature_cols].head(50),
                        use_container_width=True,
                        column_config={
                            "speed": st.column_config.NumberColumn(
                                "Speed (Q/s)", format="%.4f"
                            ),
                            "hint_ratio": st.column_config.NumberColumn(
                                "Hint Ratio", format="%.2f"
                            ),
                            "score_improvement": st.column_config.NumberColumn(
                                "Score Δ", format="%.1f"
                            ),
                        },
                    )

                    st.markdown("**Correlation Matrix (Engineered Features)**")
                    numeric_cols = [
                        "score_percentage",
                        "time_taken_seconds",
                        "hints_used",
                        "speed",
                        "hint_ratio",
                        "attempt_number",
                        "score_improvement",
                    ]
                    fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
                    corr_matrix = df_feat[numeric_cols].corr()
                    sns.heatmap(
                        corr_matrix,
                        annot=True,
                        fmt=".2f",
                        cmap="RdBu_r",
                        center=0,
                        square=True,
                        linewidths=0.5,
                        ax=ax_corr,
                    )
                    ax_corr.set_title("Feature Correlation Heatmap", fontweight="bold")
                    st.pyplot(fig_corr)

                # --- Advanced SQL Tab ---
                with ml_sub_tabs[4]:
                    st.markdown("#### Advanced SQL Analytics")
                    st.caption(
                        "Aggregation, GROUP BY, and analytical SQL queries on attempt data"
                    )

                    st.markdown("** Top Performers (GROUP BY + HAVING + ORDER BY):**")
                    df_top = analytics.get_top_performers(conn)
                    st.dataframe(df_top, use_container_width=True, hide_index=True)

                    st.markdown("** Daily Attempt Trends (DATE + GROUP BY):**")
                    df_daily = analytics.get_daily_trends(conn)
                    if not df_daily.empty:
                        fig_daily, ax_daily = plt.subplots(figsize=(10, 4))
                        ax_daily.bar(
                            range(len(df_daily)),
                            df_daily["attempts"],
                            color="#93C5FD",
                            label="Attempts",
                        )
                        ax_daily2 = ax_daily.twinx()
                        ax_daily2.plot(
                            range(len(df_daily)),
                            df_daily["avg_score"],
                            "r-o",
                            markersize=4,
                            label="Avg Score %",
                        )
                        ax_daily.set_xlabel("Day Index")
                        ax_daily.set_ylabel("Attempt Count")
                        ax_daily2.set_ylabel("Avg Score %")
                        ax_daily.set_title(
                            "Daily Attempts & Score Trend", fontweight="bold"
                        )
                        ax_daily.legend(loc="upper left")
                        ax_daily2.legend(loc="upper right")
                        st.pyplot(fig_daily)

                    st.markdown("** Hint Usage vs Pass Rate (GROUP BY Analysis):**")
                    df_hints = analytics.get_hint_vs_passrate(conn)
                    st.dataframe(df_hints, use_container_width=True, hide_index=True)

        # TAB 3: QUESTION BANK MANAGEMENT
        with admin_tabs[2]:
            st.markdown("###  Manage Assessment Question Bank")
            q_tab1, q_tab2 = st.tabs([" Add Single Question", " Bulk CSV Upload"])

            with q_tab1:
                with st.form("admin_add_q"):
                    q_text = st.text_area("Question Prompt:")
                    q_a = st.text_input("Option A:")
                    q_b = st.text_input("Option B:")
                    q_c = st.text_input("Option C:")
                    q_d = st.text_input("Option D:")
                    q_corr = st.text_input("Correct Answer (a/b/c/d or option text):")
                    q_hint = st.text_input("Hint (optional):")
                    q_exp = st.text_area("Explanation (optional):")

                    if st.form_submit_button(
                        "Add Question to Repository", type="primary"
                    ):
                        if q_text.strip() and q_a.strip():
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO questions (ques, a, b, c, d, correct, hint, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (q_text, q_a, q_b, q_c, q_d, q_corr, q_hint, q_exp),
                            )
                            conn.commit()
                            st.success("Question added successfully!")
                        else:
                            st.error("Question and Option A are required.")

            with q_tab2:
                uploaded_csv = st.file_uploader(
                    "Upload CSV Question File (e.g. quiz.csv):", type=["csv"]
                )
                if uploaded_csv is not None:
                    try:
                        df_up = pd.read_csv(uploaded_csv)
                        st.write(f"Preview ({len(df_up)} questions detected):")
                        st.dataframe(df_up.head(3))
                        if st.button("Confirm Bulk Import", type="primary"):
                            rows = []
                            for _, r in df_up.iterrows():
                                ques = str(r.get("Question", r.get("ques", ""))).strip()
                                a = str(r.get("Option1", r.get("a", ""))).strip()
                                b = str(r.get("Option2", r.get("b", ""))).strip()
                                c = str(r.get("Option3", r.get("c", ""))).strip()
                                d = str(r.get("Option4", r.get("d", ""))).strip()
                                correct = str(
                                    r.get("CorrectAnswer", r.get("correct", ""))
                                ).strip()
                                hint = (
                                    str(r.get("hint", "")).strip()
                                    if pd.notna(r.get("hint"))
                                    else ""
                                )
                                exp = (
                                    str(r.get("explanation", "")).strip()
                                    if pd.notna(r.get("explanation"))
                                    else ""
                                )
                                if ques:
                                    rows.append((ques, a, b, c, d, correct, hint, exp))
                            cur = conn.cursor()
                            cur.executemany(
                                "INSERT INTO questions (ques, a, b, c, d, correct, hint, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                rows,
                            )
                            conn.commit()
                            st.success(f"Loaded {len(rows)} questions into repository!")
                    except Exception as e:
                        st.error(f"Failed to parse CSV: {e}")

            st.divider()
            st.markdown("#### Current Questions in Repository")
            df_questions = pd.read_sql_query(
                "SELECT qno as 'ID', ques as 'Question', a as 'A', b as 'B', c as 'C', d as 'D', correct as 'Correct Answer' FROM questions ORDER BY qno ASC",
                conn,
            )
            st.dataframe(df_questions, use_container_width=True)

        # TAB 4: REGISTERED ACCOUNTS
        with admin_tabs[3]:
            st.markdown("###  Registered Users & Student Accounts")
            df_users = pd.read_sql_query(
                "SELECT username as 'Username', role as 'Role', status as 'Status' FROM login",
                conn,
            )
            st.dataframe(df_users, use_container_width=True)

        # TAB 5: LEADERBOARD
        with admin_tabs[4]:
            st.markdown("###  Full Assessment Leaderboard")
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(leaderboard)")
            cols = [r[1] for r in cur.fetchall()]
            t_col = "total_questions" if "total_questions" in cols else "limit"
            df_admin_lb = pd.read_sql_query(
                f"SELECT name as 'Candidate', score as 'Score', [{t_col}] as 'Total', scoreper as 'Score %' FROM leaderboard ORDER BY scoreper DESC",
                conn,
            )
            st.dataframe(df_admin_lb, use_container_width=True)
