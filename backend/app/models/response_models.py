from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FileListResponse(BaseModel):
    files: List[str]


class FilesFullResponse(BaseModel):
    files: List[str]
    contents: Dict[str, str]


class FileResponse(BaseModel):
    path: str
    text: str
    chunks: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]


class SummaryResponse(BaseModel):
    status: str
    overview: str
    file_count: int
    language_count: int
    endpoint_count: int
    source_type: Optional[str]
    source_label: Optional[str]
    loaded_at: Optional[str]
    top_modules: List[str]
    top_files: List[str]
    frameworks_detected: List[str]


class StoreRepositoryResponse(BaseModel):
    files: int
    chunks: int
    source_type: str
    source_label: str


class RepoSummaryResponse(BaseModel):
    summary: str


class TagQuestionResponse(BaseModel):
    success: bool
    file: str
    total_tags: int


class AskResponse(BaseModel):
    answer: str
    found: int
    selected_file: Optional[str]


class ClearResponse(BaseModel):
    cleared: bool
