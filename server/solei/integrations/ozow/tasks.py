import uuid

import structlog

from solei.external_event.service import external_event as external_event_service
from solei.logging import Logger
from solei.models.external_event import ExternalEventSource
from solei.worker import AsyncSessionMaker, TaskPriority, actor

from . import payment

log: Logger = structlog.get_logger()

OZOW_SUCCESS_STATUS = "Complete"
OZOW_FAILURE_STATUSES = {"Cancelled", "Error", "Abandoned", "PendingInvestigation"}


@actor(actor_name="ozow.webhook.notify", priority=TaskPriority.HIGH)
async def payment_notify(event_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        async with external_event_service.handle(
            session, ExternalEventSource.ozow, event_id
        ) as event:
            data = event.data
            transaction_reference: str = data["TransactionReference"]
            transaction_id: str = data["TransactionId"]
            status: str = data.get("Status", "")
            raw_amount: float | None = data.get("Amount")
            currency_code: str | None = data.get("CurrencyCode")

            amount_cents: int | None = None
            if raw_amount is not None:
                amount_cents = int(round(float(raw_amount) * 100))

            currency = currency_code.lower() if currency_code else None

            if status == OZOW_SUCCESS_STATUS:
                await payment.handle_success(
                    session,
                    transaction_reference,
                    transaction_id,
                    amount=amount_cents,
                    currency=currency,
                )
            else:
                await payment.handle_failure(
                    session,
                    transaction_reference,
                    transaction_id,
                    amount=amount_cents,
                    currency=currency,
                )
