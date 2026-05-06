"""
handlers/settings.py

User settings flow:
  /settings  — show current settings with inline edit buttons
  Inline buttons to change:
    • ⏰ Reminder time   (HH:MM, 24-hour)
    • 🗣 Communication style  (friendly / strict / neutral)

FSM states
----------
EditSettings:
  reminder_time  — waiting for HH:MM input
"""
from __future__ import annotations

import logging
import re

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.habit_service import HabitService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STYLES: dict[str, str] = {
    "friendly": "😊 Friendly",
    "strict":   "💪 Strict",
    "neutral":  "😐 Neutral",
}

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

# Callback-data tokens
CB_EDIT_TIME   = "settings_edit_time"
CB_EDIT_STYLE  = "settings_edit_style"
CB_STYLE_SET   = "settings_style_set"   # settings_style_set:<key>
CB_CANCEL      = "settings_cancel"


# ---------------------------------------------------------------------------
# FSM
# ---------------------------------------------------------------------------

class EditSettings(StatesGroup):
    reminder_time = State()


# ---------------------------------------------------------------------------
# Keyboards
# ---------------------------------------------------------------------------

def _settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏰ Change reminder time",     callback_data=CB_EDIT_TIME),
    )
    builder.row(
        InlineKeyboardButton(text="🗣 Change communication style", callback_data=CB_EDIT_STYLE),
    )
    return builder.as_markup()


def _style_keyboard(current: str | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in STYLES.items():
        tick = " ✅" if key == current else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{label}{tick}",
                callback_data=f"{CB_STYLE_SET}:{key}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data=CB_CANCEL),
    )
    return builder.as_markup()


def _cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Cancel", callback_data=CB_CANCEL),
    )
    return builder.as_markup()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _settings_text(user) -> str:
    reminder = user.reminder_time or "not set"
    style_key = user.communication_style or "neutral"
    style_label = STYLES.get(style_key, style_key)
    return (
        "⚙️ <b>Settings</b>\n\n"
        f"⏰ <b>Reminder time:</b> {reminder}\n"
        f"🗣 <b>Communication style:</b> {style_label}"
    )


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------

def get_router(habit_service: HabitService) -> Router:
    router = Router()

    # ------------------------------------------------------------------
    # /settings — show current settings
    # ------------------------------------------------------------------

    @router.message(Command("settings"))
    async def cmd_settings(message: Message) -> None:
        habit_service.ensure_user(message.from_user.id, message.from_user.full_name)
        user = habit_service._repo.get_user_by_telegram_id(message.from_user.id)
        await message.answer(
            _settings_text(user),
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )

    # ------------------------------------------------------------------
    # Edit reminder time — start FSM
    # ------------------------------------------------------------------

    @router.callback_query(F.data == CB_EDIT_TIME)
    async def cb_edit_time(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(EditSettings.reminder_time)
        await callback.message.edit_text(
            "⏰ <b>Set reminder time</b>\n\n"
            "Send the time in <b>HH:MM</b> format (24-hour).\n"
            "<i>Example: 08:30, 20:00</i>",
            reply_markup=_cancel_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()

    @router.message(EditSettings.reminder_time)
    async def fsm_reminder_time(message: Message, state: FSMContext) -> None:
        raw = (message.text or "").strip()
        if not _TIME_RE.match(raw):
            await message.answer(
                "❌ Invalid format. Please send time as <b>HH:MM</b>, e.g. <code>08:30</code>.",
                reply_markup=_cancel_keyboard(),
                parse_mode="HTML",
            )
            return

        habit_service._repo.update_user_settings(
            telegram_id=message.from_user.id,
            reminder_time=raw,
        )
        await state.clear()

        user = habit_service._repo.get_user_by_telegram_id(message.from_user.id)
        await message.answer(
            f"✅ Reminder time set to <b>{raw}</b>.\n\n" + _settings_text(user),
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )

    # ------------------------------------------------------------------
    # Edit communication style — show style picker
    # ------------------------------------------------------------------

    @router.callback_query(F.data == CB_EDIT_STYLE)
    async def cb_edit_style(callback: CallbackQuery) -> None:
        user = habit_service._repo.get_user_by_telegram_id(callback.from_user.id)
        current = user.communication_style if user else None
        await callback.message.edit_text(
            "🗣 <b>Communication style</b>\n\n"
            "Choose how you'd like the bot to talk to you:",
            reply_markup=_style_keyboard(current),
            parse_mode="HTML",
        )
        await callback.answer()

    @router.callback_query(F.data.startswith(f"{CB_STYLE_SET}:"))
    async def cb_style_set(callback: CallbackQuery) -> None:
        style_key = callback.data.split(":")[1]
        if style_key not in STYLES:
            await callback.answer("Unknown style.", show_alert=True)
            return

        habit_service._repo.update_user_settings(
            telegram_id=callback.from_user.id,
            communication_style=style_key,
        )

        user = habit_service._repo.get_user_by_telegram_id(callback.from_user.id)
        await callback.message.edit_text(
            f"✅ Style set to <b>{STYLES[style_key]}</b>.\n\n" + _settings_text(user),
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer(f"Style: {STYLES[style_key]}")

    # ------------------------------------------------------------------
    # Cancel FSM / close picker
    # ------------------------------------------------------------------

    @router.callback_query(StateFilter(EditSettings), F.data == CB_CANCEL)
    async def cb_cancel_fsm(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        user = habit_service._repo.get_user_by_telegram_id(callback.from_user.id)
        await callback.message.edit_text(
            _settings_text(user),
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer("Cancelled.")

    @router.callback_query(F.data == CB_CANCEL)
    async def cb_cancel_no_state(callback: CallbackQuery) -> None:
        user = habit_service._repo.get_user_by_telegram_id(callback.from_user.id)
        await callback.message.edit_text(
            _settings_text(user),
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()

    return router
