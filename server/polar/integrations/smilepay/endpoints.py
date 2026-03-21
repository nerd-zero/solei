import secrets
import uuid

import structlog
from fastapi import Depends, HTTPException, Query, Request

from polar.checkout.repository import CheckoutRepository
from polar.external_event.service import external_event as external_event_service
from polar.models.external_event import ExternalEventSource
from polar.postgres import AsyncSession, get_db_session
from polar.routing import APIRouter

log = structlog.get_logger()

router = APIRouter(
    prefix="/integrations/smilepay",
    tags=["integrations_smilepay"],
    include_in_schema=False,
)


@router.post("/result", status_code=202, name="integrations.smilepay.result")
async def result_webhook(
    request: Request,
    token: str = Query(),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    body = await request.json()
    order_reference = body.get("orderReference")
    transaction_reference = body.get("reference")

    if not order_reference or not transaction_reference:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Load checkout and validate webhook token
    try:
        checkout_id = uuid.UUID(order_reference)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid orderReference")

    repository = CheckoutRepository.from_session(session)
    checkout = await repository.get_by_id(checkout_id)
    if checkout is None:
        raise HTTPException(status_code=404, detail="Checkout not found")

    stored_token = (checkout.payment_processor_metadata or {}).get("webhook_token")
    if stored_token is None or not secrets.compare_digest(stored_token, token):
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    await external_event_service.enqueue(
        session,
        ExternalEventSource.smilepay,
        "smilepay.webhook.result",
        transaction_reference,
        body,
    )
