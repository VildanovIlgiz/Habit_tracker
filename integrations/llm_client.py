from __future__ import annotations

import logging
import random

from config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.openai_api_key
        self._client = None
        self._initialized = False

        self._try_init_client()

    def _try_init_client(self) -> None:
        if not self._api_key:
            logger.info("OPENAI_API_KEY not set — using fallback mode.")
            self._initialized = True
            return
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key)
            self._initialized = True
            logger.info("OpenAI client initialized successfully.")
        except ImportError:
            logger.warning("openai package not installed. Using fallback mode.")
            self._client = None
            self._initialized = True
        except Exception as e:
            logger.warning("Failed to initialize OpenAI client: %s. Using fallback.", e)
            self._client = None
            self._initialized = True

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
            content = response.choices[0].message.content
            if content and content.strip():
                return content.strip()
            logger.warning("Empty response from OpenAI. Using fallback.")
            return self._fallback(prompt)
        except Exception as e:
            logger.error("OpenAI API error: %s. Using fallback.", e)
            return self._fallback(prompt)

    def _fallback(self, prompt: str) -> str:
        tips = [
            "💡 Совет: начинай с малого — даже 5 минут практики лучше, чем ничего. Главное — регулярность!",
            "💡 Совет: привяжи привычку к уже существующему действию — например, «после завтрака сделаю зарядку».",
            "💡 Совет: отслеживай прогресс — когда видишь свои результаты, мотивация растёт!",
            "💡 Совет: не ругай себя за пропуски — просто продолжай с того места, где остановился.",
            "💡 Совет: найди напарника — вместе привычки формируются легче!",
        ]
        return random.choice(tips)
