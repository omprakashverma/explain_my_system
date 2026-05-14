from fastapi import APIRouter, Query

from backend.app.models.response_models import FileResponse
from backend.app.services.file_service import file_service

router = APIRouter()


@router.get("/file", response_model=FileResponse)
async def get_file(path: str = Query(...)) -> dict[str, object]:
    return file_service.get_file(path)
