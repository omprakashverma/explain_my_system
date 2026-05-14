from fastapi import APIRouter, HTTPException

from backend.app.agents.qa_agent import qa_agent
from backend.app.models.request_models import AskRequest
from backend.app.models.response_models import AskResponse, RepoSummaryResponse
from backend.app.services.ai_service import ai_service
from backend.app.storage.repository_store import repository_store

router = APIRouter()


@router.get("/repo-summary", response_model=RepoSummaryResponse)
async def repo_summary() -> dict[str, str]:
    context = "\n".join([f"{path}\n{text[:1000]}" for path, text in list(repository_store.files.items())[:5]])
    answer = ai_service.call_llm(
        [
            {
                "role": "system",
                "content": "You are a senior software architect. Explain the codebase in plain English in a concise summary.",
            },
            {
                "role": "user",
                "content": context if context else "No repository loaded.",
            },
        ]
    )
    return {"summary": answer}


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> dict[str, object]:
    if not repository_store.files:
        raise HTTPException(400, "Load a repository before asking questions.")
    if not req.prompt.strip():
        raise HTTPException(400, "Prompt cannot be empty.")
    answer = qa_agent.answer(repository_store, req.prompt, req.selected_file)
    return {
        "answer": answer,
        "found": 1 if req.selected_file else len(repository_store.retrieve_similar(req.prompt)),
        "selected_file": req.selected_file,
    }
