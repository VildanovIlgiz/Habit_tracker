from __future__ import annotations

from datetime import datetime


def validate_habit_title(title: str) -> bool:
    return bool(title and title.strip())


def validate_time_string(value: str) -> bool:
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False