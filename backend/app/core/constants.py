from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
SAMPLE_DIR = BASE_DIR / "sample"

SUPPORTED_CODE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx"}
IGNORED_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}

DEFAULT_SUMMARY_STATE = {
    "status": "empty",
    "overview": "No repository loaded yet.",
    "file_count": 0,
    "language_count": 0,
    "endpoint_count": 0,
    "source_type": None,
    "source_label": None,
    "loaded_at": None,
    "top_modules": [],
    "top_files": [],
    "frameworks_detected": [],
}
