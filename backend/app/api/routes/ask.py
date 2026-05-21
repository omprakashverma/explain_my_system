from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.dependencies import require_current_user
from backend.app.agents.qa_agent import qa_agent
from backend.app.models.request_models import AskRequest, PromptTemplateRunRequest, QuestionScope
from backend.app.models.response_models import (
    AskResponse,
    PromptTemplateListResponse,
    PromptTemplateRunResponse,
    RepoSummaryResponse,
)
from backend.app.services.ai_service import ai_service
from backend.app.services.prompt_template_service import prompt_template_service
from backend.app.storage.repository_store import repository_store
from backend.app.utils.text_utils import ensure_file_exists

router = APIRouter(dependencies=[Depends(require_current_user)])


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
    scope = (req.scope or QuestionScope.FILE).upper()
    if scope not in {QuestionScope.FILE, QuestionScope.REPOSITORY}:
        raise HTTPException(400, "Unsupported scope value.")
    selected_file = req.selected_file
    if scope == QuestionScope.FILE:
        if not selected_file:
            raise HTTPException(400, "Select a file or switch to repository scope before asking.")
        selected_file = ensure_file_exists(repository_store.files, selected_file)
    else:
        selected_file = None
    answer = qa_agent.answer(repository_store, req.prompt, selected_file, scope)
    found = 1 if scope == QuestionScope.FILE and selected_file else len(repository_store.retrieve_similar(req.prompt))
    return {
        "answer": answer,
        "found": found,
        "selected_file": selected_file,
    }


@router.get("/prompt-templates", response_model=PromptTemplateListResponse)
async def list_prompt_templates() -> dict[str, object]:
    return {"templates": prompt_template_service.list_templates()}


@router.post("/prompt-templates/run", response_model=PromptTemplateRunResponse)
async def run_prompt_template(req: PromptTemplateRunRequest) -> dict[str, object]:
    return prompt_template_service.run_template(req.template_id)
