from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.db import init_db
from database.repository import Repository

from config import get_settings
from handlers import advice, habits, settings as settings_handler, start, stats
from services.habit_service import HabitService
from services.achievement_service import AchievementService
from utils.scheduler import start_scheduler, stop_scheduler


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    repo = Repository()
    achievement_svc = AchievementService(repo)
    habit_service = HabitService(repo, achievement_service=achievement_svc)

    dp.include_router(start.router)
    dp.include_router(habits.get_router(habit_service))
    dp.include_router(stats.get_router(habit_service))
    dp.include_router(advice.get_router())
    dp.include_router(settings_handler.get_router(repo))

    return dp


async def main() -> None:
    setup_logging()
    app_settings = get_settings(require_token=True)

    init_db()

    bot = Bot(
        token=app_settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    start_scheduler(bot, dp)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        stop_scheduler()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
