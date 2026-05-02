from __future__ import annotations

from database.repository import Repository


ACHIEVEMENT_DEFS = [
    {
        "title": "Первый шаг",
        "description": "Создал первую привычку",
        "check": lambda ctx: ctx["total_habits"] >= 1,
    },
    {
        "title": "Коллекционер",
        "description": "Создал 5 привычек",
        "check": lambda ctx: ctx["total_habits"] >= 5,
    },
    {
        "title": "Неделя силы",
        "description": "Серия 7 дней подряд",
        "check": lambda ctx: ctx["streak"] >= 7,
    },
    {
        "title": "Месяц дисциплины",
        "description": "Серия 30 дней подряд",
        "check": lambda ctx: ctx["streak"] >= 30,
    },
    {
        "title": "Отличник",
        "description": "Все привычки выполнены за день",
        "check": lambda ctx: ctx["all_done_today"],
    },
    {
        "title": "10 раз отмечено",
        "description": "Отметил выполнение 10 раз",
        "check": lambda ctx: ctx["total_done"] >= 10,
    },
    {
        "title": "50 раз отмечено",
        "description": "Отметил выполнение 50 раз",
        "check": lambda ctx: ctx["total_done"] >= 50,
    },
]


class AchievementService:
    def __init__(self, repository: Repository) -> None:
        self._repo = repository

    def check_and_award(self, user_id: int, habit_id: int) -> list[str]:
        from datetime import date
        from database.models import HabitLog

        habits = self._repo.get_habits_by_user_id(user_id)
        total_habits = len(habits)

        all_logs = []
        for h in habits:
            all_logs.extend(self._repo.get_logs_for_habit(h.id))
        total_done = sum(1 for log in all_logs if log.status)

        streak = self._calculate_streak(user_id, habits)

        today = date.today()
        today_logs = self._repo.get_logs_for_user_on_date(user_id, today)
        done_today = sum(1 for log in today_logs if log.status)
        all_done_today = (done_today == total_habits) and total_habits > 0

        ctx = {
            "total_habits": total_habits,
            "streak": streak,
            "all_done_today": all_done_today,
            "total_done": total_done,
        }

        new_achievements = []
        for ach_def in ACHIEVEMENT_DEFS:
            title = ach_def["title"]
            if self._repo.achievement_exists(user_id, title):
                continue
            if ach_def["check"](ctx):
                self._repo.add_achievement(user_id, title)
                new_achievements.append(title)

        return new_achievements

    def get_earned_achievements(self, user_id: int) -> list[dict]:
        achs = self._repo.get_achievements_for_user(user_id)
        result = []
        for ach in achs:
            desc = ""
            for d in ACHIEVEMENT_DEFS:
                if d["title"] == ach.title:
                    desc = d["description"]
                    break
            result.append({
                "title": ach.title,
                "description": desc,
                "earned_at": ach.earned_at,
            })
        return result

    def _calculate_streak(self, user_id: int, habits: list) -> int:
        from datetime import date, timedelta

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
