from typing import Optional

from pydantic import BaseModel


class FileQuestionTag(BaseModel):
    path: str
    username: str
    question: str


class AskRequest(BaseModel):
    prompt: str
    selected_file: Optional[str] = None
