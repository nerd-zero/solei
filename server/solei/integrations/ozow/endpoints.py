import structlog
from fastapi import Depends, HTTPException, Request

from solei.external_event.service import external_event as external_event_service
from solei.models.external_event import ExternalEventSource
from solei.postgres import AsyncSession, get_db_session
from solei.routing import APIRouter

log = structlog.get_logger()

router = APIRouter(
    prefix="/integrations/ozow",
    tags=["integrations_ozow"],
    include_in_schema=False,
)

OZOW_PENDING_STATUS = "pending"


@router.post("/notify", status_code=202, name="integrations.ozow.notify")
async def notify_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    body: dict[str, object] = await request.json()

    merchant_reference = body.get("merchantReference")
    transaction_id = body.get("id")

    if not merchant_reference or not transaction_id:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # One API sends "pending" while the transaction is not yet finalised.
    # Skip storing the event — the final-status notification will follow.
    status = body.get("status", "")
    if status == OZOW_PENDING_STATUS:
        return

    await external_event_service.enqueue(
        session,
        ExternalEventSource.ozow,
        "ozow.webhook.notify",
        str(transaction_id),
        body,
    )
