from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass, field

from db.repo.app_users.api_key_repo import APIKeyRepo
from db.repo.app_users.audit_repo import AuditRepo
from db.repo.app_users.entitlement_repo import EntitlementRepo
from db.repo.app_users.membership_repo import MembershipRepo
from db.repo.app_users.user_repo import UserRepo
from db.repo.app_users.workspace_repo import WorkspaceRepo


@dataclass
class AppUsersUoW:
    db: AsyncSession

    _workspaces: WorkspaceRepo | None = field(default=None, init=False, repr=False)
    _users: UserRepo | None = field(default=None, init=False, repr=False)
    _memberships: MembershipRepo | None = field(default=None, init=False, repr=False)
    _api_keys: APIKeyRepo | None = field(default=None, init=False, repr=False)
    _entitlements: EntitlementRepo | None = field(default=None, init=False, repr=False)
    _audit: AuditRepo | None = field(default=None, init=False, repr=False)

    @property
    def workspaces(self) -> WorkspaceRepo:
        if self._workspaces is None:
            self._workspaces = WorkspaceRepo(self.db)
        return self._workspaces
    
    @property
    def users(self) -> UserRepo:
        if self._users is None:
            self._users = UserRepo(self.db)
        return self._users
    
    @property
    def memberships(self) -> MembershipRepo:
        if self._memberships is None:
            self._memberships = MembershipRepo(self.db)
        return self._memberships
    
    @property
    def api_keys(self) -> APIKeyRepo:
        if self._api_keys is None:
            self._api_keys = APIKeyRepo(self.db)
        return self._api_keys
    
    @property
    def entitlements(self) -> EntitlementRepo:
        if self._entitlements is None:
            self._entitlements = EntitlementRepo(self.db)
        return self._entitlements
    
    @property
    def audit(self) -> AuditRepo:
        if self._audit is None:
            self._audit = AuditRepo(self.db)
        return self._audit

    async def flush(self) -> None:
        await self.db.flush()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()
