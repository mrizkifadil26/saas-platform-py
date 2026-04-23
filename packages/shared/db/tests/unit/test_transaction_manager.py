from __future__ import annotations

import pytest


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeTransactionManager:
    def __init__(self, session: FakeSession) -> None:
        self._session = session

    async def __aenter__(self) -> FakeTransactionManager:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()


@pytest.mark.asyncio
async def test_transaction_manager_commits_when_no_exception() -> None:
    session = FakeSession()
    manager = FakeTransactionManager(session)

    async with manager:
        pass

    assert session.committed is True
    assert session.rolled_back is False


@pytest.mark.asyncio
async def test_transaction_manager_rolls_back_on_exception() -> None:
    session = FakeSession()
    manager = FakeTransactionManager(session)

    with pytest.raises(RuntimeError):
        async with manager:
            raise RuntimeError("boom")

    assert session.committed is False
    assert session.rolled_back is True
