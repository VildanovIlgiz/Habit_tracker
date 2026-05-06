from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.db import SessionLocal, init_db

from config import get_settings
from handlers import advice, habits, settings as settings_handler, start, stats
from services import habit_service
from services.habit_service import HabitService
from utils.scheduler import start_scheduler, stop_scheduler


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.include_router(start.router)
    
    from services.habit_service import HabitService
    from database.db import SessionLocal

# Создаем сервис для работы с привычками
    habit_service = HabitService(SessionLocal())

# Получаем роутер через фабрику
    dp.include_router(habits.get_router(habit_service))



    dp.include_router(stats.router)
    dp.include_router(advice.router)
    dp.include_router(settings_handler.router)

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

    start_scheduler()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        stop_scheduler()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())