from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from fastapi import HTTPException

from backend.app.core.constants import DEFAULT_SUMMARY_STATE
from backend.app.services.summary_service import build_repo_summary, utc_timestamp
from backend.app.utils.text_utils import ensure_file_exists, normalize_path, split_words


@dataclass
class RepositoryStore:
    files: Dict[str, str] = field(default_factory=dict)
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    file_questions: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    repository_meta: Dict[str, Any] = field(
        default_factory=lambda: {
            "source_type": None,
            "source_label": None,
            "loaded_at": None,
        }
    )
    summary_state: Dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_SUMMARY_STATE))

    def chunk_text(self, text: str, path: str) -> List[Dict[str, str]]:
        lines = text.splitlines()
        chunks: List[Dict[str, str]] = []
        current: List[str] = []
        for line in lines:
            current.append(line)
            if len("\n".join(current)) > 2000:
                chunks.append({"path": path, "text": "\n".join(current)})
                current = []
        if current:
            chunks.append({"path": path, "text": "\n".join(current)})
        return chunks

    def reload_chunks(self) -> None:
        self.chunks.clear()
        for path, text in self.files.items():
            for idx, chunk in enumerate(self.chunk_text(text, path)):
                self.chunks.append({"path": path, "idx": idx, "text": chunk["text"]})

    def retrieve_similar(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []
        scored: List[tuple[int, Dict[str, Any]]] = []
        q_words = split_words(question)
        for chunk in self.chunks:
            text = chunk["text"].lower()
            score = sum(1 for word in q_words if word in text)
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def build_file_context(self, selected_file: str | None, prompt: str) -> str:
        if selected_file:
            normalized = ensure_file_exists(self.files, selected_file)
            file_text = self.files[normalized]
            related_chunks = [chunk for chunk in self.chunks if normalize_path(chunk["path"]) == normalized]
            chunk_text = "\n---\n".join(chunk["text"][:1500] for chunk in related_chunks[:5])
            return (
                "SELECTED FILE:\n"
                f"{normalized}\n\n"
                "FULL FILE CONTENT:\n"
                f"{file_text[:12000]}\n\n"
                "RELEVANT CHUNKS FROM SAME FILE:\n"
                f"{chunk_text if chunk_text else 'No chunks available.'}"
            )
        context_chunks = self.retrieve_similar(prompt)
        return "\n---\n".join(f"FILE: {chunk['path']}\n{chunk['text'][:1500]}" for chunk in context_chunks)

    def update_summary(self, source_type: str, source_label: str) -> None:
        loaded_at = utc_timestamp()
        self.repository_meta.update(
            {
                "source_type": source_type,
                "source_label": source_label,
                "loaded_at": loaded_at,
            }
        )
        self.summary_state.clear()
        self.summary_state.update(build_repo_summary(self.files, source_type, source_label, loaded_at))

    def store_repository_files(self, files: Dict[str, str], source_type: str, source_label: str) -> Dict[str, Any]:
        if not files:
            raise HTTPException(
                400,
                "No supported source files were found. Upload a ZIP or repo with Python/JS source files.",
            )
        self.files.clear()
        self.files.update(dict(sorted(files.items())))
        self.file_questions.clear()
        self.reload_chunks()
        self.update_summary(source_type, source_label)
        return {
            "files": len(self.files),
            "chunks": len(self.chunks),
            "source_type": source_type,
            "source_label": source_label,
        }

    def get_summary_payload(self) -> Dict[str, Any]:
        return self.summary_state if self.summary_state else dict(DEFAULT_SUMMARY_STATE)

    def get_file_questions(self, path: str) -> List[Dict[str, Any]]:
        return self.file_questions.get(normalize_path(path), [])

    def add_file_question(self, path: str, username: str, question: str) -> Dict[str, Any]:
        normalized = ensure_file_exists(self.files, path)
        self.file_questions.setdefault(normalized, []).append(
            {
                "username": username,
                "question": question,
                "timestamp": utc_timestamp(),
            }
        )
        return {
            "success": True,
            "file": normalized,
            "total_tags": len(self.file_questions[normalized]),
        }

    def clear(self) -> Dict[str, bool]:
        self.files.clear()
        self.chunks.clear()
        self.file_questions.clear()
        self.repository_meta.update(
            {
                "source_type": None,
                "source_label": None,
                "loaded_at": None,
            }
        )
        self.summary_state.clear()
        self.summary_state.update(dict(DEFAULT_SUMMARY_STATE))
        return {"cleared": True}


repository_store = RepositoryStore()
