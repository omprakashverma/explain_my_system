from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class ReplyResponse(BaseModel):
    id: int
    question_id: int
    user_id: int
    username: str
    content: str
    created_at: str


class QuestionResponse(BaseModel):
    id: int
    path: Optional[str]
    scope: str
    team_name: Optional[str]
    user_id: int
    username: str
    question: str
    resolved: bool
    resolved_at: Optional[str]
    created_at: str
    reply_count: int
    latest_reply_at: Optional[str]
    replies: List[ReplyResponse]


class FileListResponse(BaseModel):
    files: List[str]


class FilesFullResponse(BaseModel):
    files: List[str]
    contents: Dict[str, str]


class FileResponse(BaseModel):
    path: str
    text: str
    chunks: List[Dict[str, Any]]
    questions: List[QuestionResponse]


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
    file: Optional[str]
    total_tags: int
    question: QuestionResponse


class ReplyMutationResponse(BaseModel):
    success: bool
    reply: ReplyResponse
    reply_count: int


class RepliesResponse(BaseModel):
    replies: List[ReplyResponse]


class QuestionMutationResponse(BaseModel):
    success: bool
    question: QuestionResponse


class QuestionsListResponse(BaseModel):
    questions: List[QuestionResponse]


class PromptTemplateResponse(BaseModel):
    id: str
    title: str
    category: str
    description: str
    prompt_template: str
    output_format: str
    scope: str


class PromptTemplateListResponse(BaseModel):
    templates: List[PromptTemplateResponse]


class HistoricalAnswerSource(BaseModel):
    question_id: int
    question: str
    username: str
    created_at: str
    replies: List[Dict[str, Any]]
    scope: str


class AskResponse(BaseModel):
    answer: str
    found: int
    selected_file: Optional[str]
    answer_source: str = "llm"  # "llm" or "history"
    source_question_id: Optional[int] = None
    related_questions: List[HistoricalAnswerSource] = []


class PromptTemplateRunResponse(AskResponse):
    template: PromptTemplateResponse
    scope: str


class ClearResponse(BaseModel):
    cleared: bool
