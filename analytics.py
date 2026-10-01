import numpy as np
import pandas as pd


def get_attempts_dataframe(conn):
    """Extract assessment attempts data from SQLite into a Pandas DataFrame."""
    query = """
    SELECT 
        attempt_id,
        student_name,
        score,
        total_questions,
        score_percentage,
        time_taken_seconds,
        reviews_used,
        attempt_date,
        passed
    FROM attempts
    """
    df = pd.read_sql_query(query, conn)
    if not df.empty and "attempt_date" in df.columns:
        df["attempt_date"] = pd.to_datetime(df["attempt_date"], errors="coerce")
    return df


def generate_eda_summary(conn):
    """Generate a comprehensive Exploratory Data Analysis report using Pandas and NumPy."""
    df = get_attempts_dataframe(conn)

    if df.empty:
        print("\n[!] No assessment attempt data available to analyze.")
        return None

    # Calculate key statistical metrics
    total_attempts = len(df)
    unique_students = df["student_name"].nunique()
    pass_count = int(df["passed"].sum())
    fail_count = total_attempts - pass_count
    pass_rate = (pass_count / total_attempts) * 100

    # Score stats (NumPy & Pandas)
    scores = df["score_percentage"].values
    mean_score = float(np.mean(scores))
    median_score = float(np.median(scores))
    std_score = float(np.std(scores))
    q25 = float(np.percentile(scores, 25))
    q75 = float(np.percentile(scores, 75))
    iqr = q75 - q25

    # Time stats
    times = df["time_taken_seconds"].values
    mean_time = float(np.mean(times))
    median_time = float(np.median(times))

    # Reviews stats
    reviews = df["reviews_used"].values
    mean_reviews = float(np.mean(reviews))

    # Correlation Matrix
    corr_time_score = float(df["time_taken_seconds"].corr(df["score_percentage"]))
    corr_reviews_score = float(df["reviews_used"].corr(df["score_percentage"]))

    # Performance Segmentation
    df["performance_tier"] = pd.cut(
        df["score_percentage"],
        bins=[-np.inf, 49.99, 74.99, 100],
        labels=[
            "Needs Improvement (<50%)",
            "Competent (50-74%)",
            "Distinction (75-100%)",
        ],
    )
    tier_counts = df["performance_tier"].value_counts().to_dict()

    print("\n" + "=" * 65)
    print("      DATA SCIENCE: EXPLORATORY DATA ANALYSIS (EDA) REPORT")
    print("=" * 65)
    print("Dataset Overview:")
    print(f"  - Total Assessment Attempts   : {total_attempts}")
    print(f"  - Unique Learners       : {unique_students}")
    print(f"  - Passed Attempts       : {pass_count} ({pass_rate:.1f}%)")
    print(f"  - Failed Attempts       : {fail_count} ({100 - pass_rate:.1f}%)")
    print("-" * 65)
    print("Score Distribution Metrics (NumPy / Pandas):")
    print(f"  - Mean Score            : {mean_score:.2f}%")
    print(f"  - Median Score          : {median_score:.2f}%")
    print(f"  - Standard Deviation    : {std_score:.2f}%")
    print(f"  - 25th Percentile (Q1)  : {q25:.2f}%")
    print(f"  - 75th Percentile (Q3)  : {q75:.2f}%")
    print(f"  - Interquartile Range   : {iqr:.2f}%")
    print(
        f"  - Min / Max Score       : {float(np.min(scores)):.1f}% / {float(np.max(scores)):.1f}%"
    )
    print("-" * 65)
    print("Behavioral & Engagement Metrics:")
    print(
        f"  - Avg Time Taken        : {mean_time:.1f} sec (~{mean_time / 60:.1f} mins)"
    )
    print(f"  - Median Time Taken     : {median_time:.1f} sec")
    print(f"  - Avg Reviews Requested   : {mean_reviews:.1f} reviews / attempt")
    print("-" * 65)
    print("Statistical Correlations (Pearson's r):")
    print(f"  - Time vs Score Corr    : {corr_time_score:+.3f}")
    print(
        f"  - Reviews vs Score Corr   : {corr_reviews_score:+.3f} (Negative: more reviews -> lower score)"
    )
    print("-" * 65)
    print("Learner Performance Tiers:")
    for tier, count in tier_counts.items():
        pct = (count / total_attempts) * 100
        print(f"  - {tier:<26}: {count:>3} attempts ({pct:4.1f}%)")

    print("=" * 65)

    return {
        "df": df,
        "total_attempts": total_attempts,
        "pass_rate": pass_rate,
        "mean_score": mean_score,
        "median_score": median_score,
        "std_score": std_score,
        "mean_time": mean_time,
        "corr_reviews_score": corr_reviews_score,
    }


