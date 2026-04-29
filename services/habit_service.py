"""
services/habit_service.py

Business logic for habit management.
All database access goes through Repository – handlers never touch the DB directly.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from database.repository import Repository


# ---------------------------------------------------------------------------
# Lightweight DTOs (no ORM objects leak into handlers)
# ---------------------------------------------------------------------------

@dataclass
class HabitDTO:
    id: int
    title: str
    category: str | None
    goal_value: float | None
    goal_unit: str | None
    schedule_type: str
    is_active: bool
    created_at: datetime


@dataclass
class LogDTO:
    habit_id: int
    date: date
    status: bool
    value_done: float | None


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class HabitService:
    def __init__(self, repository: Repository, *, achievement_service=None) -> None:
        self._repo = repository
        self._achievements = achievement_service

    # ------------------------------------------------------------------
    # User bootstrap
    # ------------------------------------------------------------------

    def ensure_user(self, telegram_id: int, name: str) -> None:
        """Create user row on first contact if it does not exist yet."""
        if not self._repo.get_user_by_telegram_id(telegram_id):
            self._repo.create_user(telegram_id=telegram_id, name=name)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_habit(
        self,
        telegram_id: int,
        title: str,
        *,
        category: str | None = None,
        goal_value: float | None = None,
        goal_unit: str | None = None,
        schedule_type: str = "daily",
    ) -> HabitDTO:
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            raise ValueError(f"User {telegram_id} not found – call ensure_user first.")

        habit = self._repo.create_habit(
            user_id=user.id,
            title=title.strip(),
            category=category,
            goal_value=goal_value,
            goal_unit=goal_unit,
            schedule_type=schedule_type,
        )
        return self._to_dto(habit)

    def get_habits(self, telegram_id: int) -> list[HabitDTO]:
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            return []
        habits = self._repo.get_habits_by_user_id(user.id)
        return [self._to_dto(h) for h in habits if h.is_active]

    def delete_habit(self, telegram_id: int, habit_id: int) -> bool:
        """
        Soft-delete a habit (sets is_active=False).
        Returns True if the habit belonged to this user and was deleted.
        """
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            return False
        habit = self._repo.get_habit_by_id(habit_id)
        if habit is None or habit.user_id != user.id:
            return False
        self._repo.deactivate_habit(habit_id)
        return True

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------

    def mark_done(
        self,
        telegram_id: int,
        habit_id: int,
        *,
        value_done: float | None = None,
        log_date: date | None = None,
    ) -> LogDTO:
        """
        Mark a habit as completed for a given date (default: today).
        If a log already exists for that date it is updated (idempotent).
        """
        log_date = log_date or date.today()
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            raise ValueError("User not found.")
        habit = self._repo.get_habit_by_id(habit_id)
        if habit is None or habit.user_id != user.id:
            raise ValueError("Habit not found or does not belong to user.")

        log = self._repo.upsert_habit_log(
            habit_id=habit_id,
            log_date=log_date,
            status=True,
            value_done=value_done,
        )

        if self._achievements:
            self._achievements.check_and_award(user.id, habit_id)

        return LogDTO(
            habit_id=log.habit_id,
            date=log.date,
            status=log.status,
            value_done=log.value_done,
        )

    def mark_undone(
        self,
        telegram_id: int,
        habit_id: int,
        *,
        log_date: date | None = None,
    ) -> None:
        """Remove today's completion mark (or any given date's)."""
        log_date = log_date or date.today()
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            return
        habit = self._repo.get_habit_by_id(habit_id)
        if habit is None or habit.user_id != user.id:
            return
        self._repo.upsert_habit_log(
            habit_id=habit_id,
            log_date=log_date,
            status=False,
            value_done=None,
        )

    def get_today_logs(self, telegram_id: int) -> dict[int, LogDTO]:
        """Return {habit_id: LogDTO} for all of today's logs for this user."""
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            return {}
        logs = self._repo.get_logs_for_user_on_date(user.id, date.today())
        return {
            log.habit_id: LogDTO(
                habit_id=log.habit_id,
                date=log.date,
                status=log.status,
                value_done=log.value_done,
            )
            for log in logs
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dto(habit) -> HabitDTO:
        return HabitDTO(
            id=habit.id,
            title=habit.title,
            category=habit.category,
            goal_value=habit.goal_value,
            goal_unit=habit.goal_unit,
            schedule_type=habit.schedule_type,
            is_active=habit.is_active,
            created_at=habit.created_at,
        )
