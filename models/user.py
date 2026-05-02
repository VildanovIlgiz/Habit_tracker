from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class User:
    id: int | None = None
    telegram_id: int = 0
    name: str | None = None
    reminder_time: str = "20:00"
    communication_style: str = "neutral"
    created_at: datetime = field(default_factory=datetime.utcnow)