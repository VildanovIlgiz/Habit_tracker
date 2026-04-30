from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repository import Repository
from database.db import SessionLocal
from keyboards.main_menu import get_main_menu
from services.habit_service import HabitService
from utils.helpers import build_welcome_text

logger = logging.getLogger(__name__)


def get_menu_router(habit_service: HabitService) -> Router:
    r = Router()

    @r.message(F.text == "Добавить привычку")
    async def btn_add_habit(message: Message) -> None:
        habit_service.ensure_user(message.from_user.id, message.from_user.full_name)
        from handlers.habits import AddHabit
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.state import State, StatesGroup
        from keyboards.habit_buttons import cancel_keyboard

        await message.answer(
            "✏️ <b>Новая привычка</b>\n\nЧто хочешь отслеживать? Пришли краткое название.\n"
            "<i>Пример: Утренняя пробежка, Чтение 30 мин, Вода</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

    @r.message(F.text == "Мои привычки")
    async def btn_my_habits(message: Message) -> None:
        habit_service.ensure_user(message.from_user.id, message.from_user.full_name)
        habits = habit_service.get_habits(message.from_user.id)
        today_logs = habit_service.get_today_logs(message.from_user.id)

        if not habits:
            await message.answer(
                "📭 У тебя пока нет активных привычек.\nНажми «Добавить привычку», чтобы создать первую!"
            )
            return

        from keyboards.habit_buttons import habits_list_keyboard
        await message.answer(
            "📋 <b>Твои привычки</b> — нажми ☐ чтобы отметить, 🗑 чтобы удалить:",
            reply_markup=habits_list_keyboard(habits, today_logs),
            parse_mode="HTML",
        )

    @r.message(F.text == "Отметить выполнение")
    async def btn_mark_done(message: Message) -> None:
        habit_service.ensure_user(message.from_user.id, message.from_user.full_name)
        habits = habit_service.get_habits(message.from_user.id)
        today_logs = habit_service.get_today_logs(message.from_user.id)

        if not habits:
            await message.answer(
                "📭 У тебя пока нет активных привычек.\nСначала добавь привычку!"
            )
            return

        from keyboards.habit_buttons import habits_list_keyboard
        await message.answer(
            "✅ Отметь привычки, которые выполнил сегодня:",
            reply_markup=habits_list_keyboard(habits, today_logs),
            parse_mode="HTML",
        )

    return r
