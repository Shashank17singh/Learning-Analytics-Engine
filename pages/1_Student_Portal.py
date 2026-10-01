import json
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

import llm_utils
from db_utils import get_db_connection, init_db
from pypdf import PdfReader

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
# HELPER FUNCTIONS
# -------------------------------------------------------------
def format_time_str(seconds):
    if pd.isna(seconds):
        return ""
    s = int(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    s = s % 60
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

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
            
            source_type = st.radio("Select Assessment Source:", ["Select Topic from Catalog", "Upload Study Material (PDF)"], horizontal=True)
            
            pdf_context = None
            ai_domain = ""
            ai_subject = ""
            custom_topic = ""
            
            if source_type == "Upload Study Material (PDF)":
                uploaded_file = st.file_uploader("Upload a PDF document to generate questions from its contents", type=["pdf"])
                if uploaded_file is not None:
                    try:
                        reader = PdfReader(uploaded_file)
                        text = ""
                        for page in reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        # Limit text to avoid blowing up context window
                        pdf_context = text[:30000] 
                        st.success(f"Successfully extracted {len(pdf_context)} characters from the PDF.")
                        
                        ai_domain = "Custom PDF"
                        ai_subject = uploaded_file.name
                        custom_topic = f"PDF: {uploaded_file.name}"
                        st.session_state.selected_domain = ai_domain
                        st.session_state.selected_subject = ai_subject
                        st.session_state.custom_topic = custom_topic
                        st.session_state.pdf_context = pdf_context
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")
            else:
                # Load extensive domains catalog
                try:
                    with open("domains_catalog.json", "r") as f:
                        ai_domains_catalog = json.load(f)
                except FileNotFoundError:
                    ai_domains_catalog = {
                        "General": ["General Knowledge", "Custom Topic..."]
                    }

                current_level = ai_domains_catalog
                selections = []
                labels = ["Broad Domain", "Branch / Course", "Category / Specialization", "Topic / Exam"]
                
                level_idx = 0
                custom_triggered = False
                
                while isinstance(current_level, dict):
                    options = list(current_level.keys()) + ["Other / Custom..."]
                    label = labels[level_idx] if level_idx < len(labels) else f"Level {level_idx+1}"
                    selection = st.selectbox(f"Search/Select {label}:", options, key=f"sel_{level_idx}")
                    
                    if selection == "Other / Custom...":
                        custom_triggered = True
                        break
                        
                    selections.append(selection)
                    current_level = current_level[selection]
                    level_idx += 1
                    
                if not custom_triggered and isinstance(current_level, list):
                    options = current_level + ["Other / Custom..."]
                    label = labels[level_idx] if level_idx < len(labels) else "Specific Subject"
                    final_selection = st.selectbox(f"Search/Select {label}:", options, key=f"sel_final")
                    if final_selection == "Other / Custom...":
                        custom_triggered = True
                    else:
                        selections.append(final_selection)

                ai_domain = selections[0] if selections else "Custom"
                
                if custom_triggered:
                    custom_topic_input = st.text_input(
                        "Type your custom topic / specialization here:", value=""
                    )
                    if not selections:
                        ai_domain = "Custom"
                        ai_subject = custom_topic_input
                        custom_topic = custom_topic_input
                    else:
                        ai_subject = " - ".join(selections[1:]) + (" - " + custom_topic_input if custom_topic_input else "")
                        ai_subject = ai_subject.strip(" -")
                        custom_topic = f"{ai_domain} - {ai_subject}" if ai_domain != "Custom" else custom_topic_input
                else:
                    ai_subject = " - ".join(selections[1:]) if len(selections) > 1 else "General Knowledge"
                    custom_topic = f"{ai_domain} - {ai_subject}"

                    if not custom_topic.strip() or custom_topic.strip() == "-":
                        custom_topic = "General Knowledge"
                        ai_subject = "General Knowledge"

                    st.session_state.selected_domain = ai_domain
                    st.session_state.selected_subject = ai_subject
                    st.session_state.custom_topic = custom_topic
                    st.session_state.pdf_context = None

            exam_rules = {
                "JEE Mains": {"q": 75, "cm": 4, "im": -1, "time": 180, "diff": "Hard"},
                "JEE Advanced": {"q": 54, "cm": 3, "im": -1, "time": 180, "diff": "Hard"},
                "BITSAT": {"q": 130, "cm": 3, "im": -1, "time": 180, "diff": "Medium"},
                "GATE": {"q": 65, "cm": 1, "im": -0.33, "time": 180, "diff": "Hard"},
                "NEET": {"q": 180, "cm": 4, "im": -1, "time": 200, "diff": "Medium"},
                "CAT": {"q": 66, "cm": 3, "im": -1, "time": 120, "diff": "Hard"},
                "XAT": {"q": 105, "cm": 1, "im": -0.25, "time": 210, "diff": "Hard"},
                "SNAP": {"q": 60, "cm": 1, "im": -0.25, "time": 60, "diff": "Medium"},
                "GMAT": {"q": 80, "cm": 1, "im": 0, "time": 195, "diff": "Hard"},
                "GRE": {"q": 80, "cm": 1, "im": 0, "time": 225, "diff": "Hard"},
                "NMAT": {"q": 108, "cm": 1, "im": 0, "time": 120, "diff": "Medium"},
                "MAT": {"q": 200, "cm": 1, "im": -0.25, "time": 150, "diff": "Easy"},
                "CMAT": {"q": 100, "cm": 4, "im": -1, "time": 180, "diff": "Medium"},
                "CUET (UG)": {"q": 50, "cm": 5, "im": -1, "time": 45, "diff": "Medium"},
                "CUET (PG)": {"q": 75, "cm": 4, "im": -1, "time": 105, "diff": "Medium"},
                "IPMAT": {"q": 90, "cm": 4, "im": -1, "time": 120, "diff": "Hard"},
                "NPAT": {"q": 120, "cm": 1, "im": 0, "time": 100, "diff": "Medium"},
                "UPSC": {"q": 100, "cm": 2, "im": -0.66, "time": 120, "diff": "Hard"},
                "NDA": {"q": 120, "cm": 2.5, "im": -0.83, "time": 150, "diff": "Medium"},
                "CLAT": {"q": 120, "cm": 1, "im": -0.25, "time": 120, "diff": "Medium"}
            }
            if source_type == "Upload Study Material (PDF)" and not uploaded_file:
                # Do not show exam configs if no file is uploaded yet
                pass
            else:
                matched_exam = None
                for ex, rules in exam_rules.items():
                    if ex in ai_subject or ex in ai_domain or ex in custom_topic:
                        matched_exam = ex
                        break
                
                if matched_exam:
                    st.info(f" **{matched_exam} Format Detected!** Applying official marking scheme and settings.")
                    q_val = exam_rules[matched_exam]['q']
                    if "Mock" not in ai_subject and "Mock" not in custom_topic:
                        q_val = max(10, q_val // 3)
                        st.caption(f"Note: Adjusted to {q_val} questions for a single subject section.")
                    
                    num_questions_chosen = q_val
                    cm_val = exam_rules[matched_exam]['cm']
                    im_val = exam_rules[matched_exam]['im']
                    time_val = exam_rules[matched_exam]['time']
                    difficulty_level = exam_rules[matched_exam]['diff']
                    
                    st.write(f"**Questions:** {q_val} | **Time Limit:** {time_val} mins | **Marking:** +{cm_val} / {im_val} | **Difficulty:** {difficulty_level}")
                else:
                    q_options = [5, 10, 15, 20, 25, 30, 40, 50]
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
                    cm_val = 1
                    im_val = 0
                    time_val = None

            if not (source_type == "Upload Study Material (PDF)" and not uploaded_file):
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
                        st.session_state.difficulty_level = difficulty_level
                        st.session_state.cm_val = cm_val
                        st.session_state.im_val = im_val
                        st.session_state.time_limit_mins = time_val
                        st.session_state.num_questions = num_questions_chosen
    
                        topic_for_gen = st.session_state.get("custom_topic", "General")
                        if not topic_for_gen.strip():
                            topic_for_gen = "General Knowledge"
    
                        pdf_context = st.session_state.get("pdf_context", None)
    
                        with st.spinner(
                            f"Preparing your {difficulty_level.lower()} assessment module on '{topic_for_gen}'..."
                        ):
                            gen_qs = llm_utils.generate_gemini_questions(
                                topic_for_gen, num_questions_chosen, difficulty_level, context=pdf_context
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

            time_limit = st.session_state.get('time_limit_mins')
            time_str = f" |  Time Limit: {time_limit} mins" if time_limit else ""
            cm_val = st.session_state.get('cm_val', 1)
            im_val = st.session_state.get('im_val', 0)
            mark_str = f" |  Marking: +{cm_val} / {im_val}" if cm_val != 1 or im_val != 0 else ""

            with st.form("student_assessment_form"):
                st.markdown(
                    f"**Answering {len(assessment_set)} Randomized Questions**{time_str}{mark_str}"
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
                incorrect_count = 0
                unattempted_count = 0
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
                    if c_val is None:
                        unattempted_count += 1
                        continue

                    is_correct = False
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
                        incorrect_count += 1
                        st.session_state.setdefault("incorrect_answers", []).append({
                            "qno": qno,
                            "ques": ques,
                            "selected": c_val,
                            "correct": correct,
                            "explanation": exp
                        })

                cm_val = st.session_state.get('cm_val', 1)
                im_val = st.session_state.get('im_val', 0)
                
                raw_score = (correct_count * cm_val) + (incorrect_count * im_val)
                max_possible_score = total_q * cm_val
                
                # Prevent negative percentage if they got heavily penalized
                score_percentage = max(0.0, (raw_score / max_possible_score) * 100.0) if max_possible_score > 0 else 0.0
                passed = 1 if score_percentage >= 50.0 else 0

                # Save attempt
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO attempts (
                        student_name, score, total_questions, score_percentage,
                        time_taken_seconds, reviews_used, attempt_date, passed, domain, subject, difficulty
                    ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
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
                        st.session_state.get("difficulty_level", "Medium"),
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
                        f" **Outstanding Performance, {st.session_state.username.title()}!** You scored **{raw_score:.2f} out of {max_possible_score}** ({score_percentage:.1f}%)."
                    )
                elif score_percentage >= 50.0:
                    st.balloons()
                    st.success(
                        f" **Great Job, {st.session_state.username.title()}!** You successfully completed the assessment with **{raw_score:.2f}/{max_possible_score}** ({score_percentage:.1f}%)."
                    )
                else:
                    st.success(
                        f" **Assessment Completed Successfully!** Good effort, **{st.session_state.username.title()}**! Score: **{raw_score:.2f}/{max_possible_score}** ({score_percentage:.1f}%)."
                    )

                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                col_res1.metric("Your Score", f"{raw_score:.2f} / {max_possible_score}")
                col_res2.metric("Accuracy", f"{score_percentage:.1f}%")
                col_res3.metric("Duration", format_time_str(duration))
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
            "SELECT * FROM attempts WHERE LOWER(TRIM(student_name)) = ? ORDER BY attempt_id ASC",
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

            # Personal Visual Grid (2x2)
            df_my["Performance Tier"] = pd.cut(
                df_my["score_percentage"],
                bins=[-np.inf, 49.99, 74.99, 100],
                labels=[
                    "Needs Improvement (<50%)",
                    "Competent (50-74%)",
                    "Distinction (75-100%)",
                ],
            )

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                fig1, ax1 = plt.subplots(figsize=(7, 4.5))
                sns.histplot(
                    df_my["score_percentage"],
                    kde=True,
                    color="#1E40AF",
                    bins=12,
                    ax=ax1,
                )
                if len(df_my) > 0:
                    ax1.axvline(
                        df_my["score_percentage"].mean(),
                        color="red",
                        linestyle="--",
                        label=f"Mean: {df_my['score_percentage'].mean():.1f}%",
                    )
                    ax1.axvline(
                        df_my["score_percentage"].median(),
                        color="green",
                        linestyle="-.",
                        label=f"Median: {df_my['score_percentage'].median():.1f}%",
                    )
                ax1.set_title(
                    "Personal Score Distribution (Histogram & KDE)", fontweight="bold"
                )
                ax1.set_xlabel("Score %")
                ax1.legend()
                st.pyplot(fig1)

            with row1_col2:
                fig2, ax2 = plt.subplots(figsize=(7, 4.5))
                sns.scatterplot(
                    data=df_my,
                    x="time_taken_seconds",
                    y="score_percentage",
                    hue="passed",
                    palette={True: "#2ca02c", False: "#d62728"},
                    s=60,
                    alpha=0.85,
                    ax=ax2,
                )
                if len(df_my) > 1:
                    sns.regplot(
                        data=df_my,
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
                fig4, ax4 = plt.subplots(figsize=(7, 4.5))
                t_counts = df_my["Performance Tier"].value_counts()
                ax4.pie(
                    t_counts,
                    labels=t_counts.index,
                    autopct="%1.1f%%",
                    startangle=140,
                    colors=["#99ff99", "#66b3ff", "#ff9999"],
                    wedgeprops={"width": 0.4, "edgecolor": "white"},
                )
                ax4.set_title("Personal Competency Breakdown", fontweight="bold")
                st.pyplot(fig4)

            st.divider()
            st.markdown("#### Assessment History")
            df_my_display = df_my.copy()
            df_my_display["attempt_date"] = pd.to_datetime(df_my_display["attempt_date"])
            df_my_display["passed"] = df_my_display["passed"].apply(lambda x: "Passed" if x else "Failed")
            df_my_display["time_taken_seconds"] = df_my_display["time_taken_seconds"].apply(format_time_str)
            st.dataframe(
                df_my_display[
                    [
                        "attempt_id",
                        "attempt_date",
                        "score",
                        "total_questions",
                        "score_percentage",
                        "time_taken_seconds",
                        "passed",
                        "difficulty",
                    ]
                ],
                width="stretch",
                hide_index=True,
                column_config={
                    "attempt_id": "Attempt ID",
                    "attempt_date": st.column_config.DatetimeColumn("Attempt Date", format="DD-MM-YYYY HH:mm:ss"),
                    "score": "Score",
                    "total_questions": "Total Questions",
                    "score_percentage": st.column_config.NumberColumn(
                        "Score %", format="%.1f%%"
                    ),
                    "time_taken_seconds": "Time Taken",
                    "passed": "Result",
                    "difficulty": "Difficulty",
                },
            )

    # TAB 3: LEADERBOARD
    with student_tabs[2]:
        st.markdown("###  Real-Time Hall of Fame")
        
        df_filters = pd.read_sql_query(
            "SELECT DISTINCT domain, subject FROM attempts WHERE student_name = ?", 
            conn, params=(st.session_state.username,)
        )
        
        if df_filters.empty:
            st.info("You haven't taken any assessments yet. Complete an assessment to unlock its leaderboard!")
            st.stop()
            
        col1, col2, col3 = st.columns(3)
        with col1:
            domains = ["All"] + sorted(df_filters["domain"].dropna().unique().tolist())
            selected_domain = st.selectbox("Filter by Domain", domains, key="lb_domain")
        with col2:
            if selected_domain == "All":
                subjects_list = sorted(df_filters["subject"].dropna().unique().tolist())
            else:
                subjects_list = sorted(df_filters[df_filters["domain"] == selected_domain]["subject"].dropna().unique().tolist())
            subjects = ["All"] + subjects_list
            selected_subject = st.selectbox("Filter by Subject", subjects, key="lb_subject")
        with col3:
            df_diffs = pd.read_sql_query("SELECT DISTINCT difficulty FROM attempts", conn)
            difficulties = ["All"] + sorted(df_diffs["difficulty"].dropna().unique().tolist())
            selected_difficulty = st.selectbox("Filter by Difficulty", difficulties, key="lb_diff")

        query = "SELECT student_name, score, total_questions, score_percentage, domain, subject, difficulty FROM attempts WHERE 1=1"
        params = []
        if selected_domain != "All":
            query += " AND domain = ?"
            params.append(selected_domain)
        if selected_subject != "All":
            query += " AND subject = ?"
            params.append(selected_subject)
        if selected_difficulty != "All":
            query += " AND difficulty = ?"
            params.append(selected_difficulty)
            
        df_all = pd.read_sql_query(query, conn, params=params)

        if not df_all.empty:
            allowed_combinations = set(zip(df_filters['domain'], df_filters['subject']))
            df_all = df_all[df_all.apply(lambda row: (row['domain'], row['subject']) in allowed_combinations, axis=1)]

        if not df_all.empty:
            # Get best attempt per student
            idx = df_all.groupby('student_name')['score_percentage'].idxmax()
            df_lb = df_all.loc[idx].sort_values(by=['score_percentage', 'score'], ascending=[False, False]).head(50).reset_index(drop=True)
            
            df_lb.rename(columns={
                "student_name": "Student",
                "score": "Score",
                "total_questions": "Total",
                "score_percentage": "Score %",
                "domain": "Domain",
                "subject": "Subject",
                "difficulty": "Difficulty"
            }, inplace=True)
            
            ranks = [
                (" 1st" if i == 0 else " 2nd" if i == 1 else " 3rd" if i == 2 else f"{i + 1}th")
                for i in range(len(df_lb))
            ]
            df_lb.insert(0, "Rank", ranks)
            st.dataframe(
                df_lb, 
                width="stretch", 
                hide_index=True,
                column_config={
                    "Score %": st.column_config.NumberColumn("Score %", format="%.1f%%")
                }
            )
        else:
            st.info("Leaderboard is currently empty for the selected filters.")

# =========================================================
