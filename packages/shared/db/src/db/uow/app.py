from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from packages.shared.db.src.db.repo.app.api_key_repo import APIKeyRepo
from packages.shared.db.src.db.repo.app.audit_repo import AuditRepo
from packages.shared.db.src.db.repo.app.entitlement_repo import EntitlementRepo
from packages.shared.db.src.db.repo.app.membership_repo import MembershipRepo
from packages.shared.db.src.db.repo.app.session_repo import SessionRepo
from packages.shared.db.src.db.repo.app.user_repo import UserRepo
from packages.shared.db.src.db.repo.app.workspace_repo import WorkspaceRepo
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@dataclass
class AppUoW:
    _sf: async_sessionmaker[AsyncSession]

    db: Optional[AsyncSession] = field(default=None, init=False, repr=False)

    _workspaces: WorkspaceRepo | None = field(default=None, init=False, repr=False)
    _users: UserRepo | None = field(default=None, init=False, repr=False)
    _memberships: MembershipRepo | None = field(default=None, init=False, repr=False)
    _api_keys: APIKeyRepo | None = field(default=None, init=False, repr=False)
    _entitlements: EntitlementRepo | None = field(default=None, init=False, repr=False)
    _audit: AuditRepo | None = field(default=None, init=False, repr=False)
    _sessions: SessionRepo | None = field(default=None, init=False, repr=False)

    async def __aenter__(self) -> AppUoW:
        self.db = self._sf()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        assert self.db is not None

        try:
            if exc_type is None:
                await self.db.commit()
            else:
                await self.db.rollback()
        finally:
            await self.db.close()

    def _require_db(self) -> AsyncSession:
        if self.db is None:
            raise RuntimeError("AppUsersUoW used outside of 'async with'")

        return self.db

    @property
    def workspaces(self) -> WorkspaceRepo:
        if self._workspaces is None:
            self._workspaces = WorkspaceRepo(self._require_db())

        return self._workspaces

    @property
    def users(self) -> UserRepo:
        if self._users is None:
            self._users = UserRepo(self._require_db())

        return self._users

    @property
    def memberships(self) -> MembershipRepo:
        if self._memberships is None:
            self._memberships = MembershipRepo(self._require_db())

        return self._memberships

    @property
    def api_keys(self) -> APIKeyRepo:
        if self._api_keys is None:
            self._api_keys = APIKeyRepo(self._require_db())

        return self._api_keys

    @property
    def entitlements(self) -> EntitlementRepo:
        if self._entitlements is None:
            self._entitlements = EntitlementRepo(self._require_db())

        return self._entitlements

    @property
    def audit(self) -> AuditRepo:
        if self._audit is None:
            self._audit = AuditRepo(self._require_db())

        return self._audit

    @property
    def sessions(self) -> SessionRepo:
        if self._sessions is None:
            self._sessions = SessionRepo(self._require_db())

        return self._sessions

    async def flush(self) -> None:
        await self._require_db().flush()

    async def commit(self) -> None:
        await self._require_db().commit()

    async def rollback(self) -> None:
        await self._require_db().rollback()
