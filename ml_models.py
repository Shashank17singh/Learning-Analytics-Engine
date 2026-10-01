"""
ml_models.py — Machine Learning Models for Assessment Assessment Analytics
=====================================================================
Implements Classification, Regression, and Clustering using Scikit-learn
to demonstrate applied Data Science on learner performance data.

Models:
    1. Logistic Regression & Random Forest — Predict pass/fail outcome
    2. Linear Regression — Predict score_percentage from engagement features
    3. K-Means Clustering — Auto-segment learners into performance clusters
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    silhouette_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

def engineer_features(df):
    """Create derived features from raw attempt data for ML modeling.

    New features:
        - speed: questions answered per second (efficiency metric)
        - review_ratio: proportion of reviews used vs total questions
        - is_fast: binary flag for below-median completion time
        - attempt_number: nth attempt per student (learning curve)
        - score_improvement: delta from previous attempt per student
    """
    df = df.copy()

    df["speed"] = df["score"] / df["time_taken_seconds"].replace(0, 1)

    median_time = df["time_taken_seconds"].median()
    df["is_fast"] = (df["time_taken_seconds"] < median_time).astype(int)

    df = df.sort_values(["student_name", "attempt_date"])
    df["attempt_number"] = df.groupby("student_name").cumcount() + 1

    df["score_improvement"] = (
        df.groupby("student_name")["score_percentage"].diff().fillna(0)
    )

    return df


CLASSIFICATION_FEATURES = [
    "time_taken_seconds",
    "total_questions",
    "speed",
    "is_fast",
]


def train_classifiers(df):
    """Train Logistic Regression and Random Forest to predict pass/fail.

    Returns:
        dict with model objects, metrics, predictions, and evaluation data.
    """
    df = engineer_features(df)

    X = df[CLASSIFICATION_FEATURES].fillna(0)
    y = df["passed"].astype(int)

    if len(y.unique()) < 2:
        return {"error": "Need both pass and fail records to train classifiers."}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)

    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train_sc, y_train)
    lr_preds = lr.predict(X_test_sc)
    lr_cv = cross_val_score(lr, scaler.transform(X), y, cv=5, scoring="accuracy")

    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_cv = cross_val_score(rf, X, y, cv=5, scoring="accuracy")

    importances = pd.Series(rf.feature_importances_, index=CLASSIFICATION_FEATURES)
    importances = importances.sort_values(ascending=False)

    return {
        "logistic_regression": {
            "model": lr,
            "predictions": lr_preds,
            "accuracy": accuracy_score(y_test, lr_preds),
            "precision": precision_score(y_test, lr_preds, zero_division=0),
            "recall": recall_score(y_test, lr_preds, zero_division=0),
            "f1": f1_score(y_test, lr_preds, zero_division=0),
            "cv_mean": lr_cv.mean(),
            "cv_std": lr_cv.std(),
            "confusion_matrix": confusion_matrix(y_test, lr_preds),
            "report": classification_report(y_test, lr_preds, output_dict=True),
        },
        "random_forest": {
            "model": rf,
            "predictions": rf_preds,
            "accuracy": accuracy_score(y_test, rf_preds),
            "precision": precision_score(y_test, rf_preds, zero_division=0),
            "recall": recall_score(y_test, rf_preds, zero_division=0),
            "f1": f1_score(y_test, rf_preds, zero_division=0),
            "cv_mean": rf_cv.mean(),
            "cv_std": rf_cv.std(),
            "confusion_matrix": confusion_matrix(y_test, rf_preds),
            "report": classification_report(y_test, rf_preds, output_dict=True),
            "feature_importances": importances,
        },
        "y_test": y_test,
        "X_test": X_test,
        "feature_names": CLASSIFICATION_FEATURES,
    }


REGRESSION_FEATURES = [
    "time_taken_seconds",
    "total_questions",
    "speed",
]


def train_regression(df):
    """Train Linear Regression to predict score_percentage.

    Returns:
        dict with model, metrics (MAE, MSE, RMSE, R²), and coefficients.
    """
    df = engineer_features(df)

    X = df[REGRESSION_FEATURES].fillna(0)
    y = df["score_percentage"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    coefficients = pd.Series(model.coef_, index=REGRESSION_FEATURES)

    return {
        "model": model,
        "predictions": preds,
        "y_test": y_test,
        "mae": mean_absolute_error(y_test, preds),
        "mse": mean_squared_error(y_test, preds),
        "rmse": np.sqrt(mean_squared_error(y_test, preds)),
        "r2": r2_score(y_test, preds),
        "intercept": model.intercept_,
        "coefficients": coefficients,
        "feature_names": REGRESSION_FEATURES,
    }


CLUSTER_FEATURES = [
    "score_percentage",
    "time_taken_seconds",
]


def train_clustering(df, n_clusters=3):
    """Apply K-Means clustering to auto-segment learners.

    Returns:
        dict with cluster labels, centroids, silhouette score, and inertia.
    """
    df = df.copy()
    X = df[CLUSTER_FEATURES].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df["cluster"] = labels
    cluster_summary = (
        df.groupby("cluster")
        .agg(
            avg_score=("score_percentage", "mean"),
            avg_time=("time_taken_seconds", "mean"),
            count=("cluster", "size"),
        )
        .sort_values("avg_score", ascending=False)
    )

    cluster_names = {}
    for rank, idx in enumerate(cluster_summary.index):
        if rank == 0:
            cluster_names[idx] = " High Performers"
        elif rank == 1:
            cluster_names[idx] = " Average Learners"
        else:
            cluster_names[idx] = " Needs Support"

    cluster_summary["segment"] = cluster_summary.index.map(cluster_names)
    df["segment"] = df["cluster"].map(cluster_names)

    sil_score = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0.0

    inertias = []
    k_range = range(2, min(9, len(df)))
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    return {
        "model": kmeans,
        "labels": labels,
        "df_clustered": df,
        "cluster_summary": cluster_summary,
        "silhouette_score": sil_score,
        "inertia": kmeans.inertia_,
        "elbow_data": {"k_range": list(k_range), "inertias": inertias},
        "feature_names": CLUSTER_FEATURES,
    }


def print_ml_report(conn):
    """Generate and print a comprehensive ML analysis report to terminal."""
    from analytics import get_attempts_dataframe

    df = get_attempts_dataframe(conn)
    if df.empty or len(df) < 20:
        print("\n[!] Need at least 20 attempt records for ML analysis.")
        return

    print("\n" + "=" * 65)
    print("    MACHINE LEARNING ANALYSIS REPORT (Scikit-learn)")
    print("=" * 65)

    print("\n--- 1. CLASSIFICATION: Pass/Fail Prediction ---")
    clf_results = train_classifiers(df)
    if "error" in clf_results:
        print(f"  [!] {clf_results['error']}")
    else:
        for name, key in [
            ("Logistic Regression", "logistic_regression"),
            ("Random Forest", "random_forest"),
        ]:
            r = clf_results[key]
            print(f"\n  {name}:")
            print(f"    Accuracy:     {r['accuracy']:.4f}")
            print(f"    Precision:    {r['precision']:.4f}")
            print(f"    Recall:       {r['recall']:.4f}")
            print(f"    F1-Score:     {r['f1']:.4f}")
            print(f"    CV Mean (5):  {r['cv_mean']:.4f} ± {r['cv_std']:.4f}")

        print("\n  Feature Importances (Random Forest):")
        for feat, imp in clf_results["random_forest"]["feature_importances"].items():
            print(f"    {feat:<25} {imp:.4f}")

    print("\n--- 2. REGRESSION: Score Prediction ---")
    reg_results = train_regression(df)
    print(f"  MAE:    {reg_results['mae']:.2f}")
    print(f"  RMSE:   {reg_results['rmse']:.2f}")
    print(f"  R²:     {reg_results['r2']:.4f}")
    print("\n  Coefficients:")
    for feat, coef in reg_results["coefficients"].items():
        print(f"    {feat:<25} {coef:+.4f}")

    print("\n--- 3. CLUSTERING: K-Means Learner Segmentation ---")
    cluster_results = train_clustering(df)
    print(f"  Silhouette Score: {cluster_results['silhouette_score']:.4f}")
    print("\n  Cluster Summary:")
    for _, row in cluster_results["cluster_summary"].iterrows():
        print(
            f"    {row['segment']:<22} | n={int(row['count']):>3} | Avg Score: {row['avg_score']:.1f}% | Avg Time: {row['avg_time']:.0f}s"
        )

    print("=" * 65)
