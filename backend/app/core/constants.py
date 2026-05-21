from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
SAMPLE_DIR = BASE_DIR / "sample"

SUPPORTED_CODE_SUFFIXES = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".sh",
}
IGNORED_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pdm.lock",
    "cargo.lock",
    "composer.lock",
}
IGNORED_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
    ".next",
    ".nuxt",
    "target",
    "out",
    "bin",
    "obj",
    ".idea",
    ".vscode",
}
MAX_FILE_CHARS = 200_000

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
