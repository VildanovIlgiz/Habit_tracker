from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.main_menu import get_main_menu
from utils.helpers import build_welcome_text

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    first_name = message.from_user.first_name if message.from_user else None

    await message.answer(
        build_welcome_text(first_name),
        reply_markup=get_main_menu(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer(
        "Главное меню открыто.",
        reply_markup=get_main_menu(),
    )
