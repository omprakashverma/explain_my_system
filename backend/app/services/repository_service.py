from backend.app.core.constants import SAMPLE_DIR
from backend.app.storage.repository_store import repository_store
from backend.app.utils.file_utils import read_code_files_from_directory, read_code_files_from_zip
from backend.app.utils.git_utils import clone_repository


class RepositoryService:
    def load_zip(self, data: bytes, filename: str) -> dict[str, object]:
        files = read_code_files_from_zip(data)
        return repository_store.store_repository_files(files, "zip", filename)

    def load_git(self, url: str) -> dict[str, object]:
        files = clone_repository(url)
        return repository_store.store_repository_files(files, "git", url)

    def load_sample(self) -> dict[str, object]:
        files = read_code_files_from_directory(SAMPLE_DIR)
        return repository_store.store_repository_files(files, "sample", "Bundled sample repository")

    def clear(self) -> dict[str, bool]:
        return repository_store.clear()

    def list_files(self) -> list[str]:
        return list(repository_store.files.keys())

    def get_files_full(self) -> dict[str, object]:
        return {
            "files": list(repository_store.files.keys()),
            "contents": repository_store.files,
        }

    def get_summary(self) -> dict[str, object]:
        return repository_store.get_summary_payload()


repository_service = RepositoryService()
