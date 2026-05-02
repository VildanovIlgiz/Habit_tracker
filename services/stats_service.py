from __future__ import annotations


class StatsService:
    def get_summary(self, user_id: int) -> dict[str, int | float | str | None]:
        return {
            "completion_rate": 0.0,
            "current_streak": 0,
            "completed_this_week": 0,
            "best_habit": None,
        }