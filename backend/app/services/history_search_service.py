"""Service for searching answers in tagged questions history."""

import json
import logging
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from backend.app.core.config import get_settings
from backend.app.services.ai_service import ai_service
from backend.app.storage.note_store import NoteStore

logger = logging.getLogger(__name__)


class HistorySearchService:
    """Search for relevant answers in question/reply history."""

    def __init__(self) -> None:
        self.store = NoteStore(get_settings().auth_db_path)
        self.min_candidate_score = 0.18
        self.related_threshold = 0.45
        self.best_match_threshold = 0.68
        self.max_rerank_candidates = 8
        self.stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "but", "by", "do", "does", "for", "from",
            "how", "i", "in", "is", "it", "me", "of", "on", "or", "so", "tell", "that", "the",
            "this", "to", "what", "when", "where", "which", "who", "why", "with", "you", "your",
        }

    def search_related_answers(
        self,
        repository_key: str,
        prompt: str,
        selected_file: Optional[str] = None,
        scope: str = "REPOSITORY",
    ) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Search for related answers in question history.

        Args:
            repository_key: Repository identifier
            prompt: User's question/prompt
            selected_file: File path for file-scoped searches
            scope: "FILE" or "REPOSITORY"

        Returns:
            Tuple of (best_match, related_questions)
            - best_match: Most relevant historical Q&A, or None
            - related_questions: List of related questions with replies
        """
        # Get questions relevant to the query
        if scope == "FILE" and selected_file:
            questions = self.store.list_questions(repository_key, path=selected_file, scope="FILE")
        elif scope == "FILE":
            # File scope but no file - return empty
            return None, []
        else:
            # Repository scope - get all questions
            questions = self.store.list_questions(repository_key, scope="ALL")

        if not questions:
            return None, []

        # Calculate fast local scores first, then optionally rerank semantically with the LLM.
        scored_questions = []
        for question in questions:
            similarity = self._calculate_text_similarity(prompt, question["question"])
            if similarity >= self.min_candidate_score:
                scored_questions.append((similarity, question))

        if not scored_questions:
            # If lexical matching is too weak, still give the LLM a few candidates to reason about.
            fallback_candidates = []
            for question in questions:
                similarity = self._calculate_fallback_similarity(prompt, question["question"])
                fallback_candidates.append((similarity, question))
            scored_questions = fallback_candidates

        # Sort by local similarity before semantic reranking.
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        scored_questions = scored_questions[: self.max_rerank_candidates]

        reranked = self._rerank_with_llm(prompt, scored_questions)
        if reranked:
            score_map = {item["question_id"]: item["semantic_score"] for item in reranked}
            reasoning_map = {item["question_id"]: item.get("reason", "") for item in reranked}
            rescored_questions = []
            for lexical_score, question in scored_questions:
                semantic_score = score_map.get(question["id"])
                final_score = self._combine_scores(lexical_score, semantic_score)
                rescored_questions.append((final_score, lexical_score, semantic_score, question))
            rescored_questions.sort(key=lambda x: x[0], reverse=True)
        else:
            rescored_questions = [
                (lexical_score, lexical_score, None, question) for lexical_score, question in scored_questions
            ]
            reasoning_map = {}

        # Process results
        best_match = None
        related_questions = []

        for idx, (similarity, lexical_score, semantic_score, question) in enumerate(rescored_questions):
            # Get replies for this question
            replies = self.store.list_replies(question["id"])

            question_data = {
                "question_id": question["id"],
                "question": question["question"],
                "username": question["username"],
                "created_at": question["created_at"],
                "scope": question["scope"],
                "path": question.get("path"),
                "replies": replies,
                "similarity": similarity,
                "lexical_similarity": lexical_score,
                "semantic_similarity": semantic_score,
                "match_reason": reasoning_map.get(question["id"], ""),
            }

            if idx == 0 and similarity >= self.best_match_threshold:
                # Best match with high confidence, including paraphrased questions.
                best_match = question_data
            elif similarity >= self.related_threshold:
                # Related questions with meaningful overlap.
                related_questions.append(question_data)

            # Limit related questions to top 3
            if len(related_questions) >= 3:
                break

        return best_match, related_questions

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate local similarity using token overlap plus phrase similarity."""
        words1 = self._tokenize(text1)
        words2 = self._tokenize(text2)

        if not words1 or not words2:
            return self._calculate_fallback_similarity(text1, text2)

        intersection = words1 & words2
        union = words1 | words2
        jaccard = len(intersection) / len(union) if union else 0.0
        overlap = len(intersection) / max(1, min(len(words1), len(words2)))
        phrase_ratio = SequenceMatcher(None, self._normalize_phrase(text1), self._normalize_phrase(text2)).ratio()
        return max(jaccard * 0.45 + overlap * 0.35 + phrase_ratio * 0.20, overlap * 0.7)

    def _calculate_fallback_similarity(self, text1: str, text2: str) -> float:
        return SequenceMatcher(None, self._normalize_phrase(text1), self._normalize_phrase(text2)).ratio()

    def _normalize_phrase(self, text: str) -> str:
        return " ".join(sorted(self._tokenize(text)))

    def _tokenize(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-z0-9_]+", text.lower())
        normalized = set()
        for token in tokens:
            if token in self.stopwords:
                continue
            normalized.add(self._normalize_token(token))
        return normalized

    def _normalize_token(self, token: str) -> str:
        if token.endswith("ication"):
            return token[:-7] + "y"
        if token.endswith("ing") and len(token) > 5:
            return token[:-3]
        if token.endswith("ed") and len(token) > 4:
            return token[:-2]
        if token.endswith("es") and len(token) > 4:
            return token[:-2]
        if token.endswith("s") and len(token) > 3:
            return token[:-1]
        return token

    def _combine_scores(self, lexical_score: float, semantic_score: Optional[float]) -> float:
        if semantic_score is None:
            return lexical_score
        return max(lexical_score * 0.35 + semantic_score * 0.65, semantic_score)

    def _rerank_with_llm(
        self, prompt: str, scored_questions: List[tuple[float, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        if not scored_questions:
            return []

        candidate_lines = []
        for lexical_score, question in scored_questions:
            replies = self.store.list_replies(question["id"])
            reply_preview = " | ".join(reply["content"].strip().replace("\n", " ")[:180] for reply in replies[:2])
            candidate_lines.append(
                {
                    "question_id": question["id"],
                    "question": question["question"],
                    "scope": question["scope"],
                    "path": question.get("path"),
                    "lexical_score": round(lexical_score, 3),
                    "reply_preview": reply_preview,
                }
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You rank whether past team questions are semantically the same as a user's new question. "
                    "Consider paraphrases, abbreviations, synonyms, and intent. "
                    "Return JSON only in the shape "
                    '{"matches":[{"question_id":123,"semantic_score":0.91,"reason":"short reason"}]}. '
                    "Use semantic_score between 0 and 1. High scores mean the historical discussion likely answers the new question."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_question": prompt,
                        "candidates": candidate_lines,
                    },
                    ensure_ascii=True,
                ),
            },
        ]

        response_text = ai_service.call_llm(messages)
        data = self._extract_json_object(response_text)
        if not data:
            return []

        matches = data.get("matches", [])
        valid_matches = []
        for item in matches:
            question_id = item.get("question_id")
            semantic_score = item.get("semantic_score")
            if not isinstance(question_id, int):
                continue
            try:
                score = float(semantic_score)
            except (TypeError, ValueError):
                continue
            valid_matches.append(
                {
                    "question_id": question_id,
                    "semantic_score": max(0.0, min(1.0, score)),
                    "reason": str(item.get("reason", "")).strip()[:240],
                }
            )

        return valid_matches

    def _extract_json_object(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {}

        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            logger.warning("History semantic reranker returned non-JSON output")
            return {}

        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            logger.warning("History semantic reranker JSON parsing failed")
            return {}


history_search_service = HistorySearchService()
