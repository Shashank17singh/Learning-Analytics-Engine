"""
Machine Learning models for assessment analytics.
Provides a unified interface for classification, regression, and clustering.
"""
import logging
from dataclasses import dataclass
from typing import Dict, Any, List

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

logger = logging.getLogger(__name__)

# Core features used across multiple models
BASE_FEATURES = [
    "time_taken_seconds",
    "total_questions",
    "speed",
]
CLASSIFICATION_FEATURES = BASE_FEATURES + ["is_fast"]


@dataclass
class ModelResult:
    """Standardized container for machine learning evaluation results."""
    model: Any
    predictions: np.ndarray
    metrics: Dict[str, float]
    feature_names: List[str]
    additional_data: Dict[str, Any]


class AssessmentAnalyticsModel:
    """
    Facade for all Machine Learning operations on assessment data.
    Provides feature engineering, classification, regression, and clustering capabilities.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Derives velocity and progression metrics from raw assessment attempts."""
        df = df.copy()
        
        # Calculate speed (score per second)
        df["speed"] = df["score"] / df["time_taken_seconds"].replace(0, 1)

        # Boolean flag for attempts faster than the global median
        median_time = df["time_taken_seconds"].median()
        df["is_fast"] = (df["time_taken_seconds"] < median_time).astype(int)

        # Calculate attempt trajectory
        df = df.sort_values(["student_name", "attempt_date"])
        df["attempt_number"] = df.groupby("student_name").cumcount() + 1
        df["score_improvement"] = df.groupby("student_name")["score_percentage"].diff().fillna(0)

        return df

    def train_classifiers(self, df: pd.DataFrame) -> Dict[str, ModelResult]:
        """Trains Logistic Regression and Random Forest models to predict pass/fail."""
        df = self.engineer_features(df)
        X = df[CLASSIFICATION_FEATURES].fillna(0)
        y = df["passed"].astype(int)

        if len(y.unique()) < 2:
            logger.warning("Insufficient class variance (needs both pass and fail records).")
            return {}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=self.random_state, stratify=y
        )

        scaler = StandardScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc = scaler.transform(X_test)

        results = {}

        # Logistic Regression
        lr = LogisticRegression(random_state=self.random_state, max_iter=1000)
        lr.fit(X_train_sc, y_train)
        lr_preds = lr.predict(X_test_sc)
        lr_cv = cross_val_score(lr, scaler.transform(X), y, cv=5, scoring="accuracy")

        results["logistic_regression"] = ModelResult(
            model=lr,
            predictions=lr_preds,
            metrics={
                "accuracy": accuracy_score(y_test, lr_preds),
                "precision": precision_score(y_test, lr_preds, zero_division=0),
                "recall": recall_score(y_test, lr_preds, zero_division=0),
                "f1": f1_score(y_test, lr_preds, zero_division=0),
                "cv_mean": lr_cv.mean(),
                "cv_std": lr_cv.std(),
            },
            feature_names=CLASSIFICATION_FEATURES,
            additional_data={
                "confusion_matrix": confusion_matrix(y_test, lr_preds),
                "report": classification_report(y_test, lr_preds, output_dict=True),
            }
        )

        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=self.random_state, max_depth=5)
        rf.fit(X_train, y_train)
        rf_preds = rf.predict(X_test)
        rf_cv = cross_val_score(rf, X, y, cv=5, scoring="accuracy")
        
        importances = pd.Series(rf.feature_importances_, index=CLASSIFICATION_FEATURES).sort_values(ascending=False)

        results["random_forest"] = ModelResult(
            model=rf,
            predictions=rf_preds,
            metrics={
                "accuracy": accuracy_score(y_test, rf_preds),
                "precision": precision_score(y_test, rf_preds, zero_division=0),
                "recall": recall_score(y_test, rf_preds, zero_division=0),
                "f1": f1_score(y_test, rf_preds, zero_division=0),
                "cv_mean": rf_cv.mean(),
                "cv_std": rf_cv.std(),
            },
            feature_names=CLASSIFICATION_FEATURES,
            additional_data={
                "confusion_matrix": confusion_matrix(y_test, rf_preds),
                "report": classification_report(y_test, rf_preds, output_dict=True),
                "feature_importances": importances,
            }
        )

        return results

    def train_regression(self, df: pd.DataFrame) -> ModelResult:
        """Trains a Linear Regression model to predict the absolute score percentage."""
        df = self.engineer_features(df)
        X = df[BASE_FEATURES].fillna(0)
        y = df["score_percentage"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=self.random_state
        )

        model = LinearRegression()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        return ModelResult(
            model=model,
            predictions=preds,
            metrics={
                "mae": mean_absolute_error(y_test, preds),
                "mse": mean_squared_error(y_test, preds),
                "rmse": np.sqrt(mean_squared_error(y_test, preds)),
                "r2": r2_score(y_test, preds),
            },
            feature_names=BASE_FEATURES,
            additional_data={
                "intercept": model.intercept_,
                "coefficients": pd.Series(model.coef_, index=BASE_FEATURES),
                "y_test": y_test
            }
        )

    def train_clustering(self, df: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """Segments learners based on performance and time utilization using K-Means."""
        df = df.copy()
        cluster_features = ["score_percentage", "time_taken_seconds"]
        X = df[cluster_features].fillna(0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
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

        # Assign semantic labels based on score performance
        segment_labels = ["High Performers", "Average Learners", "Needs Support"]
        cluster_names = {idx: segment_labels[min(rank, 2)] for rank, idx in enumerate(cluster_summary.index)}
        
        cluster_summary["segment"] = cluster_summary.index.map(cluster_names)
        df["segment"] = df["cluster"].map(cluster_names)

        sil_score = silhouette_score(X_scaled, labels) if n_clusters > 1 else 0.0

        return {
            "model": kmeans,
            "labels": labels,
            "df_clustered": df,
            "cluster_summary": cluster_summary,
            "metrics": {
                "silhouette_score": sil_score,
                "inertia": kmeans.inertia_,
            },
            "feature_names": cluster_features,
        }
