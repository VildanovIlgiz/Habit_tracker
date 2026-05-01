from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import Repository
from keyboards.main_menu import get_main_menu
from services.habit_service import HabitService
from services.stats_service import StatsService

logger = logging.getLogger(__name__)

router = Router()


def get_router(habit_service: HabitService) -> Router:
    r = Router()
    stats_svc = StatsService(habit_service._repo)

    @r.message(F.text == "Статистика")
    @r.message(Command("stats"))
    async def statistics_entry(message: Message) -> None:
        habit_service.ensure_user(message.from_user.id, message.from_user.full_name)
        summary = stats_svc.get_summary(message.from_user.id)

        if summary["total_habits"] == 0:
            await message.answer(
                "📊 У тебя пока нет активных привычек.\n"
                "Добавь первую через /add или кнопку «Добавить привычку»!"
            )
            return

        text = (
            f"📊 <b>Твоя статистика</b>\n\n"
            f"📌 Активных привычек: <b>{summary['total_habits']}</b>\n"
            f"📈 Выполнение за неделю: <b>{summary['completion_rate']}%</b>\n"
            f"🔥 Текущая серия: <b>{summary['current_streak']} дн.</b>\n"
            f"✅ Выполнено сегодня: <b>{summary['completed_today']}</b>\n"
            f"📅 Выполнено за неделю: <b>{summary['completed_this_week']}</b>"
        )
        if summary["best_habit"]:
            text += f"\n🏆 Лучшая привычка: <b>{summary['best_habit']}</b>"

        await message.answer(text, parse_mode="HTML")

    return r
