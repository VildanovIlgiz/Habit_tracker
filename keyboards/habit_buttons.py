from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.habit_service import HabitDTO, LogDTO


# ---------------------------------------------------------------------------
# Callback-data prefixes  (keep in sync with handlers/habits.py)
# ---------------------------------------------------------------------------
CB_DONE        = "habit_done"       # habit_done:<habit_id>
CB_UNDONE      = "habit_undone"     # habit_undone:<habit_id>
CB_DELETE_ASK  = "habit_del_ask"    # habit_del_ask:<habit_id>
CB_DELETE_YES  = "habit_del_yes"    # habit_del_yes:<habit_id>
CB_DELETE_NO   = "habit_del_no"     # habit_del_no:<habit_id>
CB_BACK_LIST   = "habit_back_list"  # habit_back_list  (no id)
CB_FILTER_CAT  = "habit_filter_cat" # habit_filter_cat:<category>


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cb(prefix: str, habit_id: int | None = None) -> str:
    return f"{prefix}:{habit_id}" if habit_id is not None else prefix


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------

def habits_list_keyboard(
    habits: list[HabitDTO],
    today_logs: dict[int, LogDTO],
) -> InlineKeyboardMarkup:
    """
    One row per habit:
      [✅ / ☐]  Habit title   [🗑]
    The tick/cross button toggles completion for today.
    """
    builder = InlineKeyboardBuilder()
    for habit in habits:
        log = today_logs.get(habit.id)
        done = bool(log and log.status)

        tick_label  = "✅" if done else "☐"
        tick_action = CB_UNDONE if done else CB_DONE

        title_display = habit.title
        if habit.category:
            title_display = f"[{habit.category}] {title_display}"
        if habit.goal_value and habit.goal_unit:
            title_display += f"  ({habit.goal_value} {habit.goal_unit})"

        builder.row(
            InlineKeyboardButton(
                text=tick_label,
                callback_data=_cb(tick_action, habit.id),
            ),
            InlineKeyboardButton(
                text=title_display,
                callback_data=_cb(CB_DONE if not done else CB_UNDONE, habit.id),
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=_cb(CB_DELETE_ASK, habit.id),
            ),
        )

    return builder.as_markup()


def category_filter_keyboard(habits: list[HabitDTO]) -> InlineKeyboardMarkup:
    categories = sorted({h.category for h in habits if h.category})
    if not categories:
        return habits_list_keyboard(habits, {})

    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.row(
            InlineKeyboardButton(text=cat, callback_data=f"{CB_FILTER_CAT}:{cat}"),
        )
    builder.row(
        InlineKeyboardButton(text="📋 Все привычки", callback_data=CB_BACK_LIST),
    )
    return builder.as_markup()


def confirm_delete_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Yes / Cancel confirmation before permanent delete."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Да, удалить", callback_data=_cb(CB_DELETE_YES, habit_id)),
        InlineKeyboardButton(text="Отмена",       callback_data=_cb(CB_DELETE_NO,  habit_id)),
    )
    return builder.as_markup()


def back_to_list_keyboard() -> InlineKeyboardMarkup:
    """Single 'Back to list' button used after certain actions."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Обратно к привычкам", callback_data=CB_BACK_LIST)
    )
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Shown during FSM input to let the user abort."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Отменить", callback_data="habit_cancel_fsm")
    )
    return builder.as_markup()


def skip_keyboard() -> InlineKeyboardMarkup:
    """Shown for optional FSM steps."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Пропустить", callback_data="habit_skip_step"),
        InlineKeyboardButton(text="Отменить", callback_data="habit_cancel_fsm"),
    )
    return builder.as_markup()


def schedule_keyboard() -> InlineKeyboardMarkup:
    """Quick-pick for schedule type during habit creation."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Каждый день",    callback_data="habit_sched:daily"),
        InlineKeyboardButton(text="По будням", callback_data="habit_sched:weekdays"),
    )
    builder.row(
        InlineKeyboardButton(text="Отменить", callback_data="habit_cancel_fsm"),
    )
    return builder.as_markup()
