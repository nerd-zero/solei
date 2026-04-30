from __future__ import annotations

import uuid

import stripe as stripe_lib
from sqlalchemy.orm.strategy_options import joinedload

from solei.account.repository import AccountRepository
from solei.account_credit.service import account_credit_service
from solei.auth.models import AuthSubject
from solei.campaign.service import campaign as campaign_service
from solei.enums import AccountType
from solei.exceptions import SoleiError
from solei.integrations.loops.service import loops as loops_service
from solei.integrations.paystack.service import PaystackError
from solei.integrations.paystack.service import paystack as paystack_service
from solei.integrations.stripe.service import stripe
from solei.models import Account, Organization, User
from solei.models.user import IdentityVerificationStatus
from solei.postgres import AsyncReadSession, AsyncSession
from solei.user.repository import UserRepository

from .schemas import (
    AccountCreateForOrganization,
    AccountCreateForOrganizationPaystack,
    AccountLink,
    AccountUpdate,
    BankAccountVerified,
    BankAccountVerifyRequest,
)


class AccountServiceError(SoleiError):
    pass


class AccountExternalIdDoesNotExist(AccountServiceError):
    def __init__(self, external_id: str) -> None:
        self.external_id = external_id
        message = f"No associated account exists with external ID {external_id}"
        super().__init__(message)


