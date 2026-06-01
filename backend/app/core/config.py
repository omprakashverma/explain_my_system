from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

from backend.app.core.constants import BASE_DIR

load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    app_title: str = "CodeAtlas"
    llm_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    llm_api_key: str = "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"
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    auth_db_path: str = str(BASE_DIR / "backend" / "app" / "storage" / "auth.db")
    auth_session_days: int = 7


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    import os

    return Settings(
        llm_api_url=os.getenv("LLM_API_URL", Settings().llm_api_url),
        llm_api_key=os.getenv("LLM_API_KEY", Settings().llm_api_key).strip(),
        llm_model=os.getenv("LLM_MODEL", Settings().llm_model),
        auth_db_path=os.getenv("AUTH_DB_PATH", Settings().auth_db_path),
        auth_session_days=int(os.getenv("AUTH_SESSION_DAYS", str(Settings().auth_session_days))),
    )
