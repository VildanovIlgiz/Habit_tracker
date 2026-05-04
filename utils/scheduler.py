from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.repository import Repository
from database.db import SessionLocal
from services.reminder_service import ReminderService
from services.stats_service import StatsService

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def start_scheduler(bot=None, dp=None) -> None:
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        return

    _scheduler = AsyncIOScheduler()

    if bot is not None:
        _scheduler.add_job(
            _send_morning_reminders,
            CronTrigger(hour=9, minute=0),
            id="morning_reminders",
            replace_existing=True,
            kwargs={"bot": bot},
        )
        _scheduler.add_job(
            _send_evening_checkins,
            CronTrigger(hour=20, minute=0),
            id="evening_checkins",
            replace_existing=True,
            kwargs={"bot": bot},
        )
        _scheduler.add_job(
            _send_weekly_report,
            CronTrigger(day_of_week="sun", hour=21, minute=0),
            id="weekly_report",
            replace_existing=True,
            kwargs={"bot": bot},
        )

    _scheduler.start()
    logger.info("Scheduler started with APScheduler.")


def stop_scheduler() -> None:
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
    _scheduler = None


async def _send_morning_reminders(bot) -> None:
    try:
        repo = Repository()
        reminder_svc = ReminderService(repo)
        reminders = reminder_svc.get_daily_reminders()
        repo.close()

        for r in reminders:
            try:
                habits_text = "\n".join(f"  • {h}" for h in r["pending_habits"])
                await bot.send_message(
                    r["telegram_id"],
                    f"🌅 <b>Доброе утро!</b>\n\nСегодня не забудь:\n{habits_text}",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.error("Failed to send reminder to %s: %s", r["telegram_id"], e)
    except Exception as e:
        logger.error("Morning reminder job error: %s", e)


async def _send_evening_checkins(bot) -> None:
    try:
        repo = Repository()
        reminder_svc = ReminderService(repo)
        checkins = reminder_svc.get_evening_checkins()
        repo.close()

        for c in checkins:
            try:
                if c["all_done"]:
                    await bot.send_message(
                        c["telegram_id"],
                        f"🎉 <b>Все привычки выполнены!</b> ({c['done']}/{c['total']})\nТак держать! 🔥",
                        parse_mode="HTML",
                    )
                else:
                    await bot.send_message(
                        c["telegram_id"],
                        f"🌙 <b>Вечерняя проверка</b>\nВыполнено: {c['done']}/{c['total']}\n"
                        f"Ещё есть время — отмечай невыполненные!",
                        parse_mode="HTML",
                    )
            except Exception as e:
                logger.error("Failed to send checkin to %s: %s", c["telegram_id"], e)
    except Exception as e:
        logger.error("Evening checkin job error: %s", e)


async def _send_weekly_report(bot) -> None:
    try:
        repo = Repository()
        stats_svc = StatsService(repo)
        from database.models import User
        users = repo.session.query(User).all()

        for user in users:
            try:
                report = stats_svc.get_weekly_report(user.telegram_id)
                await bot.send_message(
                    user.telegram_id,
                    report,
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.error("Failed to send weekly report to %s: %s", user.telegram_id, e)

        repo.close()
    except Exception as e:
        logger.error("Weekly report job error: %s", e)
