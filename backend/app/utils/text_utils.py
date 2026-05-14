import re
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException

from backend.app.core.constants import IGNORED_PATH_PARTS


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()


def should_skip_path(path: str) -> bool:
    normalized = normalize_path(path)
    parts = [part for part in normalized.split("/") if part]
    return any(part in IGNORED_PATH_PARTS for part in parts)


def detect_language(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    return {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript React",
        ".jsx": "JavaScript React",
    }.get(suffix, "Unknown")


def clean_route_path(path: str) -> str:
    value = (path or "").strip()
    if not value:
        return "/"
    if not value.startswith("/"):
        value = f"/{value}"
    value = re.sub(r"/{2,}", "/", value)
    if len(value) > 1 and value.endswith("/"):
        value = value[:-1]
    return value


def canonicalize_route_path(path: str) -> str:
    value = clean_route_path(path)
    value = re.sub(r"<[^>]+>", "{}", value)
    value = re.sub(r"\$\{[^}]+\}", "{}", value)
    value = re.sub(r":([A-Za-z_][A-Za-z0-9_-]*)", "{}", value)
    value = re.sub(r"\{[^}]+\}", "{}", value)
    segments = []
    for segment in value.split("/"):
        if not segment:
            continue
        segments.append(segment if segment == "{}" else segment.lower())
    return "/" + "/".join(segments) if segments else "/"


def line_number_from_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def ensure_file_exists(files: dict[str, str], path: Optional[str]) -> str:
    normalized = normalize_path(path or "")
    if normalized not in files:
        raise HTTPException(404, detail=f"File not found: {normalized}")
    return normalized


def split_words(value: str) -> List[str]:
    return [word for word in re.findall(r"\w+", value.lower()) if word]
