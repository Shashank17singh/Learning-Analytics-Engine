import passwords


def test_a_password_verifies_against_its_hash() -> None:
    assert passwords.verify_password("secret", passwords.hash_password("secret"))


def test_a_wrong_password_is_rejected() -> None:
    assert not passwords.verify_password("wrong", passwords.hash_password("secret"))


def test_each_hash_is_salted() -> None:
    assert passwords.hash_password("secret") != passwords.hash_password("secret")


def test_existing_accounts_can_still_log_in() -> None:
    stored = passwords.legacy_hash("secret")

    assert passwords.verify_password("secret", stored)
    assert not passwords.verify_password("wrong", stored)


def test_only_legacy_hashes_need_upgrading() -> None:
    assert passwords.needs_upgrade(passwords.legacy_hash("secret"))
    assert not passwords.needs_upgrade(passwords.hash_password("secret"))


def test_damaged_hashes_are_rejected_without_crashing() -> None:
    assert not passwords.verify_password("secret", "scrypt$nothex$alsonothex")
    assert not passwords.verify_password("secret", "scrypt$only-two-parts")
    assert not passwords.verify_password("secret", "")
