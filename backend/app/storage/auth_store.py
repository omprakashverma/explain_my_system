from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class AuthStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    email TEXT,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_nocase ON users(username COLLATE NOCASE)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
                """
            )
            connection.commit()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, username, email, password_hash, role, created_at FROM users WHERE username = ? COLLATE NOCASE",
                (username,),
            ).fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, username, email, password_hash, role, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return dict(row) if row else None

    def create_user(
        self,
        username: str,
        email: str | None,
        password_hash: str,
        role: str,
        created_at: str,
    ) -> Dict[str, Any]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, role, created_at),
            )
            connection.commit()
            user_id = int(cursor.lastrowid)
        return self.get_user_by_id(user_id) or {}

    def create_session(self, user_id: int, token_hash: str, created_at: str, expires_at: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (user_id, token_hash, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, token_hash, created_at, expires_at),
            )
            connection.commit()

    def delete_session(self, token_hash: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
            connection.commit()

    def delete_expired_sessions(self, current_time: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (current_time,))
            connection.commit()

    def get_user_by_session_token(self, token_hash: str, current_time: str) -> Optional[Dict[str, Any]]:
        self.delete_expired_sessions(current_time)
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT users.id, users.username, users.email, users.password_hash, users.role, users.created_at
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ? AND sessions.expires_at > ?
                """,
                (token_hash, current_time),
            ).fetchone()
        return dict(row) if row else None
