from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

router = Router()

BUTTON_RESPONSES = {
    "Добавить привычку": "заглушка",
    "Мои привычки": "заглушка",
    "Отметить выполнение": "заглушка",
    "Статистика": "заглушка",
    "Совет": "заглушка",
    "Настройки": "заглушка",
}


@router.message(F.text.in_(BUTTON_RESPONSES))
async def handle_menu_buttons(message: Message) -> None:
    await message.answer(BUTTON_RESPONSES[message.text])
