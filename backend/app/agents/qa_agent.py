from backend.app.models.request_models import QuestionScope
from backend.app.services.ai_service import ai_service
from backend.app.storage.repository_store import RepositoryStore


class QAAgent:
    def answer(self, store: RepositoryStore, prompt: str, selected_file: str | None, scope: str) -> str:
        normalized_scope = scope.upper()
        if normalized_scope == QuestionScope.REPOSITORY:
            context_text = store.build_repository_context(prompt)
            system_prompt = (
                "You are a senior software architect helping explain an entire repository. "
                "Use the repository summary, tree, and relevant code snippets to reason across files. "
                "Mention uncertainty when the provided context is insufficient."
            )
        else:
            context_text = store.build_file_context(selected_file, prompt)
            system_prompt = (
                "You are a senior software engineer helping explain a specific source file. "
                "Answer only using the provided file context. "
                "If the answer cannot be derived from the file, say that clearly. "
                "Do not give generic repository-wide answers unless no file is selected."
            )
        return ai_service.call_llm(
            [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"QUESTION SCOPE: {normalized_scope}\n"
                        f"USER PROMPT:\n{prompt}\n\n"
                        f"CONTEXT:\n{context_text if context_text else 'No context available.'}"
                    ),
                },
            ]
        )


qa_agent = QAAgent()
