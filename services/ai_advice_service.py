from __future__ import annotations

from integrations.llm_client import LLMClient
from integrations.prompt_builder import build_habit_advice_prompt


class AIAdviceService:
    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    def get_advice(self, habit_title: str) -> str:
        prompt = build_habit_advice_prompt(habit_title)
        return self.client.generate_text(prompt)