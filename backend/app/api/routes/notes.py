from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import require_current_user
from backend.app.models.request_models import FileQuestionTag, QuestionReplyRequest, QuestionScope, ResolveQuestionRequest
from backend.app.models.response_models import (
    QuestionMutationResponse,
    QuestionsListResponse,
    RepliesResponse,
    ReplyMutationResponse,
    TagQuestionResponse,
)
from backend.app.services.note_service import note_service
from backend.app.storage.repository_store import repository_store
from backend.app.utils.text_utils import ensure_file_exists

router = APIRouter()


@router.get("/questions", response_model=QuestionsListResponse)
async def list_questions(
    path: str | None = Query(default=None),
    scope: str = Query(default=QuestionScope.ALL),
    current_user: dict[str, object] = Depends(require_current_user),
) -> dict[str, object]:
    del current_user
    return {
        "questions": note_service.list_questions(
            repository_store.get_repository_key(),
            path=path,
            scope=scope,
        )
    }


@router.post("/tag-question", response_model=TagQuestionResponse)
async def tag_question(req: FileQuestionTag, current_user: dict[str, object] = Depends(require_current_user)) -> dict[str, object]:
    normalized_scope = (req.scope or QuestionScope.FILE).upper()
    normalized_path = None
    if normalized_scope == QuestionScope.FILE:
        normalized_path = ensure_file_exists(repository_store.files, req.path)
    return note_service.add_question(
        repository_store.get_repository_key(),
        normalized_path,
        normalized_scope,
        current_user,
        req.question,
    )


@router.get("/questions/{question_id}/replies", response_model=RepliesResponse)
async def get_replies(question_id: int) -> dict[str, object]:
    return {"replies": note_service.list_replies(question_id)}


@router.post("/questions/{question_id}/reply", response_model=ReplyMutationResponse)
async def add_reply(
    question_id: int,
    req: QuestionReplyRequest,
    current_user: dict[str, object] = Depends(require_current_user),
) -> dict[str, object]:
    return note_service.add_reply(question_id, current_user, req.content)


@router.patch("/questions/{question_id}/resolve", response_model=QuestionMutationResponse)
async def resolve_question(
    question_id: int,
    req: ResolveQuestionRequest,
    current_user: dict[str, object] = Depends(require_current_user),
) -> dict[str, object]:
    return note_service.set_resolved(question_id, current_user, req.resolved)
