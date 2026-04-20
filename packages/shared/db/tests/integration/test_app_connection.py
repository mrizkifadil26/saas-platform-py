import pytest
from db.uow.base import AsyncUnitOfWork


class FakeSession:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


@pytest.mark.asyncio
async def test_uow_commit():
    session = FakeSession()
    uow = AsyncUnitOfWork(session)

    await uow.commit()

    assert session.committed is True


@pytest.mark.asyncio
async def test_uow_rollback():
    session = FakeSession()
    uow = AsyncUnitOfWork(session)

    await uow.rollback()

    assert session.rolled_back is True
