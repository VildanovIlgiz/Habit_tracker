from __future__ import annotations

from datetime import date, timedelta

from database.repository import Repository


class StatsService:
    def __init__(self, repository: Repository) -> None:
        self._repo = repository

    def get_summary(self, telegram_id: int) -> dict:
        user = self._repo.get_user_by_telegram_id(telegram_id)
        if user is None:
            return {
                "total_habits": 0,
                "completion_rate": 0.0,
                "current_streak": 0,
                "completed_today": 0,
                "completed_this_week": 0,
                "best_habit": None,
            }

        habits = self._repo.get_habits_by_user_id(user.id)
        total_habits = len(habits)

        if total_habits == 0:
            return {
                "total_habits": 0,
                "completion_rate": 0.0,
                "current_streak": 0,
                "completed_today": 0,
                "completed_this_week": 0,
                "best_habit": None,
            }

        today = date.today()
        today_logs = self._repo.get_logs_for_user_on_date(user.id, today)
        completed_today = sum(1 for log in today_logs if log.status)

        week_start = today - timedelta(days=today.weekday())
        week_end = today
        completed_this_week = 0
        habit_week_counts: dict[int, int] = {}

        for habit in habits:
            logs = self._repo.get_logs_for_habit_range(habit.id, week_start, week_end)
            done_count = sum(1 for log in logs if log.status)
            completed_this_week += done_count
            habit_week_counts[habit.id] = done_count

        best_habit_id = max(habit_week_counts, key=habit_week_counts.get) if habit_week_counts else None
        best_habit = None
        if best_habit_id is not None:
            best_habit_obj = self._repo.get_habit_by_id(best_habit_id)
            if best_habit_obj:
                best_habit = best_habit_obj.title

        total_possible_days = (week_end - week_start).days + 1
        total_possible = total_habits * total_possible_days
        completion_rate = (completed_this_week / total_possible * 100) if total_possible > 0 else 0.0

        current_streak = self._calculate_streak(user.id, habits)

        return {
            "total_habits": total_habits,
            "completion_rate": round(completion_rate, 1),
            "current_streak": current_streak,
            "completed_today": completed_today,
            "completed_this_week": completed_this_week,
            "best_habit": best_habit,
        }

    def _calculate_streak(self, user_id: int, habits: list) -> int:
        if not habits:
            return 0

        today = date.today()
        streak = 0

        for day_offset in range(365):
            check_date = today - timedelta(days=day_offset)
            logs = self._repo.get_logs_for_user_on_date(user_id, check_date)
            if not logs:
                if day_offset == 0:
                    continue
                break

            done_count = sum(1 for log in logs if log.status)
            if done_count == 0:
                if day_offset == 0:
                    continue
                break
            streak += 1

        return streak

    def get_weekly_report(self, telegram_id: int) -> str:
        summary = self.get_summary(telegram_id)
        if summary["total_habits"] == 0:
            return "У тебя пока нет активных привычек для отчёта."

        lines = [
            f"📊 <b>Недельный отчёт</b>\n",
            f"📈 Процент выполнения: <b>{summary['completion_rate']}%</b>",
            f"🔥 Текущая серия: <b>{summary['current_streak']} дн.</b>",
            f"✅ Выполнено на этой неделе: <b>{summary['completed_this_week']}</b>",
        ]
        if summary["best_habit"]:
            lines.append(f"🏆 Лучшая привычка: <b>{summary['best_habit']}</b>")

        return "\n".join(lines)
