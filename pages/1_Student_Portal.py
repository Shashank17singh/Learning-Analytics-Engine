import json
import time

import pandas as pd
import streamlit as st

import llm_utils
from db_utils import get_db_connection, init_db

# -------------------------------------------------------------
# PAGE CONFIGURATION (NO SIDEBAR, FULL BROWSER APP LAYOUT)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Assessment & Analytics Portal",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    .block-container {
        padding-top: 4rem;
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

    
    
    /* Fix Streamlit tab and button text clipping */
    [data-testid="stTabs"] [role="tablist"] {
        padding-top: 15px !important;
        height: auto !important;
    }
    [data-testid="stTabs"] [role="tab"] p {
        margin-top: 10px !important;
        margin-bottom: 0 !important;
        line-height: normal !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

import auth_utils

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
auth_utils.sync_session_state()

# Logout Button UI
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Logout", key="logout_btn", use_container_width=True):
        auth_utils.logout_user()
        st.switch_page("app.py")


if not st.session_state.authenticated or st.session_state.user_role == "admin":
    st.switch_page("app.py")
    st.stop()

conn = get_db_connection()

# =========================================================
# ROLE A: STUDENT DASHBOARD
# =========================================================
if st.session_state.user_role != "admin":
    student_tabs = st.tabs(
        [
            "Take Assessment",
            "My Performance & Analytics",
            "Hall of Fame (Leaderboard)",
        ]
    )

    # TAB 1: TAKE ASSESSMENT
    with student_tabs[0]:
        st.markdown("###  Active Assessment: Dynamic Domain & Subject Selection")
        if not st.session_state.get("student_assessment_started", False):
            # Load extensive domains catalog
            try:
                with open("domains_catalog.json", "r") as f:
                    ai_domains_catalog = json.load(f)
            except FileNotFoundError:
                ai_domains_catalog = {
                    "General": ["General Knowledge", "Custom Topic..."]
                }

            col_aid, col_ais = st.columns(2)
            with col_aid:
                ai_domain = st.selectbox(
                    "Search/Select Broad Domain:", list(ai_domains_catalog.keys())
                )

            with col_ais:
                ai_subject = st.selectbox(
                    "Search/Select Specific Subject:",
                    ai_domains_catalog.get(ai_domain, ["Custom Topic..."]),
                )

            if ai_subject == "Custom Topic...":
                custom_topic = st.text_input(
                    "Type your completely custom topic here:", value=""
                )
            else:
                custom_topic = f"{ai_domain} - {ai_subject}"

            st.session_state.selected_domain = ai_domain
            st.session_state.selected_subject = (
                ai_subject if ai_subject != "Custom Topic..." else "Custom"
            )
            st.session_state.custom_topic = custom_topic

            q_options = [5, 10, 15, 20, 25]
            
            col_q, col_diff = st.columns(2)
            with col_q:
                num_questions_chosen = st.select_slider(
                    " Number of Questions:",
                    options=q_options,
                    value=10,
                )
            with col_diff:
                difficulty_level = st.select_slider(
                    " Select Difficulty:",
                    options=["Easy", "Medium", "Hard"],
                    value="Medium"
                )

            st.write("")
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                if st.button(
                    "Start Assessment Now ",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.student_assessment_started = True
                    st.session_state.assessment_start_time = time.time()

                    provider = "Gemini"
                    topic_for_gen = st.session_state.get("custom_topic", "General")
                    if not topic_for_gen.strip():
                        topic_for_gen = "General Knowledge"

                    with st.spinner(
                        f"{provider} is generating your {difficulty_level.lower()} custom exam on '{topic_for_gen}'..."
                    ):
                        gen_qs = llm_utils.generate_gemini_questions(
                            topic_for_gen, num_questions_chosen, difficulty_level
                        )

                    if gen_qs:
                        mapped_qs = [
                            (
                                q.get("qno", i),
                                q.get("ques", ""),
                                q.get("a", ""),
                                q.get("b", ""),
                                q.get("c", ""),
                                q.get("d", ""),
                                q.get("correct", ""),
                                q.get("explanation", ""),
                            )
                            for i, q in enumerate(gen_qs, 1)
                        ]
                        st.session_state.assessment_set = mapped_qs
                        st.rerun()
                    else:
                        st.error(
                            f"{provider.split()[0]} failed to generate questions. Ensure API Key is valid and try again."
                        )
                        st.session_state.student_assessment_started = False
                        st.stop()
        else:
            assessment_set = st.session_state.get("assessment_set")
            if not assessment_set:
                st.warning("No questions loaded. Please start a new assessment.")
                st.session_state.student_assessment_started = False
                st.rerun()
            user_choices = {}

            with st.form("student_assessment_form"):
                st.markdown(
                    f"**Answering {len(assessment_set)} Randomized Questions:**"
                )
                for idx, (
                    qno,
                    ques,
                    a,
                    b,
                    c,
                    d,
                    correct,
                    explanation,
                ) in enumerate(assessment_set, 1):
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
                        ques,
                    )

                    st.write("")

                submit_assessment = st.form_submit_button(
                    " Finish & Submit Assessment",
                    type="primary",
                    width="stretch",
                )

            if submit_assessment:
                duration = max(
                    1, int(time.time() - st.session_state.assessment_start_time)
                )
                correct_count = 0
                total_q = len(assessment_set)
                reviews_used_count = sum(
                    1
                    for qno in user_choices
                    if st.session_state.get(f"review_{qno}", False)
                )

                for qno, (
                    c_val,
                    correct,
                    a,
                    b,
                    c,
                    d,
                    exp,
                    ques,
                ) in user_choices.items():
                    is_correct = False
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
                                is_correct = True
                        elif c_val == clean_corr:
                            is_correct = True

                    if is_correct:
                        correct_count += 1
                    else:
                        st.session_state.setdefault("incorrect_answers", []).append({
                            "qno": qno,
                            "ques": ques,
                            "selected": c_val if c_val else "No Answer Selected",
                            "correct": correct,
                            "explanation": exp
                        })

                score_percentage = (correct_count / total_q) * 100.0
                passed = 1 if score_percentage >= 50.0 else 0

                # Save attempt
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO attempts (
                        student_name, score, total_questions, score_percentage,
                        time_taken_seconds, reviews_used, attempt_date, passed, domain, subject
                    ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?)
                    """,
                    (
                        st.session_state.username,
                        correct_count,
                        total_q,
                        score_percentage,
                        duration,
                        reviews_used_count,
                        passed,
                        st.session_state.get("selected_domain", "General"),
                        st.session_state.get("selected_subject", "General"),
                    ),
                )

                # Save leaderboard
                cur.execute("PRAGMA table_info(leaderboard)")
                cols = [r[1] for r in cur.fetchall()]
                t_col = "total_questions" if "total_questions" in cols else "limit"
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

                if st.session_state.get("incorrect_answers"):
                    st.divider()
                    st.markdown("###  Detailed Review of Incorrect Answers")
                    st.info("Here is a breakdown of the questions you got wrong, including a specific explanation of why your chosen answer was incorrect.")
                    
                    for d in st.session_state.incorrect_answers:
                        with st.expander(f"Question {d['qno']}: {d['ques']}"):
                            st.markdown(f" **Your Answer:** {d['selected']}")
                            st.markdown(f" **Correct Answer:** {d['correct']}")
                            
                            with st.spinner("Generating targeted explanation..."):
                                targeted_exp = llm_utils.explain_wrong_answer(d['ques'], d['selected'], d['correct'], d['explanation'])
                            
                            st.markdown(f"**Explanation:** {targeted_exp}")

                st.session_state.student_assessment_started = False
                st.session_state.assessment_set = None
                st.session_state.incorrect_answers = []
                
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
            df_my['passed'] = df_my['passed'].astype(bool)
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
                        "passed",
                    ]
                ],
                width="stretch",
                hide_index=True,
                column_config={
                    "attempt_date": "Attempt Date",
                    "score": "Score",
                    "total_questions": "Total Questions",
                    "score_percentage": st.column_config.ProgressColumn(
                        "Score %", format="%.1f%%", min_value=0, max_value=100
                    ),
                    "time_taken_seconds": "Time Taken (s)",
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
                    " 1st"
                    if i == 0
                    else " 2nd"
                    if i == 1
                    else " 3rd"
                    if i == 2
                    else f"{i + 1}th"
                )
                for i in range(len(df_lb))
            ]
            df_lb.insert(0, "Rank", ranks)
            st.dataframe(df_lb, width="stretch", hide_index=True)
        else:
            st.info("Leaderboard is currently empty.")

# =========================================================
