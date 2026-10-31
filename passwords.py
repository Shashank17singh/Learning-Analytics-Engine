"""
Password hashing. Accounts created before salted hashes were introduced keep working
and are upgraded the next time they log in.
"""

import hashlib
import hmac
import os

_SCHEME = "scrypt"
_COST = {"n": 2**14, "r": 8, "p": 1}


def legacy_hash(password: str) -> str:
    """The unsalted SHA-256 hash used by older accounts."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _scrypt(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, **_COST)


def hash_password(password: str) -> str:
    """Return a salted scrypt hash in the form scrypt$salt$digest."""
    salt = os.urandom(16)
    return f"{_SCHEME}${salt.hex()}${_scrypt(password, salt).hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against a stored hash of either format."""
    if not stored:
        return False
    if not stored.startswith(f"{_SCHEME}$"):
        return hmac.compare_digest(legacy_hash(password), stored)
    try:
        _, salt, digest = stored.split("$")
        expected = bytes.fromhex(digest)
        return hmac.compare_digest(_scrypt(password, bytes.fromhex(salt)), expected)
    except ValueError:
        return False


def needs_upgrade(stored: str) -> bool:
    """Return True if a stored hash should be replaced at the next login."""
    return not stored.startswith(f"{_SCHEME}$")
