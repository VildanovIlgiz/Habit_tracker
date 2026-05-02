from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_scheduler_started = False


def start_scheduler() -> None:
    global _scheduler_started

    if _scheduler_started:
        return

    logger.info("Scheduler placeholder started.")
    _scheduler_started = True


def stop_scheduler() -> None:
    global _scheduler_started

    if not _scheduler_started:
        return

    logger.info("Scheduler placeholder stopped.")
    _scheduler_started = False