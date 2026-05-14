from backend.app.storage.repository_store import RepositoryStore


class DocumentationAgent:
    def generate_outline(self, store: RepositoryStore) -> dict[str, object]:
        return {
            "status": "not_implemented",
            "message": "Documentation agent placeholder for future docs generation and collaboration workflows.",
            "source_label": store.repository_meta.get("source_label"),
        }
