from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "Настройки")
async def settings_entry(message: Message) -> None:
    await message.answer(
        "настроечки"
    )