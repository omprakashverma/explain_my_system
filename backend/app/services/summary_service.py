from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from backend.app.services.parser_service import extract_repository_operations
from backend.app.utils.text_utils import detect_language, normalize_path


def top_modules_from_files(files: Dict[str, str], limit: int = 6) -> List[str]:
    counts: Counter[str] = Counter()
    for path in files:
        normalized = normalize_path(path)
        parts = [part for part in normalized.split("/") if part]
        if len(parts) > 1:
            counts[parts[0]] += 1
        else:
            counts[Path(normalized).stem or "root"] += 1
    return [name for name, _ in counts.most_common(limit)]


def build_repo_summary(files: Dict[str, str], source_type: str, source_label: str, loaded_at: str) -> Dict[str, Any]:
    repo_operations = extract_repository_operations(files)
    language_count = len({detect_language(path) for path in files})
    endpoint_count = len({(op["method"], op["canonical_path"]) for op in repo_operations})
    frameworks_detected = sorted({op["framework"] for op in repo_operations})
    top_files = list(files.keys())[:10]
    top_modules = top_modules_from_files(files)
    overview = (
        f"Detected {len(files)} files across {language_count} language(s). "
        f"Found {endpoint_count} route(s) in the repository. "
        f"Top modules: {', '.join(top_modules) if top_modules else 'none detected'}."
    )
    if frameworks_detected:
        overview += f" Route frameworks detected: {', '.join(frameworks_detected)}."
    return {
        "status": "ready",
        "overview": overview,
        "file_count": len(files),
        "language_count": language_count,
        "endpoint_count": endpoint_count,
        "source_type": source_type,
        "source_label": source_label,
        "loaded_at": loaded_at,
        "top_modules": top_modules,
        "top_files": top_files,
        "frameworks_detected": frameworks_detected,
    }


def utc_timestamp() -> str:
    return datetime.utcnow().isoformat()
