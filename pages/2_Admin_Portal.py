import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

import analytics
import ml_models
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

    
    
    
    /* Fix tab text clipping completely */
    .stTabs button {
        height: 50px !important;
        min-height: 50px !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        overflow: visible !important;
    }
    .stTabs button * {
        overflow: visible !important;
        font-size: 15px !important;
        line-height: 1.8 !important;
        padding-top: 4px !important;
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


if not st.session_state.authenticated or st.session_state.user_role != "admin":
    st.switch_page("app.py")
    st.stop()

conn = get_db_connection()

# =========================================================
# ROLE B: ADMINISTRATOR DASHBOARD
# =========================================================
admin_tabs = st.tabs(
    [
        " Cohort Analytics & BI Dashboard",
        " ML & Predictive Analytics",
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
        k1, k2, k3, k4 = st.columns(4)
        tot = len(df_cohort)
        pass_cnt = int(df_cohort["passed"].sum())
        k1.metric("Total Attempts", tot)
        k2.metric("Cohort Pass Rate", f"{(pass_cnt / tot) * 100:.1f}%")
        k3.metric("Mean Score", f"{df_cohort['score_percentage'].mean():.1f}%")
        k4.metric(
            "Avg Completion Time",
            f"{df_cohort['time_taken_seconds'].mean():.0f}s",
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
            fig4, ax4 = plt.subplots(figsize=(7, 4.5))
            t_counts = df_cohort["Performance Tier"].value_counts()
            ax4.pie(
                t_counts,
                labels=t_counts.index,
                autopct="%1.1f%%",
                startangle=140,
                colors=["#99ff99", "#66b3ff", "#ff9999"],
                wedgeprops={"width": 0.4, "edgecolor": "white"},
            )
            ax4.set_title("Cohort Competency Breakdown", fontweight="bold")
            st.pyplot(fig4)

        st.markdown("#### Complete Cohort Attempt Records")
        st.dataframe(df_cohort, width="stretch")
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
    df_ml = pd.read_sql_query("SELECT * FROM attempts ORDER BY attempt_date ASC", conn)

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
                "Models: Logistic Regression & Random Forest | Features: time, speed"
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
                    width="stretch",
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
                "Unsupervised grouping of learners by score, time, and review usage"
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
                ["segment", "count", "avg_score", "avg_time"]
            ].copy()
            summary_display.columns = [
                "Segment",
                "Count",
                "Avg Score %",
                "Avg Time (s)",
                "Avg Reviews",
            ]
            st.dataframe(summary_display, width="stretch", hide_index=True)

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
            st.caption("New features computed from raw attempt data for ML modeling")

            df_feat = ml_models.engineer_features(df_ml)
            feature_cols = [
                "student_name",
                "score_percentage",
                "time_taken_seconds",
                "reviews_used",
                "speed",
                "review_ratio",
                "is_fast",
                "attempt_number",
                "score_improvement",
            ]
            st.dataframe(
                df_feat[feature_cols].head(50),
                width="stretch",
                column_config={
                    "speed": st.column_config.NumberColumn(
                        "Speed (Q/s)", format="%.4f"
                    ),
                    "review_ratio": st.column_config.NumberColumn(
                        "Review Ratio", format="%.2f"
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
                "reviews_used",
                "speed",
                "review_ratio",
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
            st.dataframe(df_top, width="stretch", hide_index=True)

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
                ax_daily.set_title("Daily Attempts & Score Trend", fontweight="bold")
                ax_daily.legend(loc="upper left")
                ax_daily2.legend(loc="upper right")
                st.pyplot(fig_daily)

            st.markdown("** Review Usage vs Pass Rate (GROUP BY Analysis):**")
            df_reviews = analytics.get_review_vs_passrate(conn)
            st.dataframe(df_reviews, width="stretch", hide_index=True)

# TAB 3: REGISTERED ACCOUNTS
with admin_tabs[2]:
    st.markdown("###  Registered Users & Student Accounts")
    df_users = pd.read_sql_query(
        "SELECT username as 'Username', role as 'Role', status as 'Status' FROM login",
        conn,
    )
    st.dataframe(df_users, width="stretch")

# TAB 4: LEADERBOARD
with admin_tabs[3]:
    st.markdown("###  Full Assessment Leaderboard")
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(leaderboard)")
    cols = [r[1] for r in cur.fetchall()]
    t_col = "total_questions" if "total_questions" in cols else "limit"
    df_admin_lb = pd.read_sql_query(
        f"SELECT name as 'Candidate', score as 'Score', [{t_col}] as 'Total', scoreper as 'Score %' FROM leaderboard ORDER BY scoreper DESC",
        conn,
    )
    st.dataframe(df_admin_lb, width="stretch")
