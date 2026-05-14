import logging
from typing import Dict, List

import requests

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def call_llm(self, messages: List[Dict[str, str]]) -> str:
        if not self.settings.llm_api_key:
            return "LLM is not configured. Set LLM_API_KEY to enable repository Q&A and summaries."

        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.llm_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 700,
        }

        try:
            response = requests.post(
                self.settings.llm_api_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
        except requests.RequestException as exc:
            logger.exception("LLM request failed")
            return f"LLM request failed: {exc}"

        if response.status_code != 200:
            logger.warning("LLM API failed with status %s", response.status_code)
            return f"LLM API failed: {response.text}"

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            logger.exception("Unexpected LLM response format")
            return "LLM returned an unexpected response format."


ai_service = AIService()
