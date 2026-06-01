from __future__ import annotations

from typing import Any, Dict, List

from fastapi import HTTPException, status

from backend.app.core.config import get_settings
from backend.app.core.security import utc_iso
from backend.app.models.request_models import QuestionScope
from backend.app.storage.note_store import NoteStore


class NoteService:
    def __init__(self) -> None:
        self.store = NoteStore(get_settings().auth_db_path)

    def _validate_question_text(self, question: str) -> str:
        value = question.strip()
        if not value:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Question cannot be empty.")
        if len(value) > 1200:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Question must be 1200 characters or fewer.")
        return value

    def _validate_reply_text(self, content: str) -> str:
        value = content.strip()
        if not value:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reply cannot be empty.")
        if len(value) > 1200:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reply must be 1200 characters or fewer.")
        return value

    def _hydrate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        replies = self.store.list_replies(int(question["id"]))
        return {
            "id": int(question["id"]),
            "path": str(question["path"]) if question.get("path") else None,
            "scope": str(question.get("scope") or QuestionScope.FILE),
            "team_name": str(question["team_name"]) if question.get("team_name") else None,
            "user_id": int(question["user_id"]),
            "username": str(question["username"]),
            "question": str(question["question"]),
            "resolved": bool(question["resolved"]),
            "resolved_at": question.get("resolved_at"),
            "created_at": str(question["created_at"]),
            "reply_count": len(replies),
            "latest_reply_at": replies[-1]["created_at"] if replies else None,
            "replies": replies,
        }

    def list_questions(
        self,
        repository_key: str,
        path: str | None = None,
        scope: str = QuestionScope.ALL,
        team_name: str | None = None,
    ) -> List[Dict[str, Any]]:
        normalized_scope = self._validate_scope(scope)
        questions = self.store.list_questions(repository_key, path, normalized_scope, self._normalize_team_name(team_name))
        return [self._hydrate_question(question) for question in questions]

    def add_question(
        self,
        repository_key: str,
        path: str | None,
        scope: str,
        current_user: Dict[str, Any],
        question: str,
        team_name: str | None = None,
    ) -> Dict[str, Any]:
        normalized_scope = self._validate_scope(scope, allow_all=False)
        normalized_path = path if normalized_scope == QuestionScope.FILE else ""
        if normalized_scope == QuestionScope.FILE and not normalized_path:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A file question requires a selected file.")
        normalized_team_name = self._normalize_team_name(team_name)
        saved_question = self.store.create_question(
            repository_key=repository_key,
            path=normalized_path,
            scope=normalized_scope,
            team_name=normalized_team_name,
            user_id=int(current_user["id"]),
            username=str(current_user["username"]),
            question=self._validate_question_text(question),
            created_at=utc_iso(),
        )
        return {
            "success": True,
            "file": normalized_path,
            "total_tags": len(
                self.store.list_questions(repository_key, normalized_path, normalized_scope, normalized_team_name)
            ),
            "question": self._hydrate_question(saved_question),
        }

    def _normalize_team_name(self, team_name: str | None) -> str | None:
        if team_name is None:
            return None
        value = team_name.strip()
        if not value:
            return None
        if len(value) > 120:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Team name must be 120 characters or fewer.")
        return value

    def _validate_scope(self, scope: str, allow_all: bool = True) -> str:
        normalized = (scope or "").upper()
        allowed_scopes = {QuestionScope.FILE, QuestionScope.REPOSITORY}
        if allow_all:
            allowed_scopes.add(QuestionScope.ALL)
        if normalized not in allowed_scopes:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported scope value.")
        return normalized

    def list_replies(self, question_id: int) -> List[Dict[str, Any]]:
        question = self.store.get_question(question_id)
        if not question:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")
        return self.store.list_replies(question_id)

    def add_reply(self, question_id: int, current_user: Dict[str, Any], content: str) -> Dict[str, Any]:
        question = self.store.get_question(question_id)
        if not question:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")
        reply = self.store.create_reply(
            question_id=question_id,
            user_id=int(current_user["id"]),
            username=str(current_user["username"]),
            content=self._validate_reply_text(content),
            created_at=utc_iso(),
        )
        return {
            "success": True,
            "reply": reply,
            "reply_count": len(self.store.list_replies(question_id)),
        }

    def set_resolved(self, question_id: int, current_user: Dict[str, Any], resolved: bool) -> Dict[str, Any]:
        question = self.store.get_question(question_id)
        if not question:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")

        is_creator = int(question["user_id"]) == int(current_user["id"])
        is_admin = str(current_user["role"]) == "admin"
        if not is_creator and not is_admin:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Only the question author or an admin can change the resolution status.",
            )

        updated_question = self.store.set_question_resolved(
            question_id,
            resolved,
            utc_iso() if resolved else None,
        )
        if not updated_question:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")
        return {
            "success": True,
            "question": self._hydrate_question(updated_question),
        }


note_service = NoteService()
