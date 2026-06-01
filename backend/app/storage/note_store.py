from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.models.request_models import QuestionScope


class NoteStore:
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
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repository_key TEXT NOT NULL,
                    path TEXT,
                    scope TEXT NOT NULL DEFAULT 'FILE',
                    team_name TEXT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    question TEXT NOT NULL,
                    resolved INTEGER NOT NULL DEFAULT 0,
                    resolved_at TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(questions)").fetchall()}
            if "scope" not in columns:
                connection.execute("ALTER TABLE questions ADD COLUMN scope TEXT NOT NULL DEFAULT 'FILE'")
            if "team_name" not in columns:
                connection.execute("ALTER TABLE questions ADD COLUMN team_name TEXT")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (question_id) REFERENCES questions (id)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_questions_repo_path ON questions(repository_key, path)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_questions_repo_scope ON questions(repository_key, scope)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_replies_question_id ON replies(question_id)"
            )
            connection.commit()

    def create_question(
        self,
        repository_key: str,
        path: str | None,
        scope: str,
        team_name: str | None,
        user_id: int,
        username: str,
        question: str,
        created_at: str,
    ) -> Dict[str, Any]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO questions (repository_key, path, scope, team_name, user_id, username, question, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (repository_key, path, scope, team_name, user_id, username, question, created_at),
            )
            connection.commit()
            question_id = int(cursor.lastrowid)
        question = self.get_question(question_id)
        return question or {}

    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, repository_key, path, scope, team_name, user_id, username, question, resolved, resolved_at, created_at
                FROM questions
                WHERE id = ?
                """,
                (question_id,),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["resolved"] = bool(payload["resolved"])
        return payload

    def list_questions(
        self,
        repository_key: str,
        path: str | None = None,
        scope: str = QuestionScope.ALL,
        team_name: str | None = None,
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT id, repository_key, path, scope, team_name, user_id, username, question, resolved, resolved_at, created_at
            FROM questions
            WHERE repository_key = ?
        """
        params: list[Any] = [repository_key]
        if scope == QuestionScope.FILE:
            query += " AND scope = ?"
            params.append(QuestionScope.FILE)
            if path is not None:
                query += " AND path = ?"
                params.append(path)
        elif scope == QuestionScope.REPOSITORY:
            query += " AND scope = ?"
            params.append(QuestionScope.REPOSITORY)
        elif path is not None:
            query += " AND (scope = ? OR (scope = ? AND path = ?))"
            params.extend([QuestionScope.REPOSITORY, QuestionScope.FILE, path])
        if team_name is not None:
            query += " AND team_name = ?"
            params.append(team_name)
        query += " ORDER BY created_at DESC, id DESC"
        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()
        questions: List[Dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["resolved"] = bool(payload["resolved"])
            questions.append(payload)
        return questions

    def set_question_resolved(self, question_id: int, resolved: bool, resolved_at: str | None) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            connection.execute(
                "UPDATE questions SET resolved = ?, resolved_at = ? WHERE id = ?",
                (1 if resolved else 0, resolved_at, question_id),
            )
            connection.commit()
        return self.get_question(question_id)

    def create_reply(
        self,
        question_id: int,
        user_id: int,
        username: str,
        content: str,
        created_at: str,
    ) -> Dict[str, Any]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO replies (question_id, user_id, username, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (question_id, user_id, username, content, created_at),
            )
            connection.commit()
            reply_id = int(cursor.lastrowid)
            row = connection.execute(
                """
                SELECT id, question_id, user_id, username, content, created_at
                FROM replies
                WHERE id = ?
                """,
                (reply_id,),
            ).fetchone()
        return dict(row) if row else {}

    def list_replies(self, question_id: int) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, question_id, user_id, username, content, created_at
                FROM replies
                WHERE question_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (question_id,),
            ).fetchall()
        return [dict(row) for row in rows]
