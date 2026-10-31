import numpy as np
import pandas as pd
import pytest

from ml_models import CLASSIFICATION_FEATURES, AssessmentAnalyticsModel


@pytest.fixture
def attempts() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for index in range(60):
        score = int(rng.integers(0, 11))
        rows.append(
            {
                "student_name": f"student{index % 6}",
                "attempt_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=index),
                "score": score,
                "total_questions": 10,
                "score_percentage": score * 10.0,
                "time_taken_seconds": int(rng.integers(60, 600)),
                "passed": score >= 5,
            }
        )
    return pd.DataFrame(rows)


def test_speed_is_score_per_second() -> None:
    frame = pd.DataFrame(
        {
            "student_name": ["a"],
            "attempt_date": ["2026-01-01"],
            "score": [10],
            "score_percentage": [100.0],
            "time_taken_seconds": [5],
        }
    )

    assert AssessmentAnalyticsModel().engineer_features(frame)["speed"].iloc[0] == 2


def test_zero_seconds_does_not_divide_by_zero() -> None:
    frame = pd.DataFrame(
        {
            "student_name": ["a"],
            "attempt_date": ["2026-01-01"],
            "score": [4],
            "score_percentage": [40.0],
            "time_taken_seconds": [0],
        }
    )

    assert AssessmentAnalyticsModel().engineer_features(frame)["speed"].iloc[0] == 4


def test_attempts_are_numbered_per_student_with_their_improvement() -> None:
    frame = pd.DataFrame(
        {
            "student_name": ["a", "a", "b"],
            "attempt_date": ["2026-01-02", "2026-01-01", "2026-01-01"],
            "score": [8, 5, 1],
            "score_percentage": [80.0, 50.0, 10.0],
            "time_taken_seconds": [10, 10, 10],
        }
    )

    result = AssessmentAnalyticsModel().engineer_features(frame)
    student_a = result[result.student_name == "a"]

    assert student_a["attempt_number"].tolist() == [1, 2]
    assert student_a["score_improvement"].tolist() == [0.0, 30.0]


def test_the_input_frame_is_not_modified(attempts: pd.DataFrame) -> None:
    columns = list(attempts.columns)

    AssessmentAnalyticsModel().engineer_features(attempts)

    assert list(attempts.columns) == columns


def test_classifiers_report_metrics_in_range(attempts: pd.DataFrame) -> None:
    results = AssessmentAnalyticsModel().train_classifiers(attempts)

    logistic = results["logistic_regression"]
    assert logistic.feature_names == CLASSIFICATION_FEATURES
    assert 0 <= logistic.metrics["accuracy"] <= 1


def test_classifiers_need_both_outcomes(attempts: pd.DataFrame) -> None:
    attempts["passed"] = True

    assert AssessmentAnalyticsModel().train_classifiers(attempts) == {}
