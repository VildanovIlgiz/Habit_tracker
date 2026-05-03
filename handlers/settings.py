from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repository import Repository
from keyboards.main_menu import get_main_menu
from utils.validators import validate_time_string

logger = logging.getLogger(__name__)


class SettingsFSM(StatesGroup):
    main = State()
    reminder_time = State()
    communication_style = State()


def get_router(repo: Repository) -> Router:
    r = Router()

    def _settings_keyboard() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="⏰ Время напоминания", callback_data="set_reminder"))
        builder.row(InlineKeyboardButton(text="💬 Стиль общения", callback_data="set_style"))
        builder.row(InlineKeyboardButton(text="🏆 Достижения", callback_data="show_achievements"))
        builder.row(InlineKeyboardButton(text="🔙 Закрыть", callback_data="settings_close"))
        return builder.as_markup()

    def _style_keyboard() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Нейтральный", callback_data="style:neutral"))
        builder.row(InlineKeyboardButton(text="😊 Дружелюбный", callback_data="style:friendly"))
        builder.row(InlineKeyboardButton(text="💪 Строгий", callback_data="style:strict"))
        builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="settings_back"))
        return builder.as_markup()

    @r.message(F.text == "Настройки")
    async def settings_entry(message: Message) -> None:
        user = repo.get_user_by_telegram_id(message.from_user.id)
        if user is None:
            user = repo.create_user(message.from_user.id, message.from_user.full_name)

        style_names = {"neutral": "Нейтральный", "friendly": "Дружелюбный", "strict": "Строгий"}
        style_display = style_names.get(user.communication_style, user.communication_style)

        await message.answer(
            f"⚙️ <b>Настройки</b>\n\n"
            f"⏰ Напоминание в: <b>{user.reminder_time}</b>\n"
            f"💬 Стиль: <b>{style_display}</b>",
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )

    @r.callback_query(F.data == "set_reminder")
    async def cb_set_reminder(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(SettingsFSM.reminder_time)
        await callback.message.edit_text(
            "⏰ Введи время напоминания в формате <b>ЧЧ:ММ</b>\n"
            "<i>Например: 20:00</i>",
            parse_mode="HTML",
        )
        await callback.answer()

    @r.message(SettingsFSM.reminder_time)
    async def fsm_reminder_time(message: Message, state: FSMContext) -> None:
        time_str = (message.text or "").strip()
        if not validate_time_string(time_str):
            await message.answer(
                "❌ Неверный формат. Введи время в формате ЧЧ:ММ (например, 20:00)."
            )
            return

        user = repo.update_user_settings(message.from_user.id, reminder_time=time_str)
        await state.clear()
        await message.answer(
            f"✅ Время напоминания установлено: <b>{time_str}</b>",
            reply_markup=get_main_menu(),
            parse_mode="HTML",
        )

    @r.callback_query(F.data == "set_style")
    async def cb_set_style(callback: CallbackQuery) -> None:
        await callback.message.edit_text(
            "💬 Выбери стиль общения бота:",
            reply_markup=_style_keyboard(),
        )
        await callback.answer()

    @r.callback_query(F.data.startswith("style:"))
    async def cb_choose_style(callback: CallbackQuery) -> None:
        style = callback.data.split(":")[1]
        style_names = {"neutral": "Нейтральный", "friendly": "Дружелюбный", "strict": "Строгий"}

        user = repo.update_user_settings(callback.from_user.id, communication_style=style)
        await callback.message.edit_text(
            f"✅ Стиль общения: <b>{style_names.get(style, style)}</b>",
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()

    @r.callback_query(F.data == "show_achievements")
    async def cb_show_achievements(callback: CallbackQuery) -> None:
        from services.achievement_service import AchievementService
        ach_svc = AchievementService(repo)
        user = repo.get_user_by_telegram_id(callback.from_user.id)
        if user is None:
            await callback.answer("Сначала начни работу с ботом!", show_alert=True)
            return

        achievements = ach_svc.get_earned_achievements(user.id)
        if not achievements:
            await callback.message.edit_text(
                "🏆 У тебя пока нет достижений.\n"
                "Отмечай привычки каждый день, чтобы заработать первые!",
                reply_markup=_settings_keyboard(),
            )
        else:
            lines = ["🏆 <b>Твои достижения</b>\n"]
            for ach in achievements:
                lines.append(f"  🎖 {ach['title']} — {ach['description']}")
            await callback.message.edit_text(
                "\n".join(lines),
                reply_markup=_settings_keyboard(),
                parse_mode="HTML",
            )
        await callback.answer()

    @r.callback_query(F.data == "settings_back")
    async def cb_settings_back(callback: CallbackQuery) -> None:
        user = repo.get_user_by_telegram_id(callback.from_user.id)
        style_names = {"neutral": "Нейтральный", "friendly": "Дружелюбный", "strict": "Строгий"}
        style_display = style_names.get(user.communication_style, user.communication_style) if user else "Нейтральный"

        await callback.message.edit_text(
            f"⚙️ <b>Настройки</b>\n\n"
            f"⏰ Напоминание в: <b>{user.reminder_time if user else '20:00'}</b>\n"
            f"💬 Стиль: <b>{style_display}</b>",
            reply_markup=_settings_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()

    @r.callback_query(F.data == "settings_close")
    async def cb_settings_close(callback: CallbackQuery) -> None:
        await callback.message.edit_text("Настройки закрыты.")
        await callback.answer()

    return r
