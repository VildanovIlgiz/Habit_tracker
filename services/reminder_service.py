from __future__ import annotations

from datetime import date, time

from database.repository import Repository


class ReminderService:
    def __init__(self, repository: Repository) -> None:
        self._repo = repository

    def get_daily_reminders(self) -> list[dict]:
        today = date.today()
        users = self._repo.session.query(
            self._repo.session.query.__self__.__class__
        )
        from database.models import User, Habit, HabitLog
        all_users = self._repo.session.query(User).all()

        reminders = []
        for user in all_users:
            habits = self._repo.get_habits_by_user_id(user.id)
            if not habits:
                continue

            today_logs = self._repo.get_logs_for_user_on_date(user.id, today)
            pending = [
                h for h in habits
                if not any(log.habit_id == h.id and log.status for log in today_logs)
            ]
            if pending:
                reminders.append({
                    "telegram_id": user.telegram_id,
                    "reminder_time": user.reminder_time,
                    "pending_habits": [h.title for h in pending],
                })

        return reminders

    def get_evening_checkins(self) -> list[dict]:
        today = date.today()
        from database.models import User
        all_users = self._repo.session.query(User).all()

        checkins = []
        for user in all_users:
            habits = self._repo.get_habits_by_user_id(user.id)
            if not habits:
                continue

            today_logs = self._repo.get_logs_for_user_on_date(user.id, today)
            done_count = sum(1 for log in today_logs if log.status)
            total_count = len(habits)

            checkins.append({
                "telegram_id": user.telegram_id,
                "reminder_time": user.reminder_time,
                "done": done_count,
                "total": total_count,
                "all_done": done_count == total_count,
            })

        return checkins
