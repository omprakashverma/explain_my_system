import os
import zipfile
import io
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# =========================
# ENV CONFIG
# =========================
load_dotenv()

FILE_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {}


class FileQuestionTag(BaseModel):
    path: str
    username: str
    question: str

LLM_API_URL = os.getenv(
    "LLM_API_URL",
    "https://api.groq.com/openai/v1/chat/completions"
)

LLM_API_KEY = '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'

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct"
)

# =========================
# APP INIT
# =========================
app = FastAPI(title="Explain My System - POC")

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
# REQUEST MODELS
# =========================
class AskRequest(BaseModel):
    question: str


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
                "text": "\n".join(current)
            })
            current = []

    if current:
        chunks.append({
            "path": path,
            "text": "\n".join(current)
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
                "text": chunk["text"]
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

    scored.sort(key=lambda x: x[0], reverse=True)

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
        timeout=60
    )

    if response.status_code != 200:
        raise HTTPException(
            500,
            f"LLM API failed: {response.text}"
        )

    data = response.json()

    return data["choices"][0]["message"]["content"]


def normalize_path(path: str):
    return path.replace("\\", "/").strip()


# =========================
# ROUTES
# =========================
@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    data = await file.read()

    z = zipfile.ZipFile(io.BytesIO(data))

    FILES.clear()

    for name in z.namelist():
        if name.endswith("/"):
            continue

        if name.endswith((
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx"
        )):
            try:
                content = z.read(name).decode(
                    "utf-8",
                    errors="ignore"
                )

                FILES[normalize_path(name)] = content

            except Exception:
                continue

    load_chunks()

    return {
        "files": len(FILES),
        "chunks": len(CHUNKS)
    }


@app.post("/load-git")
async def load_git(url: str):
    tmp = tempfile.mkdtemp(prefix="repo_")

    try:
        subprocess.check_call(
            ["git", "clone", "--depth", "1", url, tmp],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        FILES.clear()

        for p in Path(tmp).rglob("*"):
            if p.is_file() and p.suffix in (
                ".py",
                ".js",
                ".ts",
                ".tsx",
                ".jsx"
            ):
                try:
                    rel_path = normalize_path(
                        str(p.relative_to(tmp))
                    )

                    FILES[rel_path] = p.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )

                except Exception:
                    continue

        load_chunks()

        return {
            "files": len(FILES),
            "chunks": len(CHUNKS)
        }

    except Exception as e:
        raise HTTPException(400, str(e))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@app.get("/files")
async def list_files():
    return {"files": list(FILES.keys())}


@app.get("/files-full")
async def files_full():
    return {
        "files": list(FILES.keys()),
        "contents": FILES
    }


# =========================
# FIXED PREVIEW ENDPOINT
# =========================
@app.get("/file")
async def get_file(path: str = Query(...)):
    normalized = normalize_path(path)

    if normalized not in FILES:
        raise HTTPException(
            404,
            detail=f"File not found: {normalized}"
        )

    related_chunks = [
        c for c in CHUNKS
        if normalize_path(c["path"]) == normalized
    ]

    return {
        "path": normalized,
        "text": FILES[normalized],
        "chunks": related_chunks[:5],
        "questions": FILE_QUESTIONS.get(normalized, [])
    }



@app.get("/summary")
async def summary():
    return {
        "file_count": len(FILES),
        "top_files": list(FILES.keys())[:10]
    }


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
            )
        },
        {
            "role": "user",
            "content": context
        }
    ])

    return {"summary": answer}

@app.post("/tag-question")
async def tag_question(req: FileQuestionTag):
    normalized = normalize_path(req.path)

    if normalized not in FILE_QUESTIONS:
        FILE_QUESTIONS[normalized] = []

    FILE_QUESTIONS[normalized].append({
        "username": req.username,
        "question": req.question,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "success": True,
        "file": normalized,
        "total_tags": len(FILE_QUESTIONS[normalized])
    }


@app.post("/ask")
async def ask(req: AskRequest):
    context_chunks = retrieve_similar(req.question)

    context_text = "\n---\n".join([
        f"FILE: {c['path']}\n{c['text'][:1500]}"
        for c in context_chunks
    ])

    answer = call_llm([
        {
            "role": "system",
            "content": (
                "Explain code in simple English "
                "with short bullet points."
            )
        },
        {
            "role": "user",
            "content": f"""
QUESTION:
{req.question}

CODE CONTEXT:
{context_text}
"""
        }
    ])

    return {
        "answer": answer,
        "found": len(context_chunks)
    }


@app.post("/clear")
async def clear_store():
    FILES.clear()
    CHUNKS.clear()
    FILE_QUESTIONS.clear()

    return {"cleared": True}






