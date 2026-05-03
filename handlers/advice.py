from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import Repository
from services.ai_advice_service import AIAdviceService
from services.habit_service import HabitService

logger = logging.getLogger(__name__)


def get_router() -> Router:
    r = Router()
    advice_svc = AIAdviceService()

    @r.message(F.text == "Совет")
    @r.message(Command("advice"))
    async def advice_entry(message: Message) -> None:
        await message.answer("🧠 Дай мне секунду, подумаю...")

        habit_title = None

        try:
            from database.repository import Repository
            from database.db import SessionLocal
            repo = Repository(SessionLocal())
            user = repo.get_user_by_telegram_id(message.from_user.id)
            if user:
                habits = repo.get_habits_by_user_id(user.id)
                if habits:
                    import random
                    habit_title = random.choice(habits).title
                    user_style = user.communication_style
                else:
                    user_style = "neutral"
                repo.close()
            else:
                user_style = "neutral"
        except Exception:
            user_style = "neutral"

        if habit_title:
            advice_text = advice_svc.get_advice(habit_title, user_style)
            await message.answer(
                f"💡 Совет для привычки «<b>{habit_title}</b>»:\n\n{advice_text}",
                parse_mode="HTML",
            )
        else:
            advice_text = advice_svc.get_advice("формирование полезных привычек", user_style)
            await message.answer(
                f"💡 Общий совет:\n\n{advice_text}",
                parse_mode="HTML",
            )

    return r
