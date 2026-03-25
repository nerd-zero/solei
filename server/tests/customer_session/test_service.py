import pytest
from sqlalchemy import select

from solei.auth.models import AuthSubject
from solei.customer_session.service import customer_session as customer_session_service
from solei.models import Member, Organization, User, UserOrganization
from solei.models.member import MemberRole
from solei.postgres import AsyncSession
from tests.fixtures.auth import AuthSubjectFixture
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_customer


@pytest.mark.asyncio
class TestCreateGracefulFallback:
    """Tests for graceful owner member auto-creation in customer session service."""

    @pytest.mark.auth(
        AuthSubjectFixture(subject="user"),
        AuthSubjectFixture(subject="organization"),
    )
    async def test_auto_creates_owner_member_for_customer_session(
        self,
        session: AsyncSession,
        save_fixture: SaveFixture,
        organization: Organization,
        user: User,
        user_organization: UserOrganization,
        auth_subject: AuthSubject[User | Organization],
    ) -> None:
        """When member_model enabled but customer has no owner member,
        auto-create one and return MemberSession."""
        organization.feature_settings = {"member_model_enabled": True}
        await save_fixture(organization)

        customer = await create_customer(
            save_fixture,
            organization=organization,
            email="no-member@example.com",
        )

        from solei.customer_session.schemas import CustomerSessionCustomerIDCreate

        create_schema = CustomerSessionCustomerIDCreate(
            customer_id=customer.id,
        )

        result = await customer_session_service.create(
            session, auth_subject, create_schema
        )

        # Should succeed — an owner member was auto-created
        assert result is not None

        # Verify the owner member was created
        stmt = select(Member).where(
            Member.customer_id == customer.id,
            Member.role == MemberRole.owner,
            Member.deleted_at.is_(None),
        )
        db_result = await session.execute(stmt)
        members = db_result.scalars().all()
        assert len(members) == 1
        assert members[0].email == "no-member@example.com"

    @pytest.mark.auth(
        AuthSubjectFixture(subject="user"),
        AuthSubjectFixture(subject="organization"),
    )
    async def test_returns_customer_session_when_flag_disabled(
        self,
        session: AsyncSession,
        save_fixture: SaveFixture,
        organization: Organization,
        user: User,
        user_organization: UserOrganization,
        auth_subject: AuthSubject[User | Organization],
    ) -> None:
        """When member_model disabled, should return CustomerSession (not MemberSession)."""
        # organization defaults to member_model_enabled=false
        customer = await create_customer(
            save_fixture,
            organization=organization,
            email="legacy@example.com",
        )

        from solei.customer_session.schemas import CustomerSessionCustomerIDCreate
        from solei.models import CustomerSession

        create_schema = CustomerSessionCustomerIDCreate(
            customer_id=customer.id,
        )

        result = await customer_session_service.create(
            session, auth_subject, create_schema
        )

        assert result is not None
        assert isinstance(result, CustomerSession)
