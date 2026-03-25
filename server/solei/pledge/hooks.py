from dataclasses import dataclass

from solei.kit.hook import Hook
from solei.models.pledge import Pledge
from solei.models.pledge_transaction import PledgeTransaction
from solei.postgres import AsyncSession


@dataclass
class PledgeHook:
    session: AsyncSession
    pledge: Pledge


@dataclass
class PledgePaidHook:
    session: AsyncSession
    pledge: Pledge
    transaction: PledgeTransaction


# pledge_created fires when the pledge state is set to created
# (not the same as created in the initiated state)
pledge_created: Hook[PledgeHook] = Hook()
pledge_disputed: Hook[PledgeHook] = Hook()
pledge_updated: Hook[PledgeHook] = Hook()
