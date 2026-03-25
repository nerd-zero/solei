from fastapi import Depends, Query
from pydantic import UUID4

from solei.exceptions import ResourceNotFound
from solei.kit.pagination import ListResource, PaginationParamsQuery
from solei.kit.schemas import MultipleQueryFilter
from solei.models import OrganizationAccessToken
from solei.openapi import APITag
from solei.organization.schemas import OrganizationID
from solei.postgres import AsyncSession, get_db_session
from solei.routing import APIRouter

from . import sorting
from .auth import OrganizationAccessTokensRead, OrganizationAccessTokensWrite
from .schemas import (
    OrganizationAccessToken as OrganizationAccessTokenSchema,
)
from .schemas import (
    OrganizationAccessTokenCreate,
    OrganizationAccessTokenCreateResponse,
    OrganizationAccessTokenUpdate,
)
from .service import organization_access_token as organization_access_token_service

router = APIRouter(
    prefix="/organization-access-tokens",
    tags=["organization_access_tokens", APITag.public, APITag.mcp],
)


@router.get("/", response_model=ListResource[OrganizationAccessTokenSchema])
async def list(
    auth_subject: OrganizationAccessTokensRead,
    pagination: PaginationParamsQuery,
    sorting: sorting.ListSorting,
    organization_id: MultipleQueryFilter[OrganizationID] | None = Query(
        None, title="OrganizationID Filter", description="Filter by organization ID."
    ),
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[OrganizationAccessTokenSchema]:
    """List organization access tokens."""
    results, count = await organization_access_token_service.list(
        session,
        auth_subject,
        organization_id=organization_id,
        pagination=pagination,
        sorting=sorting,
    )

    return ListResource.from_paginated_results(
        [OrganizationAccessTokenSchema.model_validate(result) for result in results],
        count,
        pagination,
    )


@router.post("/", response_model=OrganizationAccessTokenCreateResponse, status_code=201)
async def create(
    organization_access_token_create: OrganizationAccessTokenCreate,
    auth_subject: OrganizationAccessTokensWrite,
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationAccessTokenCreateResponse:
    organization_access_token, token = await organization_access_token_service.create(
        session, auth_subject, organization_access_token_create
    )
    return OrganizationAccessTokenCreateResponse.model_validate(
        {
            "organization_access_token": organization_access_token,
            "token": token,
        }
    )


@router.patch("/{id}", response_model=OrganizationAccessTokenSchema)
async def update(
    id: UUID4,
    organization_access_token_update: OrganizationAccessTokenUpdate,
    auth_subject: OrganizationAccessTokensWrite,
    session: AsyncSession = Depends(get_db_session),
) -> OrganizationAccessToken:
    organization_access_token = await organization_access_token_service.get(
        session, auth_subject, id
    )
    if organization_access_token is None:
        raise ResourceNotFound()

    return await organization_access_token_service.update(
        session, organization_access_token, organization_access_token_update
    )


@router.delete("/{id}", status_code=204)
async def delete(
    id: UUID4,
    auth_subject: OrganizationAccessTokensWrite,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    organization_access_token = await organization_access_token_service.get(
        session, auth_subject, id
    )
    if organization_access_token is None:
        raise ResourceNotFound()

    await organization_access_token_service.delete(session, organization_access_token)
