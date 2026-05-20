import structlog

from solei.config import stripe_is_configured
from solei.worker import AsyncSessionMaker, CronTrigger, TaskPriority, actor

from .service import processor_transaction as processor_transaction_service

log = structlog.get_logger()


@actor(
    actor_name="processor_transaction.sync_stripe",
    cron_trigger=CronTrigger(minute=5),
    priority=TaskPriority.LOW,
)
async def sync_stripe() -> None:
    # Bail out gracefully in dev environments where Stripe credentials have not
    # been set up yet. Without this guard the actor would crash with an
    # AuthenticationError on every 5-minute cron tick.
    if not stripe_is_configured():
        log.warning("sync_stripe skipped: Stripe is not configured")
        return
    async with AsyncSessionMaker() as session:
        await processor_transaction_service.sync_stripe(session)
