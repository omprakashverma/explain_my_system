from typing import Protocol

from backend.app.storage.repository_store import RepositoryStore


class RepositoryAgent(Protocol):
    def summarize(self, store: RepositoryStore) -> str:
        ...


class DefaultRepositoryAgent:
    def summarize(self, store: RepositoryStore) -> str:
        summary = store.get_summary_payload()
        return summary.get("overview", "No repository loaded yet.")
