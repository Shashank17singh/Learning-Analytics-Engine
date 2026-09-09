import hashlib
import os


def hash_password(password):
    """Securely hash passwords for storage using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_default_admin_password():
    """Get the default admin password from environment variable, or fallback to 'admin123'."""
    return os.environ.get("ADMIN_PASSWORD", "admin123")
