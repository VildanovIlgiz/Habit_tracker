from __future__ import annotations

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

from database.db import Base


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

    habits: Mapped[list["Habit"]] = relationship(back_populates="user")
    achievements: Mapped[list["Achievement"]] = relationship(back_populates="user")


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
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    value_done: Mapped[float | None] = mapped_column(Float, nullable=True)

    habit: Mapped["Habit"] = relationship(back_populates="logs")


# -----------------------
# ACHIEVEMENTS
# -----------------------
class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="achievements")
