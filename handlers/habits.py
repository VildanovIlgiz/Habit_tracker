"""
handlers/habits.py

Handles the full habits flow:
  /habits  — show list with today's completion status
  /add     — start FSM to create a new habit
  Inline buttons for mark-done, mark-undone, delete (with confirmation)

FSM states
----------
AddHabit:
  title       → ask for a title
  category    → optional category (skip allowed)
  goal_value  → optional numeric goal (skip allowed)
  goal_unit   → unit for goal (shown only if goal_value provided)
  schedule    → daily / weekdays (inline keyboard)
"""
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards.habit_buttons import (
    CB_BACK_LIST,
    CB_DELETE_ASK,
    CB_DELETE_NO,
    CB_DELETE_YES,
    CB_DONE,
    CB_UNDONE,
    back_to_list_keyboard,
    cancel_keyboard,
    confirm_delete_keyboard,
    habits_list_keyboard,
    schedule_keyboard,
    skip_keyboard,
)
from services.habit_service import HabitService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FSM state group
# ---------------------------------------------------------------------------

class AddHabit(StatesGroup):
    title      = State()
    category   = State()
    goal_value = State()
    goal_unit  = State()
    schedule   = State()


# ---------------------------------------------------------------------------
# Router factory (dependency injection pattern used in this project)
# ---------------------------------------------------------------------------

