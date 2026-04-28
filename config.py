from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(slots=True)
class Settings:
    bot_token: str = ""
    openai_api_key: str | None = None
    database_url: str = "sqlite:///habit_tracker.db"
    debug: bool = False


def _to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings(require_token: bool = False) -> Settings:
    load_dotenv()

    settings = Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        database_url=os.getenv("DATABASE_URL", "sqlite:///habit_tracker.db").strip(),
        debug=_to_bool(os.getenv("DEBUG")),
    )

    if require_token and not settings.bot_token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Create a .env file and add your Telegram bot token."
        )

    return settings