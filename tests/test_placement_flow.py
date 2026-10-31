"""Drives the student portal through a placement round, with the database and LLM stubbed."""

import time
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import db_utils
import llm_utils
import placement

ROOT = Path(__file__).resolve().parent.parent
PORTAL = str(ROOT / "pages" / "Student_Portal.py")
CODING_QUESTION = {
    "qno": 1,
    "type": "coding",
    "ques": "Reverse a string.",
    "options": {},
    "correct": "Use two pointers",
    "explanation": "Handle the empty string",
}
MCQ = {
    "qno": 2,
    "type": "single_mcq",
    "ques": "2 + 2?",
    "options": {"a": "4", "b": "5"},
    "correct": "a",
    "explanation": "Sum",
}


class FakeCursor:
    def __init__(self, inserts: list) -> None:
        self.inserts = inserts

    def execute(self, sql: str, params: tuple = ()) -> None:
        if "INSERT INTO attempts" in sql:
            self.inserts.append(params)

    def fetchone(self) -> None:
        return None

    def fetchall(self) -> list:
        return []

    def close(self) -> None:
        pass


class FakeConnection:
    def __init__(self, inserts: list) -> None:
        self.inserts = inserts

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.inserts)

    def commit(self) -> None:
        pass

    def close(self) -> None:
        pass


@pytest.fixture
def portal(monkeypatch: pytest.MonkeyPatch):
    """Return a function that opens the portal, plus the attempts it saves."""
    inserts: list = []
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(db_utils, "get_db_connection", lambda: FakeConnection(inserts))
    monkeypatch.setattr(db_utils, "init_db", lambda conn: None)
    monkeypatch.setattr(pd, "read_sql_query", lambda *_, **__: pd.DataFrame())

    def open_portal():
        at = AppTest.from_file(PORTAL, default_timeout=60)
        at.session_state["authenticated"] = True
        at.session_state["username"] = "asha"
        at.session_state["user_role"] = "student"
        return at.run()

    return open_portal, inserts


def select_round(at: AppTest, *choices: str) -> AppTest:
    for index, choice in enumerate(choices):
        at.selectbox(key=f"sel_{index}").select(choice).run()
    return at


def start(at: AppTest) -> AppTest:
    next(b for b in at.button if "Start Assessment Now" in b.label).click().run()
    assert not at.exception
    return at


def submit(at: AppTest) -> AppTest:
    next(b for b in at.button if "Finish & Submit" in b.label).click().run()
    assert not at.exception
    return at


def test_a_coding_round_gets_its_format_and_is_graded_with_partial_marks(
    portal, monkeypatch: pytest.MonkeyPatch
) -> None:
    open_portal, inserts = portal
    requested = {}

    def fake_generate(topic, count, difficulty, **kwargs):
        requested.update(topic=topic, count=count, **kwargs)
        return [CODING_QUESTION, MCQ]

    graded = {}

    def fake_grade(question, answer, reference, kind, language=""):
        graded.update(answer=answer, kind=kind, language=language)
        return {
            "score": 75.0,
            "feedback": "Solid.",
            "strengths": ["Clear"],
            "gaps": ["Empty input"],
        }

    monkeypatch.setattr(llm_utils, "generate_gemini_questions", fake_generate)
    monkeypatch.setattr(llm_utils, "grade_written_answer", fake_grade)

    at = open_portal()
    assert not at.exception
    select_round(at, placement.PLACEMENT_DOMAIN, "Coding Round")
    assert any("Coding Round" in info.value for info in at.info)
    assert any("not run" in caption.value for caption in at.caption)

    start(at)
    assert requested["count"] == placement.ROUNDS["Coding Round"].questions
    assert (
        requested["round_instructions"] == placement.ROUNDS["Coding Round"].instructions
    )
    assert at.session_state["time_limit_mins"] == 60

    at.selectbox(key="sq_1_language").select("Java").run()
    at.text_area(key="sq_1").set_value("return s[::-1]").run()
    at.radio(key="sq_2").set_value("a) 4").run()
    submit(at)

    assert graded == {"answer": "return s[::-1]", "kind": "coding", "language": "Java"}
    attempt = inserts[0]
    assert attempt[0] == "asha"
    assert attempt[1:4] == (2, 2, 87.5)  # One right, plus 0.75 of the coding question.
    assert attempt[-3:-1] == (placement.PLACEMENT_DOMAIN, "Coding Round")