def get_router(habit_service: HabitService) -> Router:
    router = Router()

    # ------------------------------------------------------------------ #
    #  Helper: render the habit list for a user                           #
    # ------------------------------------------------------------------ #

    async def _send_habits_list(target: Message | CallbackQuery) -> None:
        """Send (or edit) the habit list message."""
        if isinstance(target, CallbackQuery):
            user_id = target.from_user.id
            name    = target.from_user.full_name
            send    = target.message.edit_text
        else:
            user_id = target.from_user.id
            name    = target.from_user.full_name
            send    = target.answer

        habit_service.ensure_user(user_id, name)
        habits     = habit_service.get_habits(user_id)
        today_logs = habit_service.get_today_logs(user_id)

        if not habits:
            await send(
                "📭 You have no active habits yet.\n"
                "Use /add to create your first one!",
            )
            return

        await send(
            "📋 <b>Your habits</b> — tap ☐ to mark done, 🗑 to delete:\n",
            reply_markup=habits_list_keyboard(habits, today_logs),
            parse_mode="HTML",
        )

    # ================================================================== #
    #  /habits  —  show list                                              #
    # ================================================================== #

    @router.message(Command("habits"))
    async def cmd_habits(message: Message) -> None:
        await _send_habits_list(message)

    # ================================================================== #
    #  /add  —  start FSM                                                 #
    # ================================================================== #

    @router.message(Command("add"))
    async def cmd_add(message: Message, state: FSMContext) -> None:
        await state.set_state(AddHabit.title)
        await message.answer(
            "✏️ <b>New habit</b>\n\nWhat do you want to track? Send a short title.\n"
            "<i>Example: Morning run, Read 30 min, Drink water</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

    # -- title step --

    @router.message(AddHabit.title)
    async def fsm_title(message: Message, state: FSMContext) -> None:
        title = (message.text or "").strip()
        if not title:
            await message.answer("Please send a non-empty title.", reply_markup=cancel_keyboard())
            return
        if len(title) > 200:
            await message.answer("Title is too long (max 200 chars).", reply_markup=cancel_keyboard())
            return

        await state.update_data(title=title)
        await state.set_state(AddHabit.category)
        await message.answer(
            "🏷 <b>Category</b> (optional)\n\nSend a category name or skip.",
            reply_markup=skip_keyboard(),
            parse_mode="HTML",
        )

    # -- category step --

    @router.message(AddHabit.category)
    async def fsm_category(message: Message, state: FSMContext) -> None:
        category = (message.text or "").strip() or None
        await state.update_data(category=category)
        await state.set_state(AddHabit.goal_value)
        await message.answer(
            "🔢 <b>Goal amount</b> (optional)\n\n"
            "Does this habit have a numeric goal? E.g. <code>30</code> (minutes), "
            "<code>2</code> (litres). Send a number or skip.",
            reply_markup=skip_keyboard(),
            parse_mode="HTML",
        )

    # -- goal_value step --

    @router.message(AddHabit.goal_value)
    async def fsm_goal_value(message: Message, state: FSMContext) -> None:
        raw = (message.text or "").strip()
        goal: float | None = None
        if raw:
            try:
                goal = float(raw)
                if goal <= 0:
                    raise ValueError
            except ValueError:
                await message.answer(
                    "Please send a positive number, or skip.",
                    reply_markup=skip_keyboard(),
                )
                return

        await state.update_data(goal_value=goal)

        if goal is not None:
            await state.set_state(AddHabit.goal_unit)
            await message.answer(
                "📐 <b>Unit</b>\n\nWhat unit? E.g. <i>min, km, glasses, pages</i>",
                reply_markup=skip_keyboard(),
                parse_mode="HTML",
            )
        else:
            await state.set_state(AddHabit.schedule)
            await message.answer(
                "📅 <b>Schedule</b>\n\nHow often?",
                reply_markup=schedule_keyboard(),
                parse_mode="HTML",
            )

    # -- goal_unit step --

    @router.message(AddHabit.goal_unit)
    async def fsm_goal_unit(message: Message, state: FSMContext) -> None:
        unit = (message.text or "").strip() or None
        await state.update_data(goal_unit=unit)
        await state.set_state(AddHabit.schedule)
        await message.answer(
            "📅 <b>Schedule</b>\n\nHow often?",
            reply_markup=schedule_keyboard(),
            parse_mode="HTML",
        )

    # -- schedule step (answered via inline button callback) --

    @router.callback_query(AddHabit.schedule, F.data.startswith("habit_sched:"))
    async def fsm_schedule(callback: CallbackQuery, state: FSMContext) -> None:
        schedule_type = callback.data.split(":")[1]  # 'daily' or 'weekdays'
        data = await state.get_data()
        await state.clear()

        try:
            habit = habit_service.create_habit(
                telegram_id=callback.from_user.id,
                title=data["title"],
                category=data.get("category"),
                goal_value=data.get("goal_value"),
                goal_unit=data.get("goal_unit"),
                schedule_type=schedule_type,
            )
        except Exception as exc:
            logger.exception("Error creating habit: %s", exc)
            await callback.message.edit_text("❌ Something went wrong. Please try again.")
            await callback.answer()
            return

        schedule_label = "every day" if schedule_type == "daily" else "weekdays only"
        goal_text = ""
        if habit.goal_value and habit.goal_unit:
            goal_text = f"\n🎯 Goal: {habit.goal_value} {habit.goal_unit}"

        await callback.message.edit_text(
            f"✅ <b>Habit added!</b>\n\n"
            f"📌 <b>{habit.title}</b>"
            f"{goal_text}\n"
            f"📅 Schedule: {schedule_label}\n\n"
            f"Use /habits to see your list.",
            parse_mode="HTML",
        )
        await callback.answer("Habit created! 🎉")

    # ================================================================== #
    #  FSM — skip / cancel callbacks                                       #
    # ================================================================== #

    @router.callback_query(StateFilter(AddHabit), F.data == "habit_skip_step")
    async def fsm_skip(callback: CallbackQuery, state: FSMContext) -> None:
        """Move to next step by injecting an empty message text."""
        current = await state.get_state()

        if current == AddHabit.category:
            await state.update_data(category=None)
            await state.set_state(AddHabit.goal_value)
            await callback.message.edit_text(
                "🔢 <b>Goal amount</b> (optional)\n\n"
                "Send a number or skip.",
                reply_markup=skip_keyboard(),
                parse_mode="HTML",
            )
        elif current == AddHabit.goal_value:
            await state.update_data(goal_value=None)
            await state.set_state(AddHabit.schedule)
            await callback.message.edit_text(
                "📅 <b>Schedule</b>\n\nHow often?",
                reply_markup=schedule_keyboard(),
                parse_mode="HTML",
            )
        elif current == AddHabit.goal_unit:
            await state.update_data(goal_unit=None)
            await state.set_state(AddHabit.schedule)
            await callback.message.edit_text(
                "📅 <b>Schedule</b>\n\nHow often?",
                reply_markup=schedule_keyboard(),
                parse_mode="HTML",
            )
        else:
            await callback.answer()
            return

        await callback.answer()

    @router.callback_query(StateFilter(AddHabit), F.data == "habit_cancel_fsm")
    async def fsm_cancel(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.message.edit_text("❌ Habit creation cancelled.")
        await callback.answer()

    # ================================================================== #
    #  Inline list buttons — mark done / undone                           #
    # ================================================================== #

    @router.callback_query(F.data.startswith(f"{CB_DONE}:"))
    async def cb_mark_done(callback: CallbackQuery) -> None:
        habit_id = int(callback.data.split(":")[1])
        try:
            habit_service.mark_done(callback.from_user.id, habit_id)
        except ValueError as e:
            await callback.answer(str(e), show_alert=True)
            return

        await callback.answer("✅ Marked as done!")
        await _send_habits_list(callback)

    @router.callback_query(F.data.startswith(f"{CB_UNDONE}:"))
    async def cb_mark_undone(callback: CallbackQuery) -> None:
        habit_id = int(callback.data.split(":")[1])
        habit_service.mark_undone(callback.from_user.id, habit_id)
        await callback.answer("↩️ Mark removed.")
        await _send_habits_list(callback)

    # ================================================================== #
    #  Inline list buttons — delete with confirmation                     #
    # ================================================================== #

    @router.callback_query(F.data.startswith(f"{CB_DELETE_ASK}:"))
    async def cb_delete_ask(callback: CallbackQuery) -> None:
        habit_id = int(callback.data.split(":")[1])
        # Find the habit title for a nicer confirmation message
        habits = habit_service.get_habits(callback.from_user.id)
        habit  = next((h for h in habits if h.id == habit_id), None)
        title  = habit.title if habit else "this habit"

        await callback.message.edit_text(
            f"🗑 Delete <b>{title}</b>?\n\n"
            "All logs for this habit will be kept, but it won't appear in your list anymore.",
            reply_markup=confirm_delete_keyboard(habit_id),
            parse_mode="HTML",
        )
        await callback.answer()

    @router.callback_query(F.data.startswith(f"{CB_DELETE_YES}:"))
    async def cb_delete_yes(callback: CallbackQuery) -> None:
        habit_id = int(callback.data.split(":")[1])
        deleted  = habit_service.delete_habit(callback.from_user.id, habit_id)
        if deleted:
            await callback.message.edit_text(
                "🗑 Habit deleted.",
                reply_markup=back_to_list_keyboard(),
            )
            await callback.answer("Deleted.")
        else:
            await callback.answer("Habit not found.", show_alert=True)

    @router.callback_query(F.data.startswith(f"{CB_DELETE_NO}:"))
    async def cb_delete_no(callback: CallbackQuery) -> None:
        await callback.answer("Cancelled.")
        await _send_habits_list(callback)

    # ================================================================== #
    #  Back-to-list button                                                #
    # ================================================================== #

    @router.callback_query(F.data == CB_BACK_LIST)
    async def cb_back_list(callback: CallbackQuery) -> None:
        await _send_habits_list(callback)
        await callback.answer()

    return router
