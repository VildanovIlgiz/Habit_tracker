from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class Progress:
    id: int | None = None
    habit_id: int = 0
    date: date = field(default_factory=date.today)
    status: str = "pending"
    value_done: float | None = None