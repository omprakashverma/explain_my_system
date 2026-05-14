from backend.app.storage.repository_store import repository_store


class NoteService:
    def add_question(self, path: str, username: str, question: str) -> dict[str, object]:
        return repository_store.add_file_question(path, username, question)


note_service = NoteService()
