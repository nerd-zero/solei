from typing import Annotated

from fastapi import Depends

from solei.exceptions import ResourceNotFound
from solei.kit.db.postgres import AsyncSession
from solei.kit.pagination import ListResource, PaginationParamsQuery
from solei.kit.sorting import Sorting, SortingGetter
from solei.models import Wallet
from solei.openapi import APITag
from solei.postgres import get_db_session
from solei.routing import APIRouter
from solei.wallet.schemas import WalletID, WalletNotFound

from .. import auth
from ..schemas.wallet import CustomerWallet
from ..service.wallet import customer_wallet as customer_wallet_service
from ..sorting.wallet import CustomerWalletSortProperty

router = APIRouter(prefix="/wallets", tags=["wallets", APITag.public])

ListSorting = Annotated[
    list[Sorting[CustomerWalletSortProperty]],
    Depends(SortingGetter(CustomerWalletSortProperty, ["-created_at"])),
]


@router.get("/", summary="List Wallets", response_model=ListResource[CustomerWallet])
async def list(
    auth_subject: auth.CustomerPortalUnionBillingRead,
    pagination: PaginationParamsQuery,
    sorting: ListSorting,
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[CustomerWallet]:
    """List wallets of the authenticated customer."""
    results, count = await customer_wallet_service.list(
        session,
        auth_subject,
        pagination=pagination,
        sorting=sorting,
    )

    return ListResource.from_paginated_results(
        [CustomerWallet.model_validate(result) for result in results],
        count,
        pagination,
    )


@router.get(
    "/{id}",
    summary="Get Wallet",
    response_model=CustomerWallet,
    responses={404: WalletNotFound},
)
async def get(
    id: WalletID,
    auth_subject: auth.CustomerPortalUnionBillingRead,
    session: AsyncSession = Depends(get_db_session),
) -> Wallet:
    """Get a wallet by ID for the authenticated customer."""
    wallet = await customer_wallet_service.get_by_id(session, auth_subject, id)

    if wallet is None:
        raise ResourceNotFound()

    return wallet
