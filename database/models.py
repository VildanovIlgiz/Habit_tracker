# from __future__ import annotations

# from dataclasses import dataclass, field
# from datetime import date, datetime


# @dataclass(slots=True)
# class UserRecord:
#     telegram_id: int
#     name: str | None = None
#     reminder_time: str = "20:00"
#     communication_style: str = "neutral"
#     created_at: datetime = field(default_factory=datetime.utcnow)


# @dataclass(slots=True)
# class HabitRecord:
#     id: int | None = None
#     user_id: int = 0
#     title: str = ""
#     category: str | None = None
#     goal_value: float | None = None
#     goal_unit: str | None = None
#     schedule_type: str = "daily"
#     schedule_data: str | None = None
#     is_active: bool = True
#     created_at: datetime = field(default_factory=datetime.utcnow)


# @dataclass(slots=True)
# class HabitLogRecord:
#     id: int | None = None
#     habit_id: int = 0
#     date: date = field(default_factory=date.today)
#     status: str = "pending"
#     value_done: float | None = None



from __future__ import annotations

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from database.db import Base

from datetime import datetime, date

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship



# -----------------------
# USERS
# -----------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    reminder_time: Mapped[str] = mapped_column(String, default="20:00")
    communication_style: Mapped[str] = mapped_column(String, default="neutral")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # связь с привычками
    habits: Mapped[list["Habit"]] = relationship(back_populates="user")


# -----------------------
# HABITS
# -----------------------
class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String, nullable=True)

    goal_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    goal_unit: Mapped[str | None] = mapped_column(String, nullable=True)

    schedule_type: Mapped[str] = mapped_column(String, default="daily")
    schedule_data: Mapped[str | None] = mapped_column(String, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # связи
    user: Mapped["User"] = relationship(back_populates="habits")
    logs: Mapped[list["HabitLog"]] = relationship(back_populates="habit")


# -----------------------
# HABIT LOGS
# -----------------------
class HabitLog(Base):
    __tablename__ = "habit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"))

    date: Mapped[date] = mapped_column(Date, default=date.today)
    status: Mapped[str] = mapped_column(String, default="pending")
    value_done: Mapped[float | None] = mapped_column(Float, nullable=True)

    # связь
    habit: Mapped["Habit"] = relationship(back_populates="logs")


# -----------------------
# ACHIEVEMENTS (можно позже)
# -----------------------
class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)