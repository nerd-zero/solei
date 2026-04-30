import uuid

from solei.external_event.service import external_event as external_event_service
from solei.user.service import user as user_service
from solei.worker import AsyncSessionMaker, TaskPriority, actor


@actor(
    actor_name="paystack.webhook.customeridentification.success",
    priority=TaskPriority.HIGH,
)
async def customeridentification_success(event_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        async with external_event_service.handle_paystack(session, event_id) as event:
            customer_code: str = event.data["data"]["customer_code"]
            await user_service.identity_verification_verified_by_id(
                session, customer_code
            )


@actor(
    actor_name="paystack.webhook.customeridentification.failed",
    priority=TaskPriority.HIGH,
)
async def customeridentification_failed(event_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        async with external_event_service.handle_paystack(session, event_id) as event:
            customer_code: str = event.data["data"]["customer_code"]
            await user_service.identity_verification_failed_by_id(
                session, customer_code
            )
