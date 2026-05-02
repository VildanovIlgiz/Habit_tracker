from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_habit_action_buttons(habit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Сделано!",
                    callback_data=f"habit:done:{habit_id}",
                ),
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"habit:delete:{habit_id}",
                ),
            ]
        ]
    )