import uuid

import structlog

from polar.external_event.service import external_event as external_event_service
from polar.logging import Logger
from polar.models.external_event import ExternalEventSource
from polar.worker import AsyncSessionMaker, TaskPriority, actor

from . import payment
from .service import SmilePayError, smilepay_service

log: Logger = structlog.get_logger()


@actor(actor_name="smilepay.webhook.result", priority=TaskPriority.HIGH)
async def payment_result(event_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        async with external_event_service.handle(
            session, ExternalEventSource.smilepay, event_id
        ) as event:
            data = event.data
            order_reference: str = data["orderReference"]
            transaction_reference: str = data["reference"]
            payment_option: str | None = data.get("paymentOption")
            raw_amount: float | None = data.get("amount")
            currency: str | None = data.get("currency")

            # Verify status with SmilePay before acting
            try:
                verified_status = await smilepay_service.verify_payment_status(
                    order_reference
                )
            except SmilePayError:
                log.warning(
                    "SmilePay status check failed, falling back to webhook status",
                    order_reference=order_reference,
                )
                verified_status = data.get("status", "UNKNOWN")

            # Convert amount to cents if present
            amount_cents: int | None = None
            if raw_amount is not None and currency is not None:
                amount_cents = int(round(raw_amount * 100))

            if verified_status == "PAID":
                await payment.handle_success(
                    session,
                    order_reference,
                    transaction_reference,
                    payment_option=payment_option,
                    amount=amount_cents,
                    currency=currency.lower() if currency else None,
                )
            else:
                await payment.handle_failure(
                    session,
                    order_reference,
                    transaction_reference,
                    payment_option=payment_option,
                    amount=amount_cents,
                    currency=currency.lower() if currency else None,
                )
