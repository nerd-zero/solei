import structlog
from fastapi import Depends, HTTPException, Request

from solei.external_event.service import external_event as external_event_service
from solei.models.external_event import ExternalEventSource
from solei.postgres import AsyncSession, get_db_session
from solei.routing import APIRouter

from .service import ozow_service

log = structlog.get_logger()

router = APIRouter(
    prefix="/integrations/ozow",
    tags=["integrations_ozow"],
    include_in_schema=False,
)

OZOW_PENDING_STATUS = "Pending"


@router.post("/notify", status_code=202, name="integrations.ozow.notify")
async def notify_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    form = await request.form()
    body: dict[str, str] = {k: str(v) for k, v in form.items()}

    transaction_reference = body.get("TransactionReference")
    transaction_id = body.get("TransactionId")

    if not transaction_reference or not transaction_id:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Pending means Ozow hasn't determined the final status yet and will retry.
    # Don't store the event — doing so would block the later final-status notification
    # from being enqueued (unique constraint on source+external_id).
    status = body.get("Status", "")
    if status == OZOW_PENDING_STATUS:
        return

    if not ozow_service.verify_notification_hash(body):
        raise HTTPException(status_code=401, detail="Invalid hash")

    await external_event_service.enqueue(
        session,
        ExternalEventSource.ozow,
        "ozow.webhook.notify",
        transaction_id,
        body,
    )
