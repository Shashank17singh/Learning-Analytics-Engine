import pytest

import llm_utils


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give every test a placeholder key, and fail any call that would reach a provider."""

    def no_network(*_, **__):
        pytest.fail("A test tried to call an LLM provider.")

    monkeypatch.setattr(llm_utils.st, "secrets", {})
    monkeypatch.setenv("GEMINI_API_KEY", "placeholder")
    monkeypatch.setattr(llm_utils, "_ask_provider", no_network)


def test_fenced_json_questions_are_parsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        llm_utils, "_ask_provider", lambda *_, **__: '```json\n[{"qno": 1}]\n```'
    )

    assert llm_utils.generate_gemini_questions("Topic") == [{"qno": 1}]


def test_round_instructions_replace_the_default_format(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts = []

    def fake_ask(provider, api_key, prompt, temperature):
        prompts.append(prompt)
        return "[]"

    monkeypatch.setattr(llm_utils, "_ask_provider", fake_ask)

    llm_utils.generate_gemini_questions("Topic", round_instructions="ONLY CODING")

    assert "ONLY CODING" in prompts[0]
    assert '"coding"' in prompts[0]
    assert 'ONLY "single_mcq"' not in prompts[0]


def test_a_written_answer_is_graded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        llm_utils,
        "_ask_provider",
        lambda *_, **__: '{"score": 80, "feedback": "Good"}',
    )

    grade = llm_utils.grade_written_answer("Q", "A", "R", "coding", "Python")

    assert grade["score"] == 80.0


@pytest.mark.parametrize("reply", ["not json", "[]", '{"feedback": "no score"}'])
def test_a_bad_grading_reply_gives_no_grade(
    monkeypatch: pytest.MonkeyPatch, reply: str
) -> None:
    monkeypatch.setattr(llm_utils, "_ask_provider", lambda *_, **__: reply)

    assert llm_utils.grade_written_answer("Q", "A", "R", "written") is None


def test_a_provider_failure_gives_no_grade(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*_, **__):
        raise RuntimeError("503 overloaded")

    monkeypatch.setattr(llm_utils, "_ask_provider", fail)

    assert llm_utils.grade_written_answer("Q", "A", "R", "written") is None


def test_grading_without_a_key_gives_no_grade(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY")

    assert llm_utils.grade_written_answer("Q", "A", "R", "written") is None