def export_summary_csv(conn, output_filename="assessment_analytics_export.csv"):
    """Export the enriched dataset to CSV for external BI and Tableau/PowerBI reporting."""
    df = get_attempts_dataframe(conn)
    if df.empty:
        print("[!] No data available to export.")
        return False

    df["performance_tier"] = pd.cut(
        df["score_percentage"],
        bins=[-np.inf, 49.99, 74.99, 100],
        labels=["Needs Improvement", "Competent", "Distinction"],
    )
    df.to_csv(output_filename, index=False)
    print(
        f"[+] Dataset with {len(df)} records exported successfully to '{output_filename}'!"
    )
    return True


def get_top_performers(conn, limit=10):
    """Top students ranked by average score using SQL aggregation."""
    query = """
    SELECT
        student_name,
        COUNT(*) AS total_attempts,
        ROUND(AVG(score_percentage), 2) AS avg_score,
        MAX(score_percentage) AS best_score,
        MIN(score_percentage) AS worst_score,
        ROUND(AVG(time_taken_seconds), 1) AS avg_time_sec,
        ROUND(AVG(reviews_used), 1) AS avg_reviews
    FROM attempts
    GROUP BY student_name
    HAVING COUNT(*) >= 2
    ORDER BY avg_score DESC, total_attempts DESC
    LIMIT %s
    """
    return pd.read_sql_query(query, conn, params=(limit,))


def get_daily_trends(conn):
    """Daily attempt volume and average scores using SQL date functions."""
    query = """
    SELECT
        DATE(attempt_date) AS day,
        COUNT(*) AS attempts,
        ROUND(AVG(score_percentage), 1) AS avg_score,
        SUM(passed) AS passed_count,
        ROUND(SUM(passed) * 100.0 / COUNT(*), 1) AS pass_rate
    FROM attempts
    GROUP BY DATE(attempt_date)
    ORDER BY day ASC
    """
    return pd.read_sql_query(query, conn)


def get_review_vs_passrate(conn):
    """Review usage vs pass rate — demonstrates GROUP BY correlation analysis in SQL."""
    query = """
    SELECT
        reviews_used,
        COUNT(*) AS total_attempts,
        SUM(passed) AS passed,
        ROUND(SUM(passed) * 100.0 / COUNT(*), 1) AS pass_rate,
        ROUND(AVG(score_percentage), 1) AS avg_score,
        ROUND(AVG(time_taken_seconds), 1) AS avg_time
    FROM attempts
    GROUP BY reviews_used
    ORDER BY reviews_used ASC
    """
    return pd.read_sql_query(query, conn)


def get_difficulty_analysis(conn):
    """Analyze assessment difficulty across different question set sizes."""
    query = """
    SELECT
        total_questions AS question_count,
        COUNT(*) AS attempts,
        ROUND(AVG(score_percentage), 1) AS avg_score,
        ROUND(AVG(time_taken_seconds), 1) AS avg_time,
        ROUND(SUM(passed) * 100.0 / COUNT(*), 1) AS pass_rate
    FROM attempts
    GROUP BY total_questions
    ORDER BY total_questions ASC
    """
    return pd.read_sql_query(query, conn)
