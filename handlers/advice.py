from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "Совет")
async def advice_entry(message: Message) -> None:
    await message.answer(
        "не реализовано"
    )