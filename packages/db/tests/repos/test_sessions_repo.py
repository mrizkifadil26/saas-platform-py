import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from db.repo.app_users.session_repo import SessionRepo
from tests.factories import Factories


pytestmark = [pytest.mark.db, pytest.mark.asyncio]


async def test_get_active_session_by_token_hash_returns_session(
    db_session: AsyncSession,
    factories: Factories,
):
    repo = SessionRepo(db_session)
    token_hash = b"\x11" * 32

    s = await factories.session(token_hash=token_hash)

    found = await repo.get_active_session_by_token_hash(token_hash)

    assert found is not None
    assert found.id == s.id


async def test_get_active_session_by_token_hash_ignores_revoked(
    db_session: AsyncSession,
    factories: Factories,
):
    repo = SessionRepo(db_session)
    now = datetime.now(timezone.utc)
    token_hash = b"\x22" * 32

    s = await factories.session(token_hash=token_hash)

    ok = await repo.revoke_session(s.id, when=now)
    assert ok is True

    found = await repo.get_active_session_by_token_hash(token_hash)
    assert found is None


async def test_get_active_session_by_token_hash_ignores_expired(
    db_session: AsyncSession,
    factories: Factories,
):
    repo = SessionRepo(db_session)
    now = datetime.now(timezone.utc)
    token_hash = b"\x33" * 32

    await factories.session(
        token_hash=token_hash,
        created_at=now - timedelta(days=1),
        expires_at=now - timedelta(seconds=1),
    )

    found = await repo.get_active_session_by_token_hash(token_hash)
    assert found is None