class CannotChangeAdminError(AccountServiceError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Cannot change account admin: {reason}")


class UserNotOrganizationMemberError(AccountServiceError):
    def __init__(self, user_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        super().__init__(
            f"User {user_id} is not a member of organization {organization_id}"
        )


class AccountService:
    async def get(
        self,
        session: AsyncReadSession,
        auth_subject: AuthSubject[User | Organization],
        id: uuid.UUID,
    ) -> Account | None:
        repository = AccountRepository.from_session(session)
        statement = (
            repository.get_readable_statement(auth_subject)
            .where(Account.id == id)
            .options(
                joinedload(Account.users),
                joinedload(Account.organizations),
            )
        )
        account = await repository.get_one_or_none(statement)

        return account

    async def _get_unrestricted(
        self,
        session: AsyncReadSession,
        id: uuid.UUID,
    ) -> Account | None:
        repository = AccountRepository.from_session(session)
        statement = (
            repository.get_base_statement()
            .where(Account.id == id)
            .options(
                joinedload(Account.users),
                joinedload(Account.organizations),
            )
        )
        return await repository.get_one_or_none(statement)

    async def is_user_admin(
        self, session: AsyncReadSession, account_id: uuid.UUID, user: User
    ) -> bool:
        account = await self._get_unrestricted(session, account_id)
        if account is None:
            return False
        return account.admin_id == user.id

    async def update(
        self, session: AsyncSession, account: Account, account_update: AccountUpdate
    ) -> Account:
        repository = AccountRepository.from_session(session)
        return await repository.update(
            account, update_dict=account_update.model_dump(exclude_unset=True)
        )

    async def delete(self, session: AsyncSession, account: Account) -> Account:
        repository = AccountRepository.from_session(session)
        return await repository.soft_delete(account)

    async def delete_stripe_account(
        self, session: AsyncSession, account: Account
    ) -> None:
        """Delete Stripe account and clear related database fields."""
        if not account.stripe_id:
            raise AccountServiceError("Account does not have a Stripe ID")

        # Verify the account exists on Stripe before deletion
        if not await stripe.account_exists(account.stripe_id):
            raise AccountServiceError(
                f"Stripe Account ID {account.stripe_id} doesn't exist"
            )

        # Delete the account on Stripe
        await stripe.delete_account(account.stripe_id)

        # Clear Stripe account data from database
        account.stripe_id = None
        account.is_details_submitted = False
        account.is_charges_enabled = False
        account.is_payouts_enabled = False
        session.add(account)

    async def disconnect_stripe(
        self, session: AsyncSession, account: Account
    ) -> Account:
        if not account.stripe_id:
            raise AccountServiceError("Account does not have a Stripe ID")

        old_stripe_id = account.stripe_id

        archive_account = Account(
            status=account.status,
            admin_id=account.admin_id,
            account_type=account.account_type,
            stripe_id=old_stripe_id,
            email=account.email,
            country=account.country,
            currency=account.currency,
            is_details_submitted=account.is_details_submitted,
            is_charges_enabled=account.is_charges_enabled,
            is_payouts_enabled=account.is_payouts_enabled,
            business_type=account.business_type,
            data=account.data,
            processor_fees_applicable=account.processor_fees_applicable,
            _platform_fee_percent=account._platform_fee_percent,
            _platform_fee_fixed=account._platform_fee_fixed,
            next_review_threshold=account.next_review_threshold,
            campaign_id=account.campaign_id,
        )
        archive_account.set_deleted_at()
        session.add(archive_account)
        await session.flush()

        account.stripe_id = None
        session.add(account)

        return archive_account

    async def verify_bank_account(
        self, bank_verify: BankAccountVerifyRequest
    ) -> BankAccountVerified:
        country = bank_verify.country
        ba = bank_verify.bank_account
        try:
            if country in ("NG", "GH"):
                result = await paystack_service.resolve_bank_account(
                    ba.account_number, ba.bank_code
                )
                return BankAccountVerified(
                    account_name=result["account_name"],
                    account_number=result["account_number"],
                )
            else:  # ZA
                await paystack_service.validate_bank_account(
                    account_number=ba.account_number,
                    bank_code=ba.bank_code,
                    account_name=ba.account_name or "",
                    account_type=ba.account_type or "personal",
                    country_code=country,
                    document_type=ba.document_type or "identityNumber",
                    document_number=ba.document_number or "",
                )
                return BankAccountVerified(
                    account_name=ba.account_name or "",
                    account_number=ba.account_number,
                )
        except PaystackError as e:
            raise AccountServiceError(str(e)) from e

    async def create_account(
        self,
        session: AsyncSession,
        *,
        admin: User,
        account_create: AccountCreateForOrganization
        | AccountCreateForOrganizationPaystack,
    ) -> Account:
        if isinstance(account_create, AccountCreateForOrganizationPaystack):
            account = await self._create_paystack_account(
                session, admin, account_create
            )
        else:
            account = await self._create_stripe_account(session, admin, account_create)
        await loops_service.user_created_account(
            session, admin, accountType=account.account_type
        )
        return account

    async def _create_paystack_account(
        self,
        session: AsyncSession,
        admin: User,
        account_create: AccountCreateForOrganizationPaystack,
    ) -> Account:
        ba = account_create.bank_account

        # Verify the bank account via Paystack before creating
        try:
            if account_create.country in ("NG", "GH"):
                resolved = await paystack_service.resolve_bank_account(
                    ba.account_number, ba.bank_code
                )
                account_name = resolved["account_name"]
            else:  # ZA
                await paystack_service.validate_bank_account(
                    account_number=ba.account_number,
                    bank_code=ba.bank_code,
                    account_name=ba.account_name or "",
                    account_type=ba.account_type or "personal",
                    country_code=account_create.country,
                    document_type=ba.document_type or "identityNumber",
                    document_number=ba.document_number or "",
                )
                account_name = ba.account_name or ""
        except PaystackError as e:
            raise AccountServiceError(str(e)) from e

        repository = AccountRepository.from_session(session)
        currency = {"ZA": "zar", "GH": "ghs", "NG": "ngn"}.get(
            account_create.country, "usd"
        )
        account = await repository.create(
            Account(
                account_type=AccountType.paystack,
                admin_id=admin.id,
                country=account_create.country,
                currency=currency,
                is_details_submitted=True,
                is_charges_enabled=False,
                is_payouts_enabled=True,
                email=admin.email,
                paystack_recipient_code=None,
                data={"bank_account": ba.model_dump(), "account_name": account_name},
            ),
            flush=True,
        )
        return account

    async def get_or_create_account_for_organization(
        self,
        session: AsyncSession,
        organization: Organization,
        admin: User,
        account_create: AccountCreateForOrganization
        | AccountCreateForOrganizationPaystack,
    ) -> Account:
        """Get existing account for organization or create a new one.

        If organization already has an account:
        - If account has no stripe_id (deleted), create new Stripe account
        - Otherwise return existing account

        If organization has no account, create new one and link it.
        """

        # Check if organization already has an account
        if organization.account_id:
            repository = AccountRepository.from_session(session)
            account = await repository.get_by_id(
                organization.account_id,
                options=(
                    joinedload(Account.users),
                    joinedload(Account.organizations),
                ),
            )

            if (
                account
                and not account.stripe_id
                and not isinstance(account_create, AccountCreateForOrganizationPaystack)
            ):
                assert account_create.account_type == AccountType.stripe
                try:
                    stripe_account = await stripe.create_account(
                        account_create, name=None
                    )
                except stripe_lib.StripeError as e:
                    if e.user_message:
                        raise AccountServiceError(e.user_message) from e
                    else:
                        raise AccountServiceError(
                            "An unexpected Stripe error happened"
                        ) from e

                # Update account with new Stripe details
                account.stripe_id = stripe_account.id
                account.email = stripe_account.email
                if stripe_account.country is not None:
                    account.country = stripe_account.country
                assert stripe_account.default_currency is not None
                account.currency = stripe_account.default_currency
                account.is_details_submitted = stripe_account.details_submitted or False
                account.is_charges_enabled = stripe_account.charges_enabled or False
                account.is_payouts_enabled = stripe_account.payouts_enabled or False
                account.business_type = stripe_account.business_type
                account.data = stripe_account.to_dict()

                session.add(account)

                await loops_service.user_created_account(
                    session, admin, accountType=account.account_type
                )

                return account
            elif account:
                return account

        # No account exists, create new one
        account = await self.create_account(
            session, admin=admin, account_create=account_create
        )

        # Link account to organization. Import happens here to avoid circular dependency
        from solei.organization.service import organization as organization_service

        await organization_service.set_account(
            session,
            auth_subject=AuthSubject(subject=admin, scopes=set(), session=None),
            organization=organization,
            account_id=account.id,
        )

        await session.refresh(account, {"users", "organizations"})

        return account

    async def _build_stripe_account_name(
        self, session: AsyncSession, account: Account
    ) -> str | None:
        # The account name is visible for users and is used to differentiate accounts
        # from the same Platform ("Solei") in Stripe Express.
        await session.refresh(account, {"users", "organizations"})
        associations = []
        for user in account.users:
            associations.append(f"user/{user.email}")
        for organization in account.organizations:
            associations.append(f"org/{organization.slug}")
        return "·".join(associations)

    async def _create_stripe_account(
        self,
        session: AsyncSession,
        admin: User,
        account_create: AccountCreateForOrganization,
    ) -> Account:
        try:
            stripe_account = await stripe.create_account(
                account_create, name=None
            )  # TODO: name
        except stripe_lib.StripeError as e:
            if e.user_message:
                raise AccountServiceError(e.user_message) from e
            else:
                raise AccountServiceError("An unexpected Stripe error happened") from e

        account = Account(
            status=Account.Status.ONBOARDING_STARTED,
            admin_id=admin.id,
            account_type=account_create.account_type,
            stripe_id=stripe_account.id,
            email=stripe_account.email,
            country=stripe_account.country,
            currency=stripe_account.default_currency,
            is_details_submitted=stripe_account.details_submitted,
            is_charges_enabled=stripe_account.charges_enabled,
            is_payouts_enabled=stripe_account.payouts_enabled,
            business_type=stripe_account.business_type,
            data=stripe_account.to_dict(),
            users=[],
            organizations=[],
        )

        campaign = await campaign_service.get_eligible(session, admin)
        if campaign:
            account.campaign_id = campaign.id
            account._platform_fee_percent = campaign.fee_percent
            account._platform_fee_fixed = campaign.fee_fixed

        session.add(account)
        await session.flush()

        # Create fee credits from campaign if applicable
        if campaign and campaign.fee_credit:
            await account_credit_service.grant_from_campaign(
                session,
                account=account,
                campaign=campaign,
            )

        return account

    async def update_account_from_stripe(
        self, session: AsyncSession, *, stripe_account: stripe_lib.Account
    ) -> Account:
        repository = AccountRepository.from_session(session)
        account = await repository.get_by_stripe_id(stripe_account.id)
        if account is None:
            raise AccountExternalIdDoesNotExist(stripe_account.id)

        account.email = stripe_account.email
        assert stripe_account.default_currency is not None
        account.currency = stripe_account.default_currency
        account.is_details_submitted = stripe_account.details_submitted or False
        account.is_charges_enabled = stripe_account.charges_enabled or False
        account.is_payouts_enabled = stripe_account.payouts_enabled or False
        if stripe_account.country is not None:
            account.country = stripe_account.country
        account.data = stripe_account.to_dict()

        session.add(account)

        # Update organization status based on Stripe account capabilities
        # Import here to avoid circular imports
        from solei.organization.service import organization as organization_service

        await organization_service.update_status_from_stripe_account(session, account)

        return account

    async def onboarding_link(
        self, account: Account, return_path: str
    ) -> AccountLink | None:
        if account.account_type == AccountType.stripe:
            assert account.stripe_id is not None
            account_link = await stripe.create_account_link(
                account.stripe_id, return_path
            )
            return AccountLink(url=account_link.url)

        return None

    async def dashboard_link(self, account: Account) -> AccountLink | None:
        if account.account_type == AccountType.stripe:
            assert account.stripe_id is not None
            account_link = await stripe.create_login_link(account.stripe_id)
            return AccountLink(url=account_link.url)

        return None

    async def sync_to_upstream(self, session: AsyncSession, account: Account) -> None:
        if account.account_type != AccountType.stripe:
            return

        if not account.stripe_id:
            return

        name = await self._build_stripe_account_name(session, account)
        await stripe.update_account(account.stripe_id, name)

    async def change_admin(
        self,
        session: AsyncSession,
        account: Account,
        new_admin_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Account:
        if account.stripe_id:
            raise CannotChangeAdminError(
                "Stripe account must be deleted before changing admin"
            )

        user_repository = UserRepository.from_session(session)
        is_member = await user_repository.is_organization_member(
            new_admin_id, organization_id
        )

        if not is_member:
            raise UserNotOrganizationMemberError(new_admin_id, organization_id)

        new_admin_user = await user_repository.get_by_id(new_admin_id)

        if new_admin_user is None:
            raise UserNotOrganizationMemberError(new_admin_id, organization_id)

        if (
            new_admin_user.identity_verification_status
            != IdentityVerificationStatus.verified
        ):
            raise CannotChangeAdminError(
                f"New admin must be verified in Stripe. Current status: {new_admin_user.identity_verification_status.get_display_name()}"
            )

        if account.admin_id == new_admin_id:
            raise CannotChangeAdminError("New admin is the same as current admin")

        repository = AccountRepository.from_session(session)
        account = await repository.update(
            account, update_dict={"admin_id": new_admin_id}
        )

        return account


account = AccountService()
