import uuid
from datetime import datetime
from typing import Protocol


class UserRecord(Protocol):
    id: uuid.UUID
    email: str
    fullname: str | None
    is_active: bool


class UserCredentialRecord(Protocol):
    user_id: uuid.UUID
    password_hash: str
    password_updated_at: datetime | None


class SessionRecord(Protocol):
    id: uuid.UUID
    workspace_id: uuid.UUID
    user_id: uuid.UUID
    token_hash: bytes
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None


class AuthUserRepoPort(Protocol):
    async def get_user_by_id(self, user_id: uuid.UUID) -> UserRecord | None: ...

    async def get_user_by_email(self, email: str) -> UserRecord | None: ...

    async def create_user(
        self,
        *,
        email: str,
        fullname: str | None = None,
    ) -> UserRecord: ...


class AuthCredentialRepoPort(Protocol):
    async def get_by_user_id(self, user_id: uuid.UUID) -> UserCredentialRecord | None: ...

    async def upsert_password_hash(
        self,
        *,
        user_id: uuid.UUID,
        password_hash: str,
        changed_at: datetime,
    ) -> UserCredentialRecord: ...


class AuthSessionRepoPort(Protocol):
    async def get_active_session_by_token_hash(
        self,
        token_hash: bytes,
    ) -> SessionRecord | None: ...

    async def create_session(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        token_hash: bytes,
        created_at: datetime,
        expires_at: datetime,
    ) -> SessionRecord: ...

    async def touch_last_session(
        self,
        session_id: uuid.UUID,
        when: datetime,
    ) -> bool: ...

    async def revoke_session(
        self,
        session_id: uuid.UUID,
        when: datetime,
    ) -> bool: ...


class AuthMembershipRepoPort(Protocol):
    async def has_workspace_access(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> bool: ...


class AuthUoWPort(Protocol):
    users: AuthUserRepoPort
    credentials: AuthCredentialRepoPort
    sessions: AuthSessionRepoPort
    memberships: AuthMembershipRepoPort

    async def __aenter__(self) -> "AuthUoWPort": ...

    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    async def flush(self) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
