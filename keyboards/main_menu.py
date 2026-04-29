from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Добавить привычку"), KeyboardButton(text="Мои привычки")],
        [KeyboardButton(text="Отметить выполнение"), KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Совет"), KeyboardButton(text="Настройки")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )