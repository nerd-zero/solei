from typing import Any
from uuid import UUID

import stripe as stripe_lib
import structlog
from sqlalchemy import func, update

from solei.config import settings
from solei.exceptions import SoleiError
from solei.integrations.paystack.service import PaystackError
from solei.integrations.paystack.service import paystack as paystack_service
from solei.integrations.stripe.service import stripe as stripe_service
from solei.kit.anonymization import anonymize_email_for_deletion
from solei.models import NotificationRecipient, User
from solei.models.user import IdentityVerificationStatus
from solei.organization.repository import OrganizationRepository
from solei.postgres import AsyncSession
from solei.worker import enqueue_job

from .repository import UserRepository
from .schemas import (
    BlockingOrganization,
    PaystackIdentitySubmit,
    UserDeletionBlockedReason,
    UserDeletionResponse,
    UserIdentityVerification,
    UserSignupAttribution,
    UserUpdate,
)

log = structlog.get_logger()


class UserError(SoleiError): ...


class IdentityAlreadyVerified(UserError):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        message = "Your identity is already verified."
        super().__init__(message, 403)


class IdentityVerificationProcessing(UserError):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        message = "Your identity verification is still processing."
        super().__init__(message, 403)


class IdentityVerificationDoesNotExist(UserError):
    def __init__(self, identity_verification_id: str) -> None:
        self.identity_verification_id = identity_verification_id
        message = (
            f"Received identity verification {identity_verification_id} from Stripe, "
            "but no associated User exists."
        )
        super().__init__(message)


class PaystackSubmissionError(UserError):
    def __init__(self, message: str) -> None:
        super().__init__(message, 422)


class InvalidAccount(UserError):
    def __init__(self, account_id: UUID) -> None:
        self.account_id = account_id
        message = (
            f"The account {account_id} does not exist or you don't have access to it."
        )
        super().__init__(message)


# Countries routed through Paystack identity verification
PAYSTACK_COUNTRIES = frozenset({"ZA", "GH", "NG"})

# Official Paystack test credentials for Nigeria (bank_account type only works with live keys)
_PAYSTACK_NG_TEST_PAYLOAD: dict[str, Any] = {
    "country": "NG",
    "type": "bank_account",
    "account_number": "0111111111",
    "bvn": "22222222221",
    "bank_code": "007",
    "first_name": "Uchenna",
    "last_name": "Okoro",
}

# Default required ID type per country for Paystack
_PAYSTACK_ID_TYPE: dict[str, str] = {
    "ZA": "sa_id",
    "GH": "tin",
    "NG": "bank_account",
}


class UserService:
    async def get_by_email_or_create(
        self,
        session: AsyncSession,
        email: str,
        *,
        signup_attribution: UserSignupAttribution | None = None,
    ) -> tuple[User, bool]:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_email(email)
        created = False
        if user is None:
            user = await self.create_by_email(
                session, email, signup_attribution=signup_attribution
            )
            created = True

        return (user, created)

    async def create_by_email(
        self,
        session: AsyncSession,
        email: str,
        signup_attribution: UserSignupAttribution | None = None,
    ) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.create(
            User(
                email=email,
                oauth_accounts=[],
                signup_attribution=signup_attribution,
            ),
            flush=True,
        )
        enqueue_job("user.on_after_signup", user_id=user.id)
        return user

    async def update(
        self,
        session: AsyncSession,
        user: User,
        update_schema: UserUpdate,
    ) -> User:
        repository = UserRepository.from_session(session)
        return await repository.update(
            user, update_dict=update_schema.model_dump(exclude_unset=True)
        )

    async def create_identity_verification(
        self, session: AsyncSession, user: User
    ) -> UserIdentityVerification:
        if user.identity_verified:
            raise IdentityAlreadyVerified(user.id)

        if user.identity_verification_status == IdentityVerificationStatus.pending:
            raise IdentityVerificationProcessing(user.id)

        country = (user.country or "").upper()
        if country in PAYSTACK_COUNTRIES:
            return await self._create_paystack_verification(session, user, country)
        return await self._create_stripe_verification(session, user)

    async def _create_stripe_verification(
        self, session: AsyncSession, user: User
    ) -> UserIdentityVerification:
        verification_session: stripe_lib.identity.VerificationSession | None = None
        if (
            user.identity_verification_id is not None
            and user.identity_verification_provider != "paystack"
        ):
            verification_session = await stripe_service.get_verification_session(
                user.identity_verification_id
            )

        if (
            verification_session is None
            or verification_session.status != "requires_input"
        ):
            verification_session = await stripe_service.create_verification_session(
                user
            )

        repository = UserRepository.from_session(session)
        await repository.update(
            user,
            update_dict={
                "identity_verification_id": verification_session.id,
                "identity_verification_provider": "stripe",
            },
        )

        assert verification_session.client_secret is not None
        return UserIdentityVerification(
            provider="stripe",
            id=verification_session.id,
            client_secret=verification_session.client_secret,
        )

    async def _create_paystack_verification(
        self, session: AsyncSession, user: User, country: str
    ) -> UserIdentityVerification:
        # Reuse existing customer code if already created via Paystack
        customer_code = (
            user.identity_verification_id
            if user.identity_verification_provider == "paystack"
            else None
        )

        if customer_code is None:
            customer = await paystack_service.create_customer(user)
            customer_code = customer["customer_code"]
            repository = UserRepository.from_session(session)
            await repository.update(
                user,
                update_dict={
                    "identity_verification_id": customer_code,
                    "identity_verification_provider": "paystack",
                },
            )

        required_id_type = _PAYSTACK_ID_TYPE.get(country)
        return UserIdentityVerification(
            provider="paystack",
            customer_code=customer_code,
            required_id_type=required_id_type,
        )

    async def submit_paystack_verification(
        self, session: AsyncSession, user: User, payload: PaystackIdentitySubmit
    ) -> None:
        if user.identity_verification_provider != "paystack":
            raise IdentityVerificationDoesNotExist("no_paystack_session")

        if user.identity_verification_id is None:
            raise IdentityVerificationDoesNotExist("no_paystack_customer")

        country = (user.country or "").upper()

        # Paystack only validates with live keys; use official NG test credentials in dev/test
        if country == "NG" and (settings.is_development() or settings.is_testing()):
            identification_payload: dict[str, Any] = _PAYSTACK_NG_TEST_PAYLOAD
        else:
            identification_payload = {
                "country": country,
                "type": payload.id_type,
                "value": payload.id_number,
                "first_name": payload.first_name,
                "last_name": payload.last_name,
            }
            if payload.bvn is not None:
                identification_payload["bvn"] = payload.bvn
            if payload.bank_code is not None:
                identification_payload["bank_code"] = payload.bank_code
            if payload.account_number is not None:
                identification_payload["account_number"] = payload.account_number

        try:
            await paystack_service.validate_identity(
                user.identity_verification_id, identification_payload
            )
        except PaystackError as e:
            raise PaystackSubmissionError(str(e)) from e

        repository = UserRepository.from_session(session)
        await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.pending
            },
        )

    async def identity_verification_verified(
        self,
        session: AsyncSession,
        verification_session: stripe_lib.identity.VerificationSession,
    ) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_identity_verification_id(verification_session.id)
        if user is None:
            raise IdentityVerificationDoesNotExist(verification_session.id)

        assert verification_session.status == "verified"
        return await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.verified
            },
        )

    async def identity_verification_pending(
        self,
        session: AsyncSession,
        verification_session: stripe_lib.identity.VerificationSession,
    ) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_identity_verification_id(verification_session.id)
        if user is None:
            raise IdentityVerificationDoesNotExist(verification_session.id)

        # If the user is already verified, we don't need to update their status.
        # Might happen if the webhook was delayed
        if user.identity_verified:
            return user

        assert verification_session.status == "processing"
        return await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.pending
            },
        )

    async def identity_verification_failed(
        self,
        session: AsyncSession,
        verification_session: stripe_lib.identity.VerificationSession,
    ) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_identity_verification_id(verification_session.id)
        if user is None:
            raise IdentityVerificationDoesNotExist(verification_session.id)

        # TODO: should we send an email?

        return await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.failed
            },
        )

    async def identity_verification_verified_by_id(
        self, session: AsyncSession, identity_verification_id: str
    ) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_identity_verification_id(
            identity_verification_id
        )
        if user is None:
            raise IdentityVerificationDoesNotExist(identity_verification_id)
        return await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.verified
            },
        )

    async def identity_verification_failed_by_id(
        self, session: AsyncSession, identity_verification_id: str
    ) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_identity_verification_id(
            identity_verification_id
        )
        if user is None:
            raise IdentityVerificationDoesNotExist(identity_verification_id)
        return await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.failed
            },
        )

    async def get_identity_verified_country(self, user: User) -> str | None:
        if user.identity_verification_id is None:
            return None
        if user.identity_verification_provider == "paystack":
            return user.country
        try:
            vs = await stripe_service.get_verification_session(
                user.identity_verification_id,
                expand=["verified_outputs", "last_verification_report"],
            )
            # Try verified address country first
            verified_outputs = getattr(vs, "verified_outputs", None)
            if verified_outputs:
                address = getattr(verified_outputs, "address", None)
                if address and address.country:
                    return address.country
            # Fall back to document issuing country from the verification report
            report = getattr(vs, "last_verification_report", None)
            if report:
                document = getattr(report, "document", None)
                if document:
                    issuing_country = getattr(document, "issuing_country", None)
                    if issuing_country:
                        return issuing_country
        except stripe_lib.StripeError:
            log.warning(
                "get_identity_verified_country.fetch_failed",
                identity_verification_id=user.identity_verification_id,
            )
        return None

    async def delete_identity_verification(
        self, session: AsyncSession, user: User
    ) -> User:
        """Delete identity verification for a user.

        For Stripe: resets status and redacts the verification session.
        For Paystack: resets status only (no redaction API available).
        """
        repository = UserRepository.from_session(session)

        if (
            user.identity_verification_id is not None
            and user.identity_verification_provider != "paystack"
        ):
            try:
                await stripe_service.redact_verification_session(
                    user.identity_verification_id
                )
            except stripe_lib.InvalidRequestError as e:
                log.warning(
                    "stripe.identity.verification_session.redact.not_found",
                    identity_verification_id=user.identity_verification_id,
                    error=str(e),
                )

        return await repository.update(
            user,
            update_dict={
                "identity_verification_status": IdentityVerificationStatus.unverified,
                "identity_verification_id": None,
                "identity_verification_provider": None,
            },
        )

    async def check_can_delete(
        self,
        session: AsyncSession,
        user: User,
    ) -> UserDeletionResponse:
        """Check if a user can be deleted.

        A user can be deleted if all organizations they are members of
        are soft-deleted (deleted_at is not None).
        """
        blocked_reasons: list[UserDeletionBlockedReason] = []
        blocking_organizations: list[BlockingOrganization] = []

        # Get all organizations the user is a member of (excluding deleted orgs)
        org_repository = OrganizationRepository.from_session(session)
        organizations = await org_repository.get_all_by_user(user.id)

        if organizations:
            blocked_reasons.append(UserDeletionBlockedReason.HAS_ACTIVE_ORGANIZATIONS)
            for org in organizations:
                blocking_organizations.append(
                    BlockingOrganization(id=org.id, slug=org.slug, name=org.name)
                )

        return UserDeletionResponse(
            deleted=False,
            blocked_reasons=blocked_reasons,
            blocking_organizations=blocking_organizations,
        )

    async def request_deletion(
        self,
        session: AsyncSession,
        user: User,
    ) -> UserDeletionResponse:
        """Request deletion of the user account.

        Flow:
        1. Check if user has any active organizations -> block if yes
        2. Soft delete the user

        Note: The user's Account (payout account) is not deleted here.
        Accounts are tied to organizations and should be deleted when the
        organization is deleted, not when the user account is deleted.
        """
        check_result = await self.check_can_delete(session, user)

        if check_result.blocked_reasons:
            return check_result

        # Soft delete the user
        await self.soft_delete_user(session, user)

        return UserDeletionResponse(
            deleted=True,
            blocked_reasons=[],
            blocking_organizations=[],
        )

    async def soft_delete_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> User:
        """Soft-delete a user, anonymizing PII fields."""
        repository = UserRepository.from_session(session)

        update_dict: dict[str, Any] = {}

        update_dict["email"] = anonymize_email_for_deletion(user.email)

        if user.avatar_url:
            update_dict["avatar_url"] = None

        if user.meta:
            update_dict["meta"] = {}

        user = await repository.update(user, update_dict=update_dict)
        await repository.soft_delete(user)

        await self._delete_oauth_accounts(session, user)
        await self._delete_notification_recipients(session, user)

        log.info("user.deleted", user_id=user.id)

        return user

    async def _delete_oauth_accounts(self, session: AsyncSession, user: User) -> None:
        """Delete all OAuth accounts for a user."""
        for account in user.oauth_accounts:
            await session.delete(account)

    async def _delete_notification_recipients(
        self,
        session: AsyncSession,
        user: User,
    ) -> None:
        """Soft-delete all notification recipients for a user."""
        stmt = (
            update(NotificationRecipient)
            .where(NotificationRecipient.user_id == user.id)
            .where(NotificationRecipient.is_deleted.is_(False))
            .values(deleted_at=func.now())
        )
        await session.execute(stmt)

        log.info(
            "user.notification_recipients_deleted",
            user_id=user.id,
        )


user = UserService()
