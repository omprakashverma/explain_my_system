import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from openapi_spec_validator import validate_spec
except ImportError:
    validate_spec = None


# =========================
# ENV CONFIG
# =========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample"
SAMPLE_CONTRACT_PATH = SAMPLE_DIR / "sample_api_contract.yaml"
SUPPORTED_CODE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx"}
SUPPORTED_CONTRACT_SUFFIXES = {".yaml", ".yml", ".json"}
HTTP_METHODS = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
    "trace",
)
COMMON_ROUTE_METHODS = (
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
)
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

FILE_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {}
REPOSITORY_META: Dict[str, Any] = {
    "source_type": None,
    "source_label": None,
    "loaded_at": None,
}
CONTRACT_STATE: Dict[str, Any] = {}

PYTHON_METHOD_DECORATOR_RE = re.compile(
    r"@(?P<owner>[\w\.]+)\.(?P<method>get|post|put|patch|delete|options|head|trace)"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
PYTHON_GENERIC_ROUTE_RE = re.compile(
    r"@(?P<owner>[\w\.]+)\.route"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)(?P<rest>.*?)\)",
    re.IGNORECASE | re.DOTALL,
)
PYTHON_ADD_API_ROUTE_RE = re.compile(
    r"(?P<owner>[\w\.]+)\.add_api_route"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)(?P<rest>.*?)\)",
    re.IGNORECASE | re.DOTALL,
)
PYTHON_ROUTER_RE = re.compile(
    r"(?P<name>\w+)\s*=\s*APIRouter\((?P<rest>.*?)\)",
    re.DOTALL,
)
PYTHON_BLUEPRINT_RE = re.compile(
    r"(?P<name>\w+)\s*=\s*Blueprint\((?P<rest>.*?)\)",
    re.DOTALL,
)
PYTHON_INCLUDE_ROUTER_RE = re.compile(
    r"[\w\.]+\.include_router\(\s*(?P<router>\w+)(?P<rest>.*?)\)",
    re.DOTALL,
)
PYTHON_REGISTER_BLUEPRINT_RE = re.compile(
    r"[\w\.]+\.register_blueprint\(\s*(?P<router>\w+)(?P<rest>.*?)\)",
    re.DOTALL,
)
JS_ROUTER_DEF_RE = re.compile(
    r"\b(?:const|let|var)\s+(?P<name>\w+)\s*=\s*(?:express\.)?Router\(",
    re.IGNORECASE,
)
JS_MOUNT_RE = re.compile(
    r"\b[\w\.]+\.use\(\s*(?P<quote>['\"`])(?P<prefix>.*?)(?P=quote)\s*,\s*(?P<router>\w+)",
    re.IGNORECASE | re.DOTALL,
)
JS_ROUTE_RE = re.compile(
    r"\b(?P<owner>\w+)\.(?P<method>get|post|put|patch|delete|options|head|all)"
    r"\(\s*(?P<quote>['\"`])(?P<path>.*?)(?P=quote)",
    re.IGNORECASE,
)
METHODS_ARG_RE = re.compile(
    r"methods\s*=\s*\[(?P<methods>[^\]]+)\]",
    re.IGNORECASE | re.DOTALL,
)
PREFIX_ARG_TEMPLATE = r"{arg_name}\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)"

# LLM_API_URL = os.getenv(
#     "LLM_API_URL",
#     "https://api.groq.com/openai/v1/chat/completions",
# )

# LLM_API_KEY = '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'

# LLM_MODEL = os.getenv(
#     "LLM_MODEL",
#     "meta-llama/llama-4-scout-17b-16e-instruct",
# )


class FileQuestionTag(BaseModel):
    path: str
    username: str
    question: str

LLM_API_URL = os.getenv(
    "LLM_API_URL",
    "https://api.groq.com/openai/v1/chat/completions"
)


LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)

class AskRequest(BaseModel):
    question: str


