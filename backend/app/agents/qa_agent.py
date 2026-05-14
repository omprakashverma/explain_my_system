from backend.app.services.ai_service import ai_service
from backend.app.storage.repository_store import RepositoryStore


class QAAgent:
    def answer(self, store: RepositoryStore, prompt: str, selected_file: str | None) -> str:
        context_text = store.build_file_context(selected_file, prompt)
        return ai_service.call_llm(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a senior software engineer helping explain a specific source file. "
                        "Answer only using the provided file context. "
                        "If the answer cannot be derived from the file, say that clearly. "
                        "Do not give generic repository-wide answers unless no file is selected."
                    ),
                },
                {
                    "role": "user",
                    "content": f"USER PROMPT:\n{prompt}\n\nFILE CONTEXT:\n{context_text if context_text else 'No context available.'}",
                },
            ]
        )


qa_agent = QAAgent()
