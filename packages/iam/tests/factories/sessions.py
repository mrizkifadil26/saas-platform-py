from datetime import datetime, timedelta

from iam.identity.domain.value_objects import UserId
from iam.sessions.domain import RefreshToken, Session, SessionStatus
from iam.sessions.domain.value_objects import (
    RefreshTokenHash,
    RefreshTokenId,
    SessionId,
)
from tests.factories.identity import make_user_id
from tests.factories.shared import make_datetime


def make_session(
    *,
    id: SessionId | None = None,
    user_id: UserId | None = None,
    status: SessionStatus = SessionStatus.ACTIVE,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    expires_at: datetime | None = None,
    last_activity_at: datetime | None = None,
    current_refresh_token_id: RefreshTokenId | None = None,
    revoked_at: datetime | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    device_name: str | None = None,
) -> Session:
    created_at = created_at or make_datetime()

    return Session(
        id=id or SessionId.generate(),
        user_id=user_id or make_user_id(),
        status=status,
        created_at=created_at,
        updated_at=updated_at or created_at,
        expires_at=expires_at or created_at + timedelta(days=30),
        last_activity_at=last_activity_at or created_at,
        current_refresh_token_id=current_refresh_token_id,
        revoked_at=revoked_at,
        ip_address=ip_address,
        user_agent=user_agent,
        device_name=device_name,
    )


def make_refresh_token(
    *,
    id: RefreshTokenId | None = None,
    session_id: SessionId | None = None,
    token_hash: RefreshTokenHash | None = None,
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
    revoked_at: datetime | None = None,
    replaced_by_token_id: RefreshTokenId | None = None,
    parent_token_id: RefreshTokenId | None = None,
    used_at: datetime | None = None,
) -> RefreshToken:
    created_at = created_at or make_datetime()

    return RefreshToken(
        id=id or RefreshTokenId.generate(),
        session_id=session_id or SessionId.generate(),
        token_hash=token_hash or RefreshTokenHash("hashed-refresh-token"),
        created_at=created_at,
        expires_at=expires_at or created_at + timedelta(days=15),
        revoked_at=revoked_at,
        replaced_by_token_id=replaced_by_token_id,
        parent_token_id=parent_token_id,
        used_at=used_at,
    )
