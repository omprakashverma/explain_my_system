from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException, status

from backend.app.core.config import get_settings
from backend.app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expiry,
    utc_iso,
    verify_password,
)
from backend.app.storage.auth_store import AuthStore


class AuthService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.store = AuthStore(self.settings.auth_db_path)
        self.ensure_admin_user()

    def ensure_admin_user(self) -> None:
        existing_admin = self.store.get_user_by_username("admin")
        if existing_admin:
            return
        self.store.create_user(
            username="admin",
            email=None,
            password_hash=hash_password("admin123"),
            role="admin",
            created_at=utc_iso(),
        )

    def _validate_username(self, username: str) -> str:
        normalized = username.strip()
        if len(normalized) < 3:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username must be at least 3 characters long.")
        return normalized

    def _validate_password(self, password: str) -> str:
        if len(password) < 6:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password must be at least 6 characters long.")
        return password

    def _validate_email(self, email: str | None) -> str | None:
        if email is None:
            return None
        normalized = email.strip()
        if not normalized:
            return None
        if "@" not in normalized:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email must be a valid address.")
        return normalized

    def _public_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email"),
            "role": user["role"],
            "created_at": user["created_at"],
        }

    def _create_session_payload(self, user: Dict[str, Any]) -> Dict[str, Any]:
        token = generate_session_token()
        created_at = utc_iso()
        expires_at = utc_iso(session_expiry(self.settings.auth_session_days))
        self.store.create_session(user["id"], hash_session_token(token), created_at, expires_at)
        return {
            "token": token,
            "user": self._public_user(user),
        }

    def register(self, username: str, password: str, email: str | None = None) -> Dict[str, Any]:
        normalized_username = self._validate_username(username)
        normalized_email = self._validate_email(email)
        validated_password = self._validate_password(password)

        if self.store.get_user_by_username(normalized_username):
            raise HTTPException(status.HTTP_409_CONFLICT, "That username is already taken.")

        user = self.store.create_user(
            username=normalized_username,
            email=normalized_email,
            password_hash=hash_password(validated_password),
            role="user",
            created_at=utc_iso(),
        )
        return self._create_session_payload(user)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        normalized_username = username.strip()
        user = self.store.get_user_by_username(normalized_username)
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password.")
        return self._create_session_payload(user)

    def logout(self, token: str) -> None:
        self.store.delete_session(hash_session_token(token))

    def get_current_user(self, token: str) -> Dict[str, Any]:
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication is required.")
        user = self.store.get_user_by_session_token(hash_session_token(token), utc_iso())
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Your session is invalid or has expired.")
        return self._public_user(user)


auth_service = AuthService()
