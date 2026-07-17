import uuid

import structlog

from solei.external_event.service import external_event as external_event_service
from solei.logging import Logger
from solei.models.external_event import ExternalEventSource
from solei.worker import AsyncSessionMaker, TaskPriority, actor

from . import payment

log: Logger = structlog.get_logger()

OZOW_SUCCESS_STATUS = "successful"
OZOW_FAILURE_STATUSES = {"error", "incomplete", "refunded"}


@actor(actor_name="ozow.webhook.notify", priority=TaskPriority.HIGH)
async def payment_notify(event_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        async with external_event_service.handle(
            session, ExternalEventSource.ozow, event_id
        ) as event:
            data = event.data
            merchant_reference: str = data["merchantReference"]
            transaction_id: str = data["id"]
            status: str = data.get("status", "")

            amount_data: dict[str, object] | None = data.get("amount")  # type: ignore[assignment]
            amount_cents: int | None = None
            currency: str | None = None
            if amount_data:
                raw_amount = amount_data.get("value")
                if raw_amount is not None:
                    amount_cents = int(round(float(raw_amount) * 100))
                currency_code = amount_data.get("currency")
                if currency_code:
                    currency = str(currency_code).lower()

            if status == OZOW_SUCCESS_STATUS:
                await payment.handle_success(
                    session,
                    merchant_reference,
                    transaction_id,
                    amount=amount_cents,
                    currency=currency,
                )
            else:
                await payment.handle_failure(
                    session,
                    merchant_reference,
                    transaction_id,
                    amount=amount_cents,
                    currency=currency,
                )
