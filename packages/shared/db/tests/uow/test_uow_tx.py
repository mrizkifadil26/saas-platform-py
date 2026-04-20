import uuid
from datetime import datetime, timedelta, timezone

import pytest
from db.models.app_users.session import Session
from db.models.app_users.user import User
from db.models.app_users.workspace import Workspace
from db.uow.app_users import AppUsersUoW
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

pytestmark = [pytest.mark.db, pytest.mark.asyncio]


async def test_uow_rolls_back_on_exception(
    sessionmaker: async_sessionmaker[AsyncSession],
):
    uow = AppUsersUoW(sessionmaker)
    token_hash = b"\x44" * 32
    now = datetime.now(timezone.utc)

    # Create FK parents in their own committed transaction,
    # so the UoW transaction can see them.
    user_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    async with sessionmaker() as s:
        s.add(User(id=user_id, email=f"{user_id}@test.local", fullname=None))
        s.add(Workspace(id=workspace_id, name="Test", slug=f"ws-{workspace_id}"))
        await s.commit()

    created_session_id: uuid.UUID | None = None

    with pytest.raises(RuntimeError):
        async with uow as tx:
            created = await tx.sessions.create_session(
                user_id=user_id,
                workspace_id=workspace_id,
                token_hash=token_hash,
                created_at=now,
                expires_at=now + timedelta(days=1),
            )

            created_session_id = created.id
            raise RuntimeError("boom")

    # Verify rollback: session row should not exist
    assert created_session_id is not None
    async with sessionmaker() as s:
        res = await s.execute(select(Session).where(Session.id == created_session_id))
        assert res.scalar_one_or_none() is None
