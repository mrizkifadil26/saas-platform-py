from __future__ import annotations

import pytest


class FakeUnitOfWork:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> FakeUnitOfWork:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.mark.asyncio
async def test_transaction_mtest_uow_commits_when_block_succeedsanager_commits_when_no_exception() -> (
    None
):
    uow = FakeUnitOfWork()

    async with uow:
        pass

    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.asyncio
async def test_uow_rolls_back_when_block_fails() -> None:
    uow = FakeUnitOfWork()

    with pytest.raises(RuntimeError):
        async with uow:
            raise RuntimeError("fail")

    assert uow.committed is False
    assert uow.rolled_back is True
