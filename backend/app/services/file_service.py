from backend.app.storage.repository_store import repository_store
from backend.app.utils.text_utils import ensure_file_exists, normalize_path


class FileService:
    def get_file(self, path: str) -> dict[str, object]:
        normalized = ensure_file_exists(repository_store.files, path)
        related_chunks = [
            chunk for chunk in repository_store.chunks if normalize_path(chunk["path"]) == normalized
        ]
        return {
            "path": normalized,
            "text": repository_store.files[normalized],
            "chunks": related_chunks[:5],
            "questions": repository_store.get_file_questions(normalized),
        }


file_service = FileService()
