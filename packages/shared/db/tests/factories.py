# tests/factories.py
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Callable, Awaitable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from db.models.app_users.membership import Membership
from db.models.app_users.session import Session
from db.models.app_users.user import User
from db.models.app_users.workspace import Workspace
from db.repo.app_users.membership_repo import MembershipRepo
from db.repo.app_users.session_repo import SessionRepo
from db.repo.app_users.user_repo import UserRepo
from db.repo.app_users.workspace_repo import WorkspaceRepo


@dataclass
class Factories:
    user: Callable[..., Awaitable[User]]
    workspace: Callable[..., Awaitable[Workspace]]
    membership: Callable[..., Awaitable[Membership]]
    session: Callable[..., Awaitable[Session]]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def build_factories(db: AsyncSession) -> Factories:
    user_repo = UserRepo(db)
    ws_repo = WorkspaceRepo(db)
    membership_repo = MembershipRepo(db)
    session_repo = SessionRepo(db)

    async def make_user(
        *,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        if email is None:
            email = f"{uuid.uuid4()}@test.local"

        return await user_repo.create_user(email=email, fullname=full_name)

    async def make_workspace(
        *,
        name: str = "Test Workspace",
        slug: Optional[str] = None,
    ) -> Workspace:
        if slug is None:
            slug = f"ws-{uuid.uuid4()}"

        return await ws_repo.create_workspace(name=name, slug=slug)

    async def make_membership(
        *,
        user: Optional[User] = None,
        workspace: Optional[Workspace] = None,
        role: str = "member",
        status: str = "active",
    ) -> Membership:
        if user is None:
            user = await make_user()

        if workspace is None:
            workspace = await make_workspace()

        return await membership_repo.add_membership(
            user_id=user.id,
            workspace_id=workspace.id,
            role=role,
            status=status,
        )

    async def make_session(
        *,
        user: Optional[User] = None,
        workspace: Optional[Workspace] = None,
        token_hash: bytes = b"\x11" * 32,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ) -> Session:
        # satisfy FKs
        if user is None:
            user = await make_user()
        if workspace is None:
            workspace = await make_workspace()

        now = created_at or utcnow()
        exp = expires_at or (now + timedelta(days=1))

        return await session_repo.create_session(
            user_id=user.id,
            workspace_id=workspace.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=exp,
        )

    return Factories(
        user=make_user,
        workspace=make_workspace,
        membership=make_membership,
        session=make_session,
    )
