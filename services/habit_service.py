from __future__ import annotations

from models.habit import Habit


class HabitService:
    def list_habits(self, user_id: int) -> list[Habit]:
        return []

    def create_habit(self, user_id: int, title: str) -> Habit:
        return Habit(
            id=None,
            user_id=user_id,
            title=title,
        )

    def delete_habit(self, user_id: int, habit_id: int) -> bool:
        return False

    def mark_completed(
        self,
        user_id: int,
        habit_id: int,
        value_done: float | None = None,
    ) -> bool:
        return False