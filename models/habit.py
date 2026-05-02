from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Habit:
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