import pytest

import auth_rules


def test_a_session_is_active_until_it_expires() -> None:
    session = {"expires_at": 100.0}

    assert auth_rules.session_is_active(session, now=99.0)
    assert not auth_rules.session_is_active(session, now=100.0)


def test_a_session_saved_without_an_expiry_has_expired() -> None:
    assert not auth_rules.session_is_active({"username": "old"}, now=1.0)


@pytest.mark.parametrize(
    ("failures", "seconds_since", "locked"),
    [
        (auth_rules.MAX_FAILED_LOGINS - 1, 0, False),
        (auth_rules.MAX_FAILED_LOGINS, 0, True),
        (auth_rules.MAX_FAILED_LOGINS, auth_rules.LOCKOUT_SECONDS - 1, True),
        (auth_rules.MAX_FAILED_LOGINS, auth_rules.LOCKOUT_SECONDS, False),
    ],
)
def test_lockout(failures: int, seconds_since: int, locked: bool) -> None:
    assert auth_rules.is_locked_out(failures, 0.0, float(seconds_since)) is locked
