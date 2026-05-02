from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(slots=True)
class UserRecord:
    telegram_id: int
    name: str | None = None
    reminder_time: str = "20:00"
    communication_style: str = "neutral"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class HabitRecord:
    id: int | None = None
    user_id: int = 0
    title: str = ""
    category: str | None = None
    goal_value: float | None = None
    goal_unit: str | None = None
    schedule_type: str = "daily"
    schedule_data: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class HabitLogRecord:
    id: int | None = None
    habit_id: int = 0
    date: date = field(default_factory=date.today)
    status: str = "pending"
    value_done: float | None = None