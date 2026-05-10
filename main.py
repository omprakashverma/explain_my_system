import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =========================
# ENV CONFIG
# =========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
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

LLM_API_URL = os.getenv(
    "LLM_API_URL",
    "https://api.groq.com/openai/v1/chat/completions",
)
# LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct",
)

# =========================
# APP INIT
# =========================
app = FastAPI(title="Explain My System")

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
FILE_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {}

REPOSITORY_META: Dict[str, Any] = {
    "source_type": None,
    "source_label": None,
    "loaded_at": None,
}

SUMMARY_STATE: Dict[str, Any] = {
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

# =========================
# REQUEST MODELS
# =========================
class FileQuestionTag(BaseModel):
    path: str
    username: str
    question: str


class AskRequest(BaseModel):
    prompt: str
    selected_file: Optional[str] = None


# =========================
# REGEX HELPERS
# =========================
PYTHON_ROUTE_RE = re.compile(
    r"@(?P<owner>[\w\.]+)\.(?P<method>get|post|put|patch|delete|options|head|trace)"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
PYTHON_GENERIC_ROUTE_RE = re.compile(
    r"@(?P<owner>[\w\.]+)\.route"
    r"\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)(?P<rest>.*?)\)",
    re.IGNORECASE | re.DOTALL,
)
JS_ROUTE_RE = re.compile(
    r"\b(?P<owner>\w+)\.(?P<method>get|post|put|patch|delete|options|head|all)"
    r"\(\s*(?P<quote>['\"`])(?P<path>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
METHODS_ARG_RE = re.compile(
    r"methods\s*=\s*\[(?P<methods>[^\]]+)\]",
    re.IGNORECASE | re.DOTALL,
)

HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
    "trace",
}


# =========================
# BASIC HELPERS
# =========================
def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip()

def build_file_context(selected_file: Optional[str], prompt: str) -> str:
    if selected_file:
        normalized = normalize_path(selected_file)

        if normalized not in FILES:
            raise HTTPException(404, detail=f"File not found: {normalized}")

        file_text = FILES[normalized]
        related_chunks = [
            chunk for chunk in CHUNKS
            if normalize_path(chunk["path"]) == normalized
        ]

        chunk_text = "\n---\n".join(
            chunk["text"][:1500] for chunk in related_chunks[:5]
        )

        return f"""
SELECTED FILE:
{normalized}

FULL FILE CONTENT:
{file_text[:12000]}

RELEVANT CHUNKS FROM SAME FILE:
{chunk_text if chunk_text else "No chunks available."}
""".strip()

    # fallback: repo-wide retrieval if no file selected
    context_chunks = retrieve_similar(prompt)
    return "\n---\n".join(
        f"FILE: {chunk['path']}\n{chunk['text'][:1500]}"
        for chunk in context_chunks
    )

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


def parse_methods_from_rest(rest: str) -> List[str]:
    match = METHODS_ARG_RE.search(rest or "")
    if not match:
        return ["GET"]

    methods = []
    for item in re.findall(r"['\"]([A-Za-z]+)['\"]", match.group("methods")):
        upper_item = item.upper()
        if upper_item == "ALL":
            methods.extend(["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
        elif item.lower() in HTTP_METHODS:
            methods.append(upper_item)

    return sorted(set(methods)) or ["GET"]


def expand_route_methods(method: str) -> List[str]:
    if method.lower() == "all":
        return ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
    return [method.upper()]


# =========================
# CHUNKING / RETRIEVAL
# =========================
def chunk_text(text: str, path: str) -> List[Dict[str, str]]:
    lines = text.splitlines()
    chunks = []
    current = []

    for line in lines:
        current.append(line)
        if len("\n".join(current)) > 2000:
            chunks.append({"path": path, "text": "\n".join(current)})
            current = []

    if current:
        chunks.append({"path": path, "text": "\n".join(current)})

    return chunks


def load_chunks() -> None:
    CHUNKS.clear()

    for path, text in FILES.items():
        for idx, chunk in enumerate(chunk_text(text, path)):
            CHUNKS.append(
                {
                    "path": path,
                    "idx": idx,
                    "text": chunk["text"],
                }
            )


def retrieve_similar(question: str, top_k: int = 5):
    if not CHUNKS:
        return []

    scored = []
    q_words = [word for word in re.findall(r"\w+", question.lower()) if word]

    for chunk in CHUNKS:
        score = 0
        text = chunk["text"].lower()
        for word in q_words:
            if word in text:
                score += 1
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


# =========================
# LLM
# =========================
def call_llm(messages: List[Dict[str, str]]) -> str:
    if not LLM_API_KEY:
        return (
            "LLM is not configured. Set LLM_API_KEY to enable repository Q&A and summaries."
        )

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 700,
    }

    try:
        response = requests.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        return f"LLM request failed: {exc}"

    if response.status_code != 200:
        return f"LLM API failed: {response.text}"

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return "LLM returned an unexpected response format."


# =========================
# REPO FILE READERS
# =========================
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


# =========================
# ROUTE EXTRACTION
# =========================
def extract_repository_operations(files: Dict[str, str]) -> List[Dict[str, Any]]:
    operations: List[Dict[str, Any]] = []
    seen = set()

    for file_path, text in files.items():
        suffix = Path(file_path).suffix.lower()

        if suffix == ".py":
            for match in PYTHON_ROUTE_RE.finditer(text):
                method = match.group("method").upper()
                raw_path = clean_route_path(match.group("path"))
                key = (method, raw_path, file_path, line_number_from_offset(text, match.start()))

                if key in seen:
                    continue

                seen.add(key)
                operations.append(
                    {
                        "method": method,
                        "path": raw_path,
                        "canonical_path": canonicalize_route_path(raw_path),
                        "file": file_path,
                        "line": line_number_from_offset(text, match.start()),
                        "framework": "python",
                    }
                )

            for match in PYTHON_GENERIC_ROUTE_RE.finditer(text):
                methods = parse_methods_from_rest(match.group("rest"))
                raw_path = clean_route_path(match.group("path"))
                line_no = line_number_from_offset(text, match.start())

                for method in methods:
                    key = (method, raw_path, file_path, line_no)
                    if key in seen:
                        continue
                    seen.add(key)
                    operations.append(
                        {
                            "method": method,
                            "path": raw_path,
                            "canonical_path": canonicalize_route_path(raw_path),
                            "file": file_path,
                            "line": line_no,
                            "framework": "python",
                        }
                    )

        elif suffix in {".js", ".ts", ".tsx", ".jsx"}:
            for match in JS_ROUTE_RE.finditer(text):
                methods = expand_route_methods(match.group("method"))
                raw_path = clean_route_path(match.group("path"))
                line_no = line_number_from_offset(text, match.start())

                for method in methods:
                    key = (method, raw_path, file_path, line_no)
                    if key in seen:
                        continue
                    seen.add(key)
                    operations.append(
                        {
                            "method": method,
                            "path": raw_path,
                            "canonical_path": canonicalize_route_path(raw_path),
                            "file": file_path,
                            "line": line_no,
                            "framework": "javascript",
                        }
                    )

    operations.sort(key=lambda item: (item["path"], item["method"], item["file"], item["line"]))
    return operations


# =========================
# SUMMARY BUILDING
# =========================
def top_modules_from_files(files: Dict[str, str], limit: int = 6) -> List[str]:
    counts = Counter()

    for path in files.keys():
        normalized = normalize_path(path)
        parts = [p for p in normalized.split("/") if p]

        if len(parts) > 1:
            counts[parts[0]] += 1
        else:
            counts[Path(normalized).stem or "root"] += 1

    return [name for name, _ in counts.most_common(limit)]


def build_repo_summary(files: Dict[str, str], source_type: str, source_label: str, loaded_at: str) -> Dict[str, Any]:
    repo_operations = extract_repository_operations(files)
    language_count = len({detect_language(path) for path in files.keys()})
    endpoint_count = len(
        {(op["method"], op["canonical_path"]) for op in repo_operations}
    )
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


def update_summary_state(files: Dict[str, str], source_type: str, source_label: str) -> None:
    loaded_at = datetime.utcnow().isoformat()
    REPOSITORY_META.update(
        {
            "source_type": source_type,
            "source_label": source_label,
            "loaded_at": loaded_at,
        }
    )
    SUMMARY_STATE.clear()
    SUMMARY_STATE.update(build_repo_summary(files, source_type, source_label, loaded_at))


def store_repository_files(files: Dict[str, str], source_type: str, source_label: str) -> Dict[str, Any]:
    if not files:
        raise HTTPException(
            400,
            "No supported source files were found. Upload a ZIP or repo with Python/JS source files.",
        )

    FILES.clear()
    FILES.update(dict(sorted(files.items())))
    FILE_QUESTIONS.clear()
    load_chunks()
    update_summary_state(FILES, source_type, source_label)

    return {
        "files": len(FILES),
        "chunks": len(CHUNKS),
        "source_type": source_type,
        "source_label": source_label,
    }


def get_summary_payload() -> Dict[str, Any]:
    return SUMMARY_STATE if SUMMARY_STATE else {
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


# =========================
# FILE / QUESTION HELPERS
# =========================
def get_file_questions(path: str) -> List[Dict[str, Any]]:
    normalized = normalize_path(path)
    return FILE_QUESTIONS.get(normalized, [])


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
    return store_repository_files(files, "sample", "Bundled sample repository")


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
        raise HTTPException(404, detail=f"File not found: {normalized}")

    related_chunks = [
        chunk for chunk in CHUNKS
        if normalize_path(chunk["path"]) == normalized
    ]

    return {
        "path": normalized,
        "text": FILES[normalized],
        "chunks": related_chunks[:5],
        "questions": get_file_questions(normalized),
    }


@app.get("/summary")
async def summary():
    return get_summary_payload()


@app.get("/repo-summary")
async def repo_summary():
    context = "\n".join(
        [f"{path}\n{text[:1000]}" for path, text in list(FILES.items())[:5]]
    )

    answer = call_llm(
        [
            {
                "role": "system",
                "content": (
                    "You are a senior software architect. "
                    "Explain the codebase in plain English in a concise summary."
                ),
            },
            {
                "role": "user",
                "content": context if context else "No repository loaded.",
            },
        ]
    )

    return {"summary": answer}


@app.post("/tag-question")
async def tag_question(req: FileQuestionTag):
    normalized = normalize_path(req.path)

    if normalized not in FILES:
        raise HTTPException(404, f"File not found: {normalized}")

    if normalized not in FILE_QUESTIONS:
        FILE_QUESTIONS[normalized] = []

    FILE_QUESTIONS[normalized].append(
        {
            "username": req.username,
            "question": req.question,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return {
        "success": True,
        "file": normalized,
        "total_tags": len(FILE_QUESTIONS[normalized]),
    }


@app.post("/ask")
async def ask(req: AskRequest):
    if not FILES:
        raise HTTPException(400, "Load a repository before asking questions.")

    if not req.prompt.strip():
        raise HTTPException(400, "Prompt cannot be empty.")

    context_text = build_file_context(req.selected_file, req.prompt)

    answer = call_llm(
        [
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer helping explain a specific source file. "
                    "Answer only using the provided file context. "
                    "If the answer cannot be derived from the file, say that clearly. "
                    "Do not give generic repository-wide answers unless no file is selected."
                ),
            },
            {
                "role": "user",
                "content": f"""
USER PROMPT:
{req.prompt}

FILE CONTEXT:
{context_text if context_text else "No context available."}
""",
            },
        ]
    )

    return {
        "answer": answer,
        "found": 1 if req.selected_file else len(retrieve_similar(req.prompt)),
        "selected_file": req.selected_file,
    }

@app.post("/clear")
async def clear_store():
    FILES.clear()
    CHUNKS.clear()
    FILE_QUESTIONS.clear()
    REPOSITORY_META.update(
        {
            "source_type": None,
            "source_label": None,
            "loaded_at": None,
        }
    )
    SUMMARY_STATE.clear()
    SUMMARY_STATE.update(
        {
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
    )

    return {"cleared": True}