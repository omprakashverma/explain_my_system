from typing import Optional

from pydantic import BaseModel


class QuestionScope:
    FILE = "FILE"
    REPOSITORY = "REPOSITORY"
    ALL = "ALL"


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class FileQuestionTag(BaseModel):
    path: Optional[str] = None
    scope: str = QuestionScope.FILE
    team_name: Optional[str] = None
    question: str


class QuestionReplyRequest(BaseModel):
    content: str


class ResolveQuestionRequest(BaseModel):
    resolved: bool


class AskRequest(BaseModel):
    prompt: str
    selected_file: Optional[str] = None
    scope: str = QuestionScope.FILE


class PromptTemplateRunRequest(BaseModel):
    template_id: str
