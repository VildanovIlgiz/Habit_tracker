from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import User, Habit, HabitLog, Achievement


class Repository:
    def __init__(self, session: Session | None = None) -> None:
        self.session: Session = session or SessionLocal()

    # -----------------------
    # USERS
    # -----------------------
    def get_or_create_user(self, telegram_id: int, name: str | None = None) -> User:
        user = (
            self.session.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )
        if user is None:
            user = User(telegram_id=telegram_id, name=name)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        return user

    def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        return (
            self.session.query(User)
            .filter(User.telegram_id == telegram_id)
            .first()
        )

    def create_user(self, telegram_id: int, name: str | None = None) -> User:
        user = User(telegram_id=telegram_id, name=name)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user_settings(
        self,
        telegram_id: int,
        *,
        reminder_time: str | None = None,
        communication_style: str | None = None,
    ) -> User | None:
        user = self.get_user_by_telegram_id(telegram_id)
        if user is None:
            return None
        if reminder_time is not None:
            user.reminder_time = reminder_time
        if communication_style is not None:
            user.communication_style = communication_style
        self.session.commit()
        self.session.refresh(user)
        return user

    # -----------------------
    # HABITS
    # -----------------------
    def add_habit(self, user_id: int, title: str) -> Habit:
        habit = Habit(user_id=user_id, title=title)
        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        return habit

    def create_habit(
        self,
        user_id: int,
        title: str,
        *,
        category: str | None = None,
        goal_value: float | None = None,
        goal_unit: str | None = None,
        schedule_type: str = "daily",
        schedule_data: str | None = None,
    ) -> Habit:
        habit = Habit(
            user_id=user_id,
            title=title,
            category=category,
            goal_value=goal_value,
            goal_unit=goal_unit,
            schedule_type=schedule_type,
            schedule_data=schedule_data,
        )
        self.session.add(habit)
        self.session.commit()
        self.session.refresh(habit)
        return habit

    def list_habits(self, user_id: int) -> list[Habit]:
        return (
            self.session.query(Habit)
            .filter(Habit.user_id == user_id)
            .all()
        )

    def get_habits_by_user_id(self, user_id: int) -> list[Habit]:
        return (
            self.session.query(Habit)
            .filter(Habit.user_id == user_id, Habit.is_active == True)
            .all()
        )

    def get_habit_by_id(self, habit_id: int) -> Habit | None:
        return self.session.query(Habit).get(habit_id)

    def delete_habit(self, habit_id: int) -> None:
        habit = self.session.query(Habit).get(habit_id)
        if habit:
            self.session.delete(habit)
            self.session.commit()

    def deactivate_habit(self, habit_id: int) -> None:
        habit = self.session.query(Habit).get(habit_id)
        if habit:
            habit.is_active = False
            self.session.commit()

    # -----------------------
    # LOGS
    # -----------------------
    def add_habit_log(
        self,
        habit_id: int,
        status: bool,
        value_done: float | None = None,
    ) -> HabitLog:
        log = HabitLog(
            habit_id=habit_id,
            status=status,
            value_done=value_done,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def upsert_habit_log(
        self,
        habit_id: int,
        log_date: date,
        status: bool,
        value_done: float | None = None,
    ) -> HabitLog:
        log = (
            self.session.query(HabitLog)
            .filter(HabitLog.habit_id == habit_id, HabitLog.date == log_date)
            .first()
        )
        if log is None:
            log = HabitLog(
                habit_id=habit_id,
                date=log_date,
                status=status,
                value_done=value_done,
            )
            self.session.add(log)
        else:
            log.status = status
            log.value_done = value_done
        self.session.commit()
        self.session.refresh(log)
        return log

    def get_logs_for_habit(self, habit_id: int) -> list[HabitLog]:
        return (
            self.session.query(HabitLog)
            .filter(HabitLog.habit_id == habit_id)
            .all()
        )

    def get_logs_for_user_on_date(self, user_id: int, target_date: date) -> list[HabitLog]:
        habit_ids = [
            h.id for h in self.session.query(Habit)
            .filter(Habit.user_id == user_id, Habit.is_active == True)
            .all()
        ]
        if not habit_ids:
            return []
        return (
            self.session.query(HabitLog)
            .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.date == target_date)
            .all()
        )

    def get_logs_for_habit_range(
        self, habit_id: int, start: date, end: date
    ) -> list[HabitLog]:
        return (
            self.session.query(HabitLog)
            .filter(
                HabitLog.habit_id == habit_id,
                HabitLog.date >= start,
                HabitLog.date <= end,
            )
            .order_by(HabitLog.date)
            .all()
        )

    # -----------------------
    # ACHIEVEMENTS
    # -----------------------
    def add_achievement(self, user_id: int, title: str) -> Achievement:
        ach = Achievement(user_id=user_id, title=title)
        self.session.add(ach)
        self.session.commit()
        self.session.refresh(ach)
        return ach

    def get_achievements_for_user(self, user_id: int) -> list[Achievement]:
        return (
            self.session.query(Achievement)
            .filter(Achievement.user_id == user_id)
            .order_by(Achievement.earned_at)
            .all()
        )

    def achievement_exists(self, user_id: int, title: str) -> bool:
        return (
            self.session.query(Achievement)
            .filter(Achievement.user_id == user_id, Achievement.title == title)
            .first()
            is not None
        )

    # -----------------------
    # CLEANUP
    # -----------------------
    def close(self) -> None:
        self.session.close()
