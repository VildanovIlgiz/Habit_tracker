from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "Добавить привычку")
async def add_habit_entry(message: Message) -> None:
    await message.answer(
        "лень"
    )


@router.message(F.text == "Мои привычки")
async def my_habits_entry(message: Message) -> None:
    await message.answer(
        "Пока список привычек не реализован.\n\n"
        "Позже здесь будет вывод привычек пользователя."
    )


@router.message(F.text == "Отметить выполнение")
async def mark_completion_entry(message: Message) -> None:
    await message.answer(
        "Здесь позже появится отметка выполнения привычки."
    )