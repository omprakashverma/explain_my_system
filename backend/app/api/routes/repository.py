from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.app.api.dependencies import require_current_user
from backend.app.core.constants import SAMPLE_DIR
from backend.app.models.response_models import ClearResponse, FileListResponse, FilesFullResponse, StoreRepositoryResponse, SummaryResponse
from backend.app.services.repository_service import repository_service

router = APIRouter(dependencies=[Depends(require_current_user)])


@router.post("/upload-zip", response_model=StoreRepositoryResponse)
async def upload_zip(file: UploadFile = File(...)) -> dict[str, object]:
    data = await file.read()
    return repository_service.load_zip(data, file.filename or "Uploaded ZIP")


@router.post("/load-git", response_model=StoreRepositoryResponse)
async def load_git(url: str) -> dict[str, object]:
    return repository_service.load_git(url)


@router.post("/load-sample", response_model=StoreRepositoryResponse)
async def load_sample() -> dict[str, object]:
    if not SAMPLE_DIR.exists():
        raise HTTPException(404, "Sample directory not found.")
    return repository_service.load_sample()


@router.get("/files", response_model=FileListResponse)
async def list_files() -> dict[str, list[str]]:
    return {"files": repository_service.list_files()}


@router.get("/files-full", response_model=FilesFullResponse)
async def files_full() -> dict[str, object]:
    return repository_service.get_files_full()


@router.get("/summary", response_model=SummaryResponse)
async def summary() -> dict[str, object]:
    return repository_service.get_summary()


@router.post("/clear", response_model=ClearResponse)
async def clear_store() -> dict[str, bool]:
    return repository_service.clear()