def test_an_ungraded_answer_is_left_out_of_the_score(
    portal, monkeypatch: pytest.MonkeyPatch
) -> None:
    open_portal, inserts = portal
    monkeypatch.setattr(
        llm_utils,
        "generate_gemini_questions",
        lambda *_, **__: [CODING_QUESTION, MCQ],
    )
    monkeypatch.setattr(llm_utils, "grade_written_answer", lambda *_: None)

    at = select_round(open_portal(), placement.PLACEMENT_DOMAIN, "Coding Round")
    start(at)
    at.text_area(key="sq_1").set_value("answer").run()
    at.radio(key="sq_2").set_value("a) 4").run()
    submit(at)

    assert inserts[0][1:4] == (1, 1, 100.0)


def test_nothing_is_saved_when_no_answer_could_be_graded(
    portal, monkeypatch: pytest.MonkeyPatch
) -> None:
    open_portal, inserts = portal
    monkeypatch.setattr(
        llm_utils, "generate_gemini_questions", lambda *_, **__: [CODING_QUESTION]
    )
    monkeypatch.setattr(llm_utils, "grade_written_answer", lambda *_: None)

    at = select_round(open_portal(), placement.PLACEMENT_DOMAIN, "Coding Round")
    start(at)
    at.text_area(key="sq_1").set_value("my solution").run()
    submit(at)

    assert inserts == []
    assert any("could not be graded" in error.value for error in at.error)
    assert any(block.value == "my solution" for block in at.code)


def test_running_out_of_time_submits_the_saved_answers_once(
    portal, monkeypatch: pytest.MonkeyPatch
) -> None:
    open_portal, inserts = portal
    monkeypatch.setattr(
        llm_utils, "generate_gemini_questions", lambda *_, **__: [CODING_QUESTION]
    )
    monkeypatch.setattr(
        llm_utils,
        "grade_written_answer",
        lambda *_: {"score": 50.0, "feedback": "", "strengths": [], "gaps": []},
    )

    at = select_round(open_portal(), placement.PLACEMENT_DOMAIN, "Coding Round")
    start(at)
    at.text_area(key="sq_1").set_value("saved answer").run()
    at.session_state["assessment_start_time"] = time.time() - 4 * 3600
    at.run()

    assert not at.exception
    assert len(inserts) == 1
    assert at.session_state["student_assessment_started"] is False
    assert at.session_state["force_submit"] is False


def test_a_typed_custom_topic_reaches_the_generator(
    portal, monkeypatch: pytest.MonkeyPatch
) -> None:
    open_portal, _ = portal
    topics = []

    def fake_generate(topic, *_, **__):
        topics.append(topic)
        return [MCQ]

    monkeypatch.setattr(llm_utils, "generate_gemini_questions", fake_generate)

    at = select_round(open_portal(), "Other / Custom...")
    at.text_input[0].set_value("Compiler Design").run()
    start(at)

    assert topics == ["Compiler Design"]
    assert at.session_state["selected_subject"] == "Compiler Design"


def test_other_domains_keep_their_usual_settings(
    portal, monkeypatch: pytest.MonkeyPatch
) -> None:
    open_portal, _ = portal
    requested = {}

    def fake_generate(topic, count, difficulty, **kwargs):
        requested.update(kwargs)
        return [MCQ]

    monkeypatch.setattr(llm_utils, "generate_gemini_questions", fake_generate)

    at = select_round(
        open_portal(),
        "Computer Science & Information Technology (IT)",
        "Software Development",
    )
    start(at)

    assert requested["round_instructions"] is None
    assert at.session_state["time_limit_mins"] is None
