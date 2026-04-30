import structlog
from fastapi import Depends, HTTPException, Request

from solei.external_event.service import external_event as external_event_service
from solei.integrations.paystack.service import paystack as paystack_service
from solei.models.external_event import ExternalEventSource
from solei.postgres import AsyncSession, get_db_session
from solei.routing import APIRouter

log = structlog.get_logger()

router = APIRouter(
    prefix="/integrations/paystack",
    tags=["integrations_paystack"],
    include_in_schema=False,
)

IMPLEMENTED_WEBHOOKS = {
    "customeridentification.success",
    "customeridentification.failed",
}


@router.post("/webhook", status_code=202, name="integrations.paystack.webhook")
async def webhook(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    if not paystack_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401)

    payload = await request.json()
    event_type: str = payload.get("event", "")

    if event_type not in IMPLEMENTED_WEBHOOKS:
        return

    task_name = f"paystack.webhook.{event_type}"
    external_id: str = payload.get("data", {}).get("customer_code", "")
    if not external_id:
        log.warning("paystack.webhook.missing_customer_code", event=event_type)
        return

    await external_event_service.enqueue(
        session, ExternalEventSource.paystack, task_name, external_id, payload
    )
