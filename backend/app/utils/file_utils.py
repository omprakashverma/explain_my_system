import io
import zipfile
from pathlib import Path
from typing import Dict

from fastapi import HTTPException

from backend.app.core.constants import SUPPORTED_CODE_SUFFIXES
from backend.app.utils.text_utils import normalize_path, should_skip_path


def read_code_files_from_directory(directory: Path) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue
        relative_path = normalize_path(str(file_path.relative_to(directory)))
        if should_skip_path(relative_path):
            continue
        if file_path.suffix.lower() not in SUPPORTED_CODE_SUFFIXES:
            continue
        try:
            files[relative_path] = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
    return files


def read_code_files_from_zip(data: bytes) -> Dict[str, str]:
    files: Dict[str, str] = {}
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise HTTPException(400, f"Invalid ZIP file: {exc}") from exc

    for name in archive.namelist():
        normalized_name = normalize_path(name)
        if normalized_name.endswith("/"):
            continue
        if should_skip_path(normalized_name):
            continue
        if Path(normalized_name).suffix.lower() not in SUPPORTED_CODE_SUFFIXES:
            continue
        try:
            files[normalized_name] = archive.read(name).decode("utf-8", errors="ignore")
        except Exception:
            continue
    return files
