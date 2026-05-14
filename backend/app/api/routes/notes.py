from fastapi import APIRouter

from backend.app.models.request_models import FileQuestionTag
from backend.app.models.response_models import TagQuestionResponse
from backend.app.services.note_service import note_service

router = APIRouter()


@router.post("/tag-question", response_model=TagQuestionResponse)
async def tag_question(req: FileQuestionTag) -> dict[str, object]:
    return note_service.add_question(req.path, req.username, req.question)
