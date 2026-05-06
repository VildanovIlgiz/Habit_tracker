# from __future__ import annotations

# from database.models import HabitLogRecord, HabitRecord, UserRecord


# class Repository:
#     """
#     Temporary in-memory repository.

#     Later another team member can replace this with a real SQLAlchemy repository
#     without changing the handlers layer.
#     """

#     def __init__(self) -> None:
#         self._users: dict[int, UserRecord] = {}
#         self._habits: dict[int, HabitRecord] = {}
#         self._habit_logs: dict[int, HabitLogRecord] = {}
#         self._habit_seq = 1
#         self._log_seq = 1

#     def get_or_create_user(self, telegram_id: int, name: str | None = None) -> UserRecord:
#         user = self._users.get(telegram_id)
#         if user is None:
#             user = UserRecord(telegram_id=telegram_id, name=name)
#             self._users[telegram_id] = user
#         return user

#     def add_habit(self, user_id: int, title: str) -> HabitRecord:
#         habit = HabitRecord(
#             id=self._habit_seq,
#             user_id=user_id,
#             title=title,
#         )
#         self._habits[self._habit_seq] = habit
#         self._habit_seq += 1
#         return habit

#     def list_habits(self, user_id: int) -> list[HabitRecord]:
#         return [habit for habit in self._habits.values() if habit.user_id == user_id]

#     def add_habit_log(
#         self,
#         habit_id: int,
#         status: str,
#         value_done: float | None = None,
#     ) -> HabitLogRecord:
#         log = HabitLogRecord(
#             id=self._log_seq,
#             habit_id=habit_id,
#             status=status,
#             value_done=value_done,
#         )
#         self._habit_logs[self._log_seq] = log
#         self._log_seq += 1
#         return log





from __future__ import annotations

from sqlalchemy.orm import Session


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import SessionLocal


from database.models import User, Habit, HabitLog


class Repository:
    def __init__(self) -> None:
        self.session: Session = SessionLocal()

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

    # -----------------------
    # HABITS
    # -----------------------
    def add_habit(self, user_id: int, title: str) -> Habit:
        habit = Habit(user_id=user_id, title=title)

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

    def delete_habit(self, habit_id: int) -> None:
        habit = self.session.query(Habit).get(habit_id)
        if habit:
            self.session.delete(habit)
            self.session.commit()

    # -----------------------
    # LOGS
    # -----------------------
    def add_habit_log(
        self,
        habit_id: int,
        status: str,
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

    def get_logs_for_habit(self, habit_id: int) -> list[HabitLog]:
        return (
            self.session.query(HabitLog)
            .filter(HabitLog.habit_id == habit_id)
            .all()
        )

    # -----------------------
    # CLEANUP
    # -----------------------
    def close(self) -> None:
        self.session.close()