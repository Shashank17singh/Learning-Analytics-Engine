import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import analytics

CHARTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")


def ensure_charts_dir():
    """Ensure charts output directory exists."""
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)
    return CHARTS_DIR


def plot_score_distribution(df, save_dir):
    """Plot histogram and KDE distribution of assessment scores with statistical lines."""
    plt.figure(figsize=(9, 5))
    sns.set_theme(style="whitegrid")

    sns.histplot(
        df["score_percentage"],
        kde=True,
        color="#2b5c8f",
        bins=15,
        edgecolor="black",
        alpha=0.65,
    )

    mean_val = df["score_percentage"].mean()
    median_val = df["score_percentage"].median()

    plt.axvline(
        mean_val,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {mean_val:.1f}%",
    )
    plt.axvline(
        median_val,
        color="green",
        linestyle="-.",
        linewidth=2,
        label=f"Median: {median_val:.1f}%",
    )

    plt.title(
        "Learner Score Distribution (Histogram & KDE)",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    plt.xlabel("Score Percentage (%)", fontsize=11)
    plt.ylabel("Frequency (Count of Attempts)", fontsize=11)
    plt.xlim(0, 105)
    plt.legend(frameon=True, facecolor="white")
    plt.tight_layout()

    out_path = os.path.join(save_dir, "score_distribution.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_time_vs_score(df, save_dir):
    """Scatter plot illustrating engagement time vs score, split by pass/fail."""
    plt.figure(figsize=(9, 5))
    sns.set_theme(style="whitegrid")

    palette = {1: "#2ca02c", 0: "#d62728"}
    scatter = sns.scatterplot(
        data=df,
        x="time_taken_seconds",
        y="score_percentage",
        hue="passed",
        palette=palette,
        style="passed",
        s=70,
        alpha=0.85,
    )

    # Trend line
    sns.regplot(
        data=df,
        x="time_taken_seconds",
        y="score_percentage",
        scatter=False,
        color="#333333",
        line_kws={"linewidth": 1.5, "linestyle": "--"},
    )

    plt.title(
        "Assessment Completion Time vs. Score Performance",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    plt.xlabel("Time Taken (Seconds)", fontsize=11)
    plt.ylabel("Score Percentage (%)", fontsize=11)
    plt.ylim(-5, 105)

    # Customize legend
    handles, _ = scatter.get_legend_handles_labels()
    plt.legend(
        handles=handles,
        labels=["Failed (<50%)", "Passed (>=50%)"],
        title="Status",
        frameon=True,
    )
    plt.tight_layout()

    out_path = os.path.join(save_dir, "time_vs_score.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_review_impact(df, save_dir):
    """Boxplot showing how review usage impacts assessment scoring."""
    plt.figure(figsize=(8, 5))
    sns.set_theme(style="whitegrid")

    sns.boxplot(
        data=df,
        x="reviews_used",
        y="score_percentage",
        hue="reviews_used",
        legend=False,
        palette="Blues_r",
        showmeans=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "red",
            "markeredgecolor": "black",
            "markersize": "7",
        },
    )

    plt.title(
        "Impact of Review Usage on Learner Scores", fontsize=14, fontweight="bold", pad=12
    )
    plt.xlabel("Number of Reviews Requested", fontsize=11)
    plt.ylabel("Score Percentage (%)", fontsize=11)
    plt.ylim(-5, 105)
    plt.tight_layout()

    out_path = os.path.join(save_dir, "review_impact_boxplot.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def plot_performance_tiers(df, save_dir):
    """Donut chart illustrating proportion of learner performance tiers."""
    plt.figure(figsize=(7, 7))

    tiers = pd.cut(
        df["score_percentage"],
        bins=[-np.inf, 49.99, 74.99, 100],
        labels=[
            "Needs Improvement (<50%)",
            "Competent (50-74%)",
            "Distinction (75-100%)",
        ],
    )
    counts = tiers.value_counts()
    colors = ["#ff9999", "#66b3ff", "#99ff99"]

    plt.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor="white"),
    )

    plt.title(
        "Learner Performance Segmentation", fontsize=14, fontweight="bold", pad=12
    )
    plt.tight_layout()

    out_path = os.path.join(save_dir, "performance_tiers_donut.png")
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def generate_all_charts(conn):
    """Generate all analytical plots and return list of saved chart filepaths."""
    df = analytics.get_attempts_dataframe(conn)
    if df.empty:
        print("\n[!] No attempt data available to generate charts.")
        return []

    charts_dir = ensure_charts_dir()
    print("\n[*] Generating Data Science Visualizations (Matplotlib & Seaborn)...")

    p1 = plot_score_distribution(df, charts_dir)
    print(f"  [+] Saved Score Distribution: {os.path.basename(p1)}")

    p2 = plot_time_vs_score(df, charts_dir)
    print(f"  [+] Saved Time vs Score Plot: {os.path.basename(p2)}")

    p3 = plot_review_impact(df, charts_dir)
    print(f"  [+] Saved Review Impact Boxplot: {os.path.basename(p3)}")

    p4 = plot_performance_tiers(df, charts_dir)
    print(f"  [+] Saved Performance Tiers Chart: {os.path.basename(p4)}")

    print(f"\n[+] All 4 visual analytics charts successfully generated in:")
    print(f"    {charts_dir}\n")

    return [p1, p2, p3, p4]
