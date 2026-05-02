from __future__ import annotations

import logging
import os

from config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.openai_api_key
        self._client = None

        if self._api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI client: %s. Will use fallback.", e)
                self._client = None

    def generate_text(self, prompt: str) -> str:
        if self._client is None:
            return self._fallback(prompt)

        try:
            response = self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты — полезный ассистент по формированию привычек. Отвечай кратко и по делу на русском языке."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenAI API error: %s. Using fallback.", e)
            return self._fallback(prompt)

    def _fallback(self, prompt: str) -> str:
        return (
            "💡 Совет дня: начинай с малого — даже 5 минут практики лучше, "
            "чем ничего. Главное — регулярность, а не интенсивность!"
        )
