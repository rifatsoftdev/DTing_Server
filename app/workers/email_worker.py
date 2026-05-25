"""
Email worker - processes queued emails from Redis.

Usage:
    python -m app.workers.email_worker

Run in production with process manager (systemd, supervisor, etc):
    python -m app.workers.email_worker --poll-timeout 5 --idle-sleep 0.25
"""

import logging
import sys
from argparse import ArgumentParser

from services.notifications.email import EmailService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

LOGGER = logging.getLogger(__name__)


def main():
    parser = ArgumentParser(description="Email worker - processes Redis queue")
    parser.add_argument(
        "--poll-timeout",
        type=int,
        default=5,
        help="Redis blocking pop timeout (seconds)"
    )
    parser.add_argument(
        "--idle-sleep",
        type=float,
        default=0.25,
        help="Sleep duration when queue is empty (seconds)"
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=None,
        help="Stop worker after processing N jobs (useful for testing)"
    )
    args = parser.parse_args()

    try:
        service = EmailService()
        if not service.redis_client:
            raise RuntimeError(
                "Email worker cannot start because Redis queue is unavailable. "
                f"{service.redis_unavailable_reason()}"
            )

        LOGGER.info("Starting email worker...")
        LOGGER.info("  Redis URL: %s", service.redis_url)
        LOGGER.info("  Queue: %s", service.queue_name)
        LOGGER.info("  Failed queue: %s", service.failed_queue_name)
        LOGGER.info("  Poll timeout: %s seconds", args.poll_timeout)
        LOGGER.info("  Idle sleep: %s seconds", args.idle_sleep)

        service.run_worker(
            poll_timeout=args.poll_timeout,
            idle_sleep=args.idle_sleep,
            max_jobs=args.max_jobs
        )
    except KeyboardInterrupt:
        LOGGER.info("Worker stopped by user")
        sys.exit(0)
    except Exception:
        LOGGER.exception("Worker crashed")
        sys.exit(1)


if __name__ == "__main__":
    main()
