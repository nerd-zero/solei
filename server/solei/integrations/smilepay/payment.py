import uuid

import structlog

from solei.checkout.repository import CheckoutRepository
from solei.checkout.service import checkout as checkout_service
from solei.enums import PaymentProcessor
from solei.exceptions import SoleiError
from solei.kit.utils import generate_uuid
from solei.logging import Logger
from solei.models import Checkout, Payment
from solei.models.payment import PaymentStatus
from solei.payment.repository import PaymentRepository
from solei.postgres import AsyncSession

log: Logger = structlog.get_logger()


class CheckoutDoesNotExist(SoleiError):
    def __init__(self, checkout_id: str) -> None:
        self.checkout_id = checkout_id
        message = f"Checkout with id {checkout_id} does not exist."
        super().__init__(message)


async def _load_checkout(session: AsyncSession, checkout_id: str) -> Checkout:
    repository = CheckoutRepository.from_session(session)
    checkout = await repository.get_by_id(
        uuid.UUID(checkout_id), options=repository.get_eager_options()
    )
    if checkout is None:
        raise CheckoutDoesNotExist(checkout_id)
    return checkout


async def _upsert_payment(
    session: AsyncSession,
    *,
    checkout: Checkout,
    transaction_reference: str,
    status: PaymentStatus,
    payment_option: str | None = None,
    amount: int | None = None,
    currency: str | None = None,
) -> Payment:
    repository = PaymentRepository.from_session(session)
    payment = await repository.get_by_processor_id(
        PaymentProcessor.smilepay, transaction_reference
    )

    if payment is None:
        payment = Payment(
            id=generate_uuid(),
            processor=PaymentProcessor.smilepay,
            processor_id=transaction_reference,
        )

    payment.status = status
    payment.amount = amount if amount is not None else checkout.total_amount or 0
    payment.currency = currency if currency is not None else checkout.currency or ""
    payment.method = payment_option or "smilepay"
    payment.method_metadata = {}
    payment.customer_email = checkout.customer_email
    payment.checkout = checkout
    payment.organization = checkout.organization

    return await repository.update(payment)


async def handle_success(
    session: AsyncSession,
    checkout_id: str,
    transaction_reference: str,
    *,
    payment_option: str | None = None,
    amount: int | None = None,
    currency: str | None = None,
) -> None:
    checkout = await _load_checkout(session, checkout_id)
    payment = await _upsert_payment(
        session,
        checkout=checkout,
        transaction_reference=transaction_reference,
        status=PaymentStatus.succeeded,
        payment_option=payment_option,
        amount=amount,
        currency=currency,
    )
    await checkout_service.handle_success(session, checkout, payment=payment)


async def handle_failure(
    session: AsyncSession,
    checkout_id: str,
    transaction_reference: str,
    *,
    payment_option: str | None = None,
    amount: int | None = None,
    currency: str | None = None,
) -> None:
    checkout = await _load_checkout(session, checkout_id)
    payment = await _upsert_payment(
        session,
        checkout=checkout,
        transaction_reference=transaction_reference,
        status=PaymentStatus.failed,
        payment_option=payment_option,
        amount=amount,
        currency=currency,
    )
    await checkout_service.handle_failure(session, checkout, payment=payment)


__all__ = ["handle_failure", "handle_success"]