# =========================
# APP INIT
# =========================
app = FastAPI(title="Explain My System - Smart API Contract Validator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# MEMORY STORE
# =========================
FILES: Dict[str, str] = {}
CHUNKS: List[Dict[str, Any]] = []


# =========================
# HELPERS
# =========================
def chunk_text(text: str, path: str):
    lines = text.splitlines()
    chunks = []
    current = []

    for line in lines:
        current.append(line)

        if len("\n".join(current)) > 2000:
            chunks.append({
                "path": path,
                "text": "\n".join(current),
            })
            current = []

    if current:
        chunks.append({
            "path": path,
            "text": "\n".join(current),
        })

    return chunks


def load_chunks():
    CHUNKS.clear()

    for path, text in FILES.items():
        split_chunks = chunk_text(text, path)

        for idx, chunk in enumerate(split_chunks):
            CHUNKS.append({
                "path": path,
                "idx": idx,
                "text": chunk["text"],
            })


def retrieve_similar(question: str, top_k: int = 5):
    if not CHUNKS:
        return []

    scored = []
    q_words = question.lower().split()

    for chunk in CHUNKS:
        score = 0
        text = chunk["text"].lower()

        for word in q_words:
            if word in text:
                score += 1

        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def call_llm(messages):
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 600,
    }

    response = requests.post(
        LLM_API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise HTTPException(
            500,
            f"LLM API failed: {response.text}",
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]


def normalize_path(path: str):
    return path.replace("\\", "/").strip()


def should_skip_path(path: str) -> bool:
    normalized = normalize_path(path)
    parts = [part for part in normalized.split("/") if part]
    return any(part in IGNORED_PATH_PARTS for part in parts)


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


def normalize_prefix(prefix: str) -> str:
    value = clean_route_path(prefix)
    return "" if value == "/" else value


def join_route_paths(prefix: str, path: str) -> str:
    normalized_prefix = normalize_prefix(prefix)
    normalized_path = clean_route_path(path)

    if normalized_path == "/":
        return normalized_prefix or "/"

    return clean_route_path(f"{normalized_prefix}/{normalized_path.lstrip('/')}")


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

        if segment == "{}":
            segments.append(segment)
        else:
            segments.append(segment.lower())

    return "/" + "/".join(segments) if segments else "/"


def line_number_from_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def get_prefixed_argument(rest: str, arg_name: str) -> str:
    pattern = re.compile(
        PREFIX_ARG_TEMPLATE.format(arg_name=re.escape(arg_name)),
        re.DOTALL,
    )
    match = pattern.search(rest or "")
    return match.group("value") if match else ""


def parse_methods_from_rest(rest: str) -> List[str]:
    match = METHODS_ARG_RE.search(rest or "")

    if not match:
        return ["GET"]

    methods = []

    for item in re.findall(r"['\"]([A-Za-z]+)['\"]", match.group("methods")):
        upper_item = item.upper()

        if upper_item == "ALL":
            methods.extend(COMMON_ROUTE_METHODS)
        elif item.lower() in HTTP_METHODS:
            methods.append(upper_item)

    return sorted(set(methods)) or ["GET"]


def expand_route_methods(method: str) -> List[str]:
    if method.lower() == "all":
        return list(COMMON_ROUTE_METHODS)

    return [method.upper()]


def is_probable_python_route_owner(owner: str, known_prefixes: Dict[str, List[str]]) -> bool:
    token = owner.split(".")[-1]
    lowered = token.lower()

    return (
        token in known_prefixes
        or lowered in {"app", "api", "router", "bp", "blueprint", "application"}
        or lowered.endswith("router")
        or lowered.endswith("blueprint")
        or lowered.endswith("bp")
    )


def is_probable_js_route_owner(owner: str, router_names: List[str]) -> bool:
    lowered = owner.lower()

    return (
        owner in router_names
        or lowered in {"app", "api", "router", "server", "application"}
        or lowered.endswith("router")
    )


def combine_prefix_candidates(mounts: List[str], base_prefix: str) -> List[str]:
    normalized_base = normalize_prefix(base_prefix)
    normalized_mounts = [normalize_prefix(item) for item in mounts] if mounts else [""]
    combined = set()

    for mount in normalized_mounts:
        if mount or normalized_base:
            full_prefix = join_route_paths(mount, normalized_base or "/")
            combined.add("" if full_prefix == "/" else full_prefix)
        else:
            combined.add("")

    return sorted(combined)


def add_operation(
    operations: List[Dict[str, Any]],
    seen: set,
    method: str,
    path: str,
    file_path: str,
    line: int,
    framework: str,
):
    raw_path = clean_route_path(path)
    canonical_path = canonicalize_route_path(raw_path)
    key = (method.upper(), canonical_path, file_path, line)

    if key in seen:
        return

    seen.add(key)
    operations.append({
        "method": method.upper(),
        "path": raw_path,
        "canonical_path": canonical_path,
        "file": file_path,
        "line": line,
        "framework": framework,
    })


def build_repo_context(files: Dict[str, str]) -> Dict[str, Any]:
    python_base_prefixes = {}
    python_mounts = defaultdict(set)
    js_router_names = set()
    js_mounts = defaultdict(set)

    for file_path, text in files.items():
        suffix = Path(file_path).suffix.lower()

        if suffix == ".py":
            for match in PYTHON_ROUTER_RE.finditer(text):
                python_base_prefixes[match.group("name")] = get_prefixed_argument(
                    match.group("rest"),
                    "prefix",
                )

            for match in PYTHON_BLUEPRINT_RE.finditer(text):
                python_base_prefixes[match.group("name")] = get_prefixed_argument(
                    match.group("rest"),
                    "url_prefix",
                )

            for match in PYTHON_INCLUDE_ROUTER_RE.finditer(text):
                python_mounts[match.group("router")].add(
                    get_prefixed_argument(match.group("rest"), "prefix")
                )

            for match in PYTHON_REGISTER_BLUEPRINT_RE.finditer(text):
                python_mounts[match.group("router")].add(
                    get_prefixed_argument(match.group("rest"), "url_prefix")
                )

        elif suffix in {".js", ".ts", ".tsx", ".jsx"}:
            for match in JS_ROUTER_DEF_RE.finditer(text):
                js_router_names.add(match.group("name"))

            for match in JS_MOUNT_RE.finditer(text):
                js_mounts[match.group("router")].add(match.group("prefix"))

    python_prefixes = defaultdict(list)

    for name, base_prefix in python_base_prefixes.items():
        python_prefixes[name].extend(
            combine_prefix_candidates(
                list(python_mounts.get(name, [])),
                base_prefix,
            )
        )

    for name, mounts in python_mounts.items():
        if name not in python_prefixes:
            python_prefixes[name].extend(combine_prefix_candidates(list(mounts), ""))

    js_prefixes = defaultdict(list)

    for name in js_router_names:
        js_prefixes[name].extend(
            combine_prefix_candidates(list(js_mounts.get(name, [])), "")
        )

    for name, mounts in js_mounts.items():
        if name not in js_prefixes:
            js_prefixes[name].extend(combine_prefix_candidates(list(mounts), ""))

    return {
        "python_prefixes": {
            name: sorted(set(prefixes))
            for name, prefixes in python_prefixes.items()
        },
        "js_prefixes": {
            name: sorted(set(prefixes))
            for name, prefixes in js_prefixes.items()
        },
        "js_router_names": sorted(js_router_names),
    }


def extract_repository_operations(files: Dict[str, str]) -> List[Dict[str, Any]]:
    context = build_repo_context(files)
    operations: List[Dict[str, Any]] = []
    seen = set()

    for file_path, text in files.items():
        suffix = Path(file_path).suffix.lower()

        if suffix == ".py":
            python_prefixes = context["python_prefixes"]

            for match in PYTHON_METHOD_DECORATOR_RE.finditer(text):
                owner = match.group("owner")
                owner_token = owner.split(".")[-1]

                if not is_probable_python_route_owner(owner, python_prefixes):
                    continue

                route_prefixes = python_prefixes.get(owner_token, [""])

                for route_prefix in route_prefixes:
                    add_operation(
                        operations,
                        seen,
                        match.group("method"),
                        join_route_paths(route_prefix, match.group("path")),
                        file_path,
                        line_number_from_offset(text, match.start()),
                        "python",
                    )

            for match in PYTHON_GENERIC_ROUTE_RE.finditer(text):
                owner = match.group("owner")
                owner_token = owner.split(".")[-1]

                if not is_probable_python_route_owner(owner, python_prefixes):
                    continue

                route_prefixes = python_prefixes.get(owner_token, [""])

                for method in parse_methods_from_rest(match.group("rest")):
                    for route_prefix in route_prefixes:
                        add_operation(
                            operations,
                            seen,
                            method,
                            join_route_paths(route_prefix, match.group("path")),
                            file_path,
                            line_number_from_offset(text, match.start()),
                            "python",
                        )

            for match in PYTHON_ADD_API_ROUTE_RE.finditer(text):
                for method in parse_methods_from_rest(match.group("rest")):
                    add_operation(
                        operations,
                        seen,
                        method,
                        match.group("path"),
                        file_path,
                        line_number_from_offset(text, match.start()),
                        "python",
                    )

        elif suffix in {".js", ".ts", ".tsx", ".jsx"}:
            js_prefixes = context["js_prefixes"]
            js_router_names = context["js_router_names"]

            for match in JS_ROUTE_RE.finditer(text):
                owner = match.group("owner")

                if not is_probable_js_route_owner(owner, js_router_names):
                    continue

                route_prefixes = js_prefixes.get(owner, [""])

                for method in expand_route_methods(match.group("method")):
                    for route_prefix in route_prefixes:
                        add_operation(
                            operations,
                            seen,
                            method,
                            join_route_paths(route_prefix, match.group("path")),
                            file_path,
                            line_number_from_offset(text, match.start()),
                            "javascript",
                        )

    operations.sort(key=lambda item: (item["path"], item["method"], item["file"], item["line"]))
    return operations


def extract_contract_operations(document: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(document, dict):
        return []

    paths = document.get("paths", {})

    if not isinstance(paths, dict):
        return []

    operations = []

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue

            entry = operation if isinstance(operation, dict) else {}
            clean_path = clean_route_path(path)

            operations.append({
                "method": method.upper(),
                "path": clean_path,
                "canonical_path": canonicalize_route_path(clean_path),
                "operation_id": entry.get("operationId"),
                "summary": entry.get("summary"),
            })

    operations.sort(key=lambda item: (item["path"], item["method"]))
    return operations


def build_empty_contract_snapshot() -> Dict[str, Any]:
    return {
        "loaded": False,
        "filename": None,
        "title": None,
        "version": None,
        "openapi_version": None,
        "path_count": 0,
        "operation_count": 0,
        "raw_text": "",
        "operations": [],
        "validation": {
            "valid": False,
            "errors": [],
            "warnings": [],
        },
    }


def validate_contract_document(document: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors = []
    warnings = []

    if not isinstance(document, dict):
        return ["The contract file must contain a JSON or YAML object."], warnings

    openapi_version = document.get("openapi")

    if not openapi_version:
        errors.append("Missing top-level 'openapi' version.")
    elif not str(openapi_version).startswith("3."):
        errors.append("Only OpenAPI 3.x contracts are supported.")

    info = document.get("info")

    if not isinstance(info, dict):
        errors.append("Missing required 'info' object.")
    else:
        if not info.get("title"):
            errors.append("Contract 'info.title' is required.")

        if not info.get("version"):
            errors.append("Contract 'info.version' is required.")

    paths = document.get("paths")

    if not isinstance(paths, dict) or not paths:
        errors.append("Contract must declare at least one path in 'paths'.")

    if validate_spec and not errors:
        try:
            validate_spec(document)
        except Exception as exc:
            errors.append(str(exc))
    elif validate_spec is None:
        warnings.append(
            "openapi-spec-validator is not installed in the current environment, "
            "so structural validation is being used."
        )

    return errors, warnings


def build_contract_snapshot(
    filename: str,
    raw_text: str,
    document: Dict[str, Any],
    errors: List[str],
    warnings: List[str],
) -> Dict[str, Any]:
    info = document.get("info", {}) if isinstance(document, dict) else {}
    operations = extract_contract_operations(document)
    paths = document.get("paths", {}) if isinstance(document, dict) else {}

    return {
        "loaded": True,
        "filename": filename,
        "title": info.get("title"),
        "version": info.get("version"),
        "openapi_version": document.get("openapi") if isinstance(document, dict) else None,
        "path_count": len(paths) if isinstance(paths, dict) else 0,
        "operation_count": len(operations),
        "raw_text": raw_text,
        "operations": operations,
        "validation": {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
        },
    }


def store_contract_text(raw_text: str, filename: str) -> Dict[str, Any]:
    document = None
    errors = []
    warnings = []
    extension = Path(filename or "").suffix.lower()

    try:
        if extension == ".json":
            document = json.loads(raw_text)
        else:
            document = yaml.safe_load(raw_text)
    except Exception as exc:
        errors.append(f"Could not parse contract: {exc}")

    if document is not None:
        extra_errors, extra_warnings = validate_contract_document(document)
        errors.extend(extra_errors)
        warnings.extend(extra_warnings)

    snapshot = build_contract_snapshot(
        filename=filename,
        raw_text=raw_text,
        document=document if isinstance(document, dict) else {},
        errors=errors,
        warnings=warnings,
    )

    CONTRACT_STATE.clear()
    CONTRACT_STATE["document"] = document if isinstance(document, dict) else None
    CONTRACT_STATE["snapshot"] = snapshot
    return snapshot


def get_contract_snapshot() -> Dict[str, Any]:
    return CONTRACT_STATE.get("snapshot", build_empty_contract_snapshot())


def build_summary_payload() -> Dict[str, Any]:
    return {
        "file_count": len(FILES),
        "top_files": list(FILES.keys())[:10],
        "source_type": REPOSITORY_META.get("source_type"),
        "source_label": REPOSITORY_META.get("source_label"),
        "loaded_at": REPOSITORY_META.get("loaded_at"),
        "contract_loaded": get_contract_snapshot()["loaded"],
    }


def read_code_files_from_directory(directory: Path) -> Dict[str, str]:
    files = {}

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = normalize_path(str(file_path.relative_to(directory)))

        if should_skip_path(relative_path):
            continue

        if file_path.suffix.lower() not in SUPPORTED_CODE_SUFFIXES:
            continue

        try:
            files[relative_path] = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except Exception:
            continue

    return files


def read_code_files_from_zip(data: bytes) -> Dict[str, str]:
    files = {}

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
            files[normalized_name] = archive.read(name).decode(
                "utf-8",
                errors="ignore",
            )
        except Exception:
            continue

    return files


def store_repository_files(
    files: Dict[str, str],
    source_type: str,
    source_label: str,
) -> Dict[str, Any]:
    if not files:
        raise HTTPException(
            400,
            "No supported source files were found. Upload a ZIP or repo with Python/JS API files.",
        )

    FILES.clear()
    FILES.update(dict(sorted(files.items())))
    FILE_QUESTIONS.clear()
    load_chunks()

    REPOSITORY_META.update({
        "source_type": source_type,
        "source_label": source_label,
        "loaded_at": datetime.utcnow().isoformat(),
    })

    return {
        "files": len(FILES),
        "chunks": len(CHUNKS),
        "source_type": source_type,
        "source_label": source_label,
    }


def build_validation_alert(
    severity: str,
    category: str,
    message: str,
    contract_path: str = None,
    repo_path: str = None,
    expected_methods: List[str] = None,
    detected_methods: List[str] = None,
    source_file: str = None,
    source_line: int = None,
    ) -> Dict[str, Any]:
    return {
        "severity": severity,
        "category": category,
        "message": message,
        "contract_path": contract_path,
        "repo_path": repo_path,
        "expected_methods": expected_methods or [],
        "detected_methods": detected_methods or [],
        "source_file": source_file,
        "source_line": source_line,
    }


def build_comparison_row(
    status: str,
    contract_operation: Dict[str, Any] = None,
    repo_operation: Dict[str, Any] = None,
) -> Dict[str, Any]:
    contract_entry = contract_operation or {}
    repo_entry = repo_operation or {}
    severity_by_status = {
        "matched": "pass",
        "missing": "high",
        "undocumented": "medium",
    }

    return {
        "status": status,
        "severity": severity_by_status.get(status, "info"),
        "method": contract_entry.get("method") or repo_entry.get("method"),
        "contract_path": contract_entry.get("path"),
        "repo_path": repo_entry.get("path"),
        "contract_label": (
            f"{contract_entry['method']} {contract_entry['path']}"
            if contract_entry
            else "Missing"
        ),
        "repo_label": (
            f"{repo_entry['method']} {repo_entry['path']}"
            if repo_entry
            else "Missing"
        ),
        "source_file": repo_entry.get("file"),
        "source_line": repo_entry.get("line"),
        "framework": repo_entry.get("framework"),
        "clickable": bool(repo_entry.get("file")),
    }


def validate_loaded_repository_against_contract() -> Dict[str, Any]:
    if not FILES:
        raise HTTPException(
            400,
            "Load a ZIP file, sample project, or git repository before validating.",
        )

    contract_snapshot = get_contract_snapshot()
    contract_document = CONTRACT_STATE.get("document")

    if not contract_snapshot["loaded"]:
        raise HTTPException(400, "Upload an OpenAPI contract before validating.")

    if not contract_document or not contract_snapshot["validation"]["valid"]:
        raise HTTPException(
            400,
            "The uploaded contract is invalid. Fix the contract errors before validating.",
        )

    repo_operations = extract_repository_operations(FILES)
    contract_operations = contract_snapshot["operations"]
    repo_operation_keys = {
        (item["method"], item["canonical_path"])
        for item in repo_operations
    }
    contract_operation_keys = {
        (item["method"], item["canonical_path"])
        for item in contract_operations
    }
    matched_operations = len(repo_operation_keys & contract_operation_keys)
    alerts = []
    comparison_rows = []
    repo_by_path = defaultdict(list)
    contract_by_path = defaultdict(list)
    repo_by_key = defaultdict(list)
    contract_by_key = defaultdict(list)

    for operation in repo_operations:
        repo_by_path[operation["canonical_path"]].append(operation)
        repo_by_key[(operation["method"], operation["canonical_path"])].append(operation)

    for operation in contract_operations:
        contract_by_path[operation["canonical_path"]].append(operation)
        contract_by_key[(operation["method"], operation["canonical_path"])].append(operation)

    all_paths = sorted(set(repo_by_path) | set(contract_by_path))

    for canonical_path in all_paths:
        repo_ops = repo_by_path.get(canonical_path, [])
        contract_ops = contract_by_path.get(canonical_path, [])
        repo_methods = sorted({item["method"] for item in repo_ops})
        contract_methods = sorted({item["method"] for item in contract_ops})
        contract_path = contract_ops[0]["path"] if contract_ops else None
        repo_path = repo_ops[0]["path"] if repo_ops else None
        primary_repo_op = repo_ops[0] if repo_ops else {}

        if contract_methods and not repo_methods:
            alerts.append(build_validation_alert(
                severity="high",
                category="missing_path",
                message=(
                    f"The contract expects {', '.join(contract_methods)} on {contract_path}, "
                    "but no matching route was detected in the loaded repository."
                ),
                contract_path=contract_path,
                expected_methods=contract_methods,
            ))
            continue

        if contract_methods and sorted(set(contract_methods) - set(repo_methods)):
            missing_methods = sorted(set(contract_methods) - set(repo_methods))
            alerts.append(build_validation_alert(
                severity="high",
                category="method_mismatch",
                message=(
                    f"The contract expects {', '.join(missing_methods)} on {contract_path}, "
                    f"but the repository exposes {', '.join(repo_methods)} for that path."
                ),
                contract_path=contract_path,
                repo_path=repo_path,
                expected_methods=contract_methods,
                detected_methods=repo_methods,
                source_file=primary_repo_op.get("file"),
                source_line=primary_repo_op.get("line"),
            ))

        if repo_methods and not contract_methods:
            alerts.append(build_validation_alert(
                severity="medium",
                category="undocumented_path",
                message=(
                    f"The repository exposes {', '.join(repo_methods)} on {repo_path}, "
                    "but that path is not documented in the uploaded contract."
                ),
                repo_path=repo_path,
                detected_methods=repo_methods,
                source_file=primary_repo_op.get("file"),
                source_line=primary_repo_op.get("line"),
            ))
            continue

        extra_methods = sorted(set(repo_methods) - set(contract_methods))

        if extra_methods:
            alerts.append(build_validation_alert(
                severity="medium",
                category="undocumented_methods",
                message=(
                    f"The repository exposes undocumented methods {', '.join(extra_methods)} "
                    f"on {repo_path}. The contract only documents {', '.join(contract_methods)}."
                ),
                contract_path=contract_path,
                repo_path=repo_path,
                expected_methods=contract_methods,
                detected_methods=repo_methods,
                source_file=primary_repo_op.get("file"),
                source_line=primary_repo_op.get("line"),
            ))

    if not repo_operations:
            alerts.append(build_validation_alert(
                severity="info",
                category="detection_warning",
            message=(
                "No API route declarations were detected. The validator currently recognizes "
                "FastAPI, Flask, and Express-style route definitions."
            ),
        ))

    comparison_key_order = {"missing": 0, "undocumented": 1, "matched": 2}

    for operation_key in sorted(set(repo_by_key) | set(contract_by_key)):
        contract_op = contract_by_key.get(operation_key, [None])[0]
        repo_op = repo_by_key.get(operation_key, [None])[0]

        if contract_op and repo_op:
            row_status = "matched"
        elif contract_op:
            row_status = "missing"
        else:
            row_status = "undocumented"

        comparison_rows.append(build_comparison_row(
            status=row_status,
            contract_operation=contract_op,
            repo_operation=repo_op,
        ))

    comparison_rows.sort(
        key=lambda item: (
            comparison_key_order.get(item["status"], 99),
            item["contract_path"] or item["repo_path"] or "",
            item["method"] or "",
        )
    )

    severity_order = {"high": 0, "medium": 1, "info": 2}
    alerts.sort(
        key=lambda item: (
            severity_order.get(item["severity"], 99),
            item.get("contract_path") or item.get("repo_path") or "",
            item["message"],
        )
    )

    if alerts and any(item["severity"] == "high" for item in alerts):
        status = "mismatch"
        summary = (
            f"Detected {len(alerts)} contract alert(s), including required route mismatches."
        )
    elif alerts:
        status = "warning"
        summary = f"Detected {len(alerts)} documentation gap(s) between the repo and contract."
    elif repo_operations:
        status = "pass"
        summary = "Detected routes are aligned with the uploaded OpenAPI contract."
    else:
        status = "warning"
        summary = "No routes were detected, so the contract could not be verified fully."

    contract_only_operations = len(contract_operation_keys - repo_operation_keys)
    undocumented_operations = len(repo_operation_keys - contract_operation_keys)
    contract_operation_total = len(contract_operation_keys)
    compliance_score = (
        round((matched_operations / contract_operation_total) * 100)
        if contract_operation_total
        else 0
    )

    return {
        "status": status,
        "summary": summary,
        "health": {
            "score": compliance_score,
            "matched_operations": matched_operations,
            "required_operations": contract_operation_total,
            "missing_operations": contract_only_operations,
            "undocumented_operations": undocumented_operations,
        },
        "counts": {
            "contract_operations": len(contract_operations),
            "repo_operations": len(repo_operations),
            "matched_operations": matched_operations,
            "alerts": len(alerts),
        },
        "frameworks_detected": sorted({item["framework"] for item in repo_operations}),
        "alerts": alerts,
        "comparison_rows": comparison_rows,
        "repo_operations": repo_operations,
        "contract_operations": contract_operations,
    }


# =========================
# ROUTES
# =========================
@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    data = await file.read()
    files = read_code_files_from_zip(data)
    return store_repository_files(files, "zip", file.filename or "Uploaded ZIP")


@app.post("/load-git")
async def load_git(url: str):
    tmp = tempfile.mkdtemp(prefix="repo_")

    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, tmp],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "git clone failed"
            raise HTTPException(400, detail)

        files = read_code_files_from_directory(Path(tmp))
        return store_repository_files(files, "git", url)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@app.post("/load-sample")
async def load_sample():
    if not SAMPLE_DIR.exists():
        raise HTTPException(404, "Sample directory not found.")

    files = read_code_files_from_directory(SAMPLE_DIR)
    return store_repository_files(files, "sample", "Bundled sample API")


@app.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in SUPPORTED_CONTRACT_SUFFIXES:
        raise HTTPException(
            400,
            "Contract files must be .yaml, .yml, or .json.",
        )

    raw_text = (await file.read()).decode("utf-8", errors="ignore")
    return store_contract_text(raw_text, file.filename or "contract.yaml")


@app.post("/load-sample-contract")
async def load_sample_contract():
    if not SAMPLE_CONTRACT_PATH.exists():
        raise HTTPException(404, "Sample contract file not found.")

    return store_contract_text(
        SAMPLE_CONTRACT_PATH.read_text(encoding="utf-8"),
        SAMPLE_CONTRACT_PATH.name,
    )


@app.post("/validate-contract")
async def validate_contract():
    return validate_loaded_repository_against_contract()


@app.get("/contract")
async def get_contract():
    return get_contract_snapshot()


@app.get("/files")
async def list_files():
    return {"files": list(FILES.keys())}


@app.get("/files-full")
async def files_full():
    return {
        "files": list(FILES.keys()),
        "contents": FILES,
    }


@app.get("/file")
async def get_file(path: str = Query(...)):
    normalized = normalize_path(path)

    if normalized not in FILES:
        raise HTTPException(
            404,
            detail=f"File not found: {normalized}",
        )

    related_chunks = [
        chunk for chunk in CHUNKS
        if normalize_path(chunk["path"]) == normalized
    ]

    return {
        "path": normalized,
        "text": FILES[normalized],
        "chunks": related_chunks[:5],
        "questions": FILE_QUESTIONS.get(normalized, []),
    }


@app.get("/summary")
async def summary():
    return build_summary_payload()


@app.get("/repo-summary")
async def repo_summary():
    context = "\n".join([
        f"{path}\n{text[:1000]}"
        for path, text in list(FILES.items())[:5]
    ])

    answer = call_llm([
        {
            "role": "system",
            "content": (
                "You are a senior software architect. "
                "Explain the codebase in plain English."
            ),
        },
        {
            "role": "user",
            "content": context,
        },
    ])

    return {"summary": answer}


@app.post("/tag-question")
async def tag_question(req: FileQuestionTag):
    normalized = normalize_path(req.path)

    if normalized not in FILES:
        raise HTTPException(404, f"File not found: {normalized}")

    if normalized not in FILE_QUESTIONS:
        FILE_QUESTIONS[normalized] = []

    FILE_QUESTIONS[normalized].append({
        "username": req.username,
        "question": req.question,
        "timestamp": datetime.utcnow().isoformat(),
    })

    return {
        "success": True,
        "file": normalized,
        "total_tags": len(FILE_QUESTIONS[normalized]),
    }


@app.post("/ask")
async def ask(req: AskRequest):
    context_chunks = retrieve_similar(req.question)
    context_text = "\n---\n".join([
        f"FILE: {chunk['path']}\n{chunk['text'][:1500]}"
        for chunk in context_chunks
    ])

    answer = call_llm([
        {
            "role": "system",
            "content": (
                "Explain code in simple English "
                "with short bullet points."
            ),
        },
        {
            "role": "user",
            "content": f"""
QUESTION:
{req.question}

CODE CONTEXT:
{context_text}
""",
        },
    ])

    return {
        "answer": answer,
        "found": len(context_chunks),
    }


@app.post("/clear")
async def clear_store():
    FILES.clear()
    CHUNKS.clear()
    FILE_QUESTIONS.clear()
    CONTRACT_STATE.clear()
    REPOSITORY_META.update({
        "source_type": None,
        "source_label": None,
        "loaded_at": None,
    })

    return {"cleared": True}
