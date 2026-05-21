from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone


PBKDF2_ITERATIONS = 310_000


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso(value: datetime | None = None) -> str:
    current = value or utc_now()
    return current.isoformat()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        iterations_str, salt_hex, digest_hex = password_hash.split("$", 2)
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
    except (TypeError, ValueError):
        return False

    password_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(password_digest, expected_digest)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry(days: int) -> datetime:
    return utc_now() + timedelta(days=days)
