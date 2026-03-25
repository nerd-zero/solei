import pytest_asyncio

from solei.locker import Locker
from solei.redis import Redis


@pytest_asyncio.fixture
async def locker(redis: Redis) -> Locker:
    return Locker(redis)
