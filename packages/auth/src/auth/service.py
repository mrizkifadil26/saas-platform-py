"""Authentication use cases.

Orchestrates login, refresh, logout, and registration using ports, crypto,
and token minting. Designed for access token (JWT) + refresh token (opaque)
with optional refresh rotation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from auth import crypto
from auth.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    SessionExpired,
    SessionNotFound,
    SessionRevoked,
    UserInactive,
)
from auth.ports import AuthUoWPort
from auth.settings import AuthSettings
from auth.tokens import mint_access_token
from auth.types import TokenPair


def _utcnow() -> datetime:
    return datetime.now(UTC)


async def login(
    uow: AuthUoWPort,
    settings: AuthSettings,
    *,
    email: str,
    password: str,
    workspace_id: uuid.UUID,
) -> TokenPair:
    """Authenticate user with email/password and issue a token pair for the given workspace."""
    user = await uow.users.get_user_by_email(email)
    if user is None:
        raise InvalidCredentials("invalid email or password")
    if not user.is_active:
        raise UserInactive("account is inactive")

    cred = await uow.credentials.get_by_user_id(user.id)
    if cred is None or not crypto.verify_password(password, cred.password_hash):
        raise InvalidCredentials("invalid email or password")

    has_access = await uow.memberships.has_workspace_access(
        user_id=user.id,
        workspace_id=workspace_id,
    )
    if not has_access:
        raise InvalidCredentials("no access to this workspace")

    refresh_token = crypto.mint_refresh_token()
    token_hash = crypto.hash_refresh_token(refresh_token)
    now = _utcnow()
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)

    session = await uow.sessions.create_session(
        user_id=user.id,
        workspace_id=workspace_id,
        token_hash=token_hash,
        created_at=now,
        expires_at=expires_at,
    )

    access_token, access_exp = mint_access_token(
        settings=settings,
        user_id=user.id,
        workspace_id=workspace_id,
        session_id=session.id,
    )

    await uow.commit()
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_exp,
    )


async def refresh(
    uow: AuthUoWPort,
    settings: AuthSettings,
    refresh_token: str,
) -> TokenPair:
    """Issue a new token pair from a valid refresh token. Optionally rotates refresh token."""
    token_hash = crypto.hash_refresh_token(refresh_token)
    session = await uow.sessions.get_active_session_by_token_hash(token_hash)

    if session is None:
        raise SessionNotFound("session not found or no longer valid")
    if session.revoked_at is not None:
        raise SessionRevoked("session has been revoked")
    if session.expires_at <= _utcnow():
        raise SessionExpired("session has expired")

    now = _utcnow()
    next_refresh_token = refresh_token
    next_token_hash = token_hash
    session_id = session.id

    if settings.ROTATE_REFRESH_TOKENS:
        next_refresh_token = crypto.mint_refresh_token()
        next_token_hash = crypto.hash_refresh_token(next_refresh_token)
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
        new_session = await uow.sessions.create_session(
            user_id=session.user_id,
            workspace_id=session.workspace_id,
            token_hash=next_token_hash,
            created_at=now,
            expires_at=expires_at,
        )
        session_id = new_session.id
        await uow.sessions.revoke_session(session.id, now)

    await uow.sessions.touch_last_session(session_id, now)

    access_token, access_exp = mint_access_token(
        settings=settings,
        user_id=session.user_id,
        workspace_id=session.workspace_id,
        session_id=session_id,
    )

    await uow.commit()
    return TokenPair(
        access_token=access_token,
        refresh_token=next_refresh_token,
        access_expires_at=access_exp,
    )


async def logout(uow: AuthUoWPort, session_id: uuid.UUID) -> None:
    """Revoke the session (e.g. after verifying the access token and reading sid)."""
    await uow.sessions.revoke_session(session_id, _utcnow())
    await uow.commit()


async def register(
    uow: AuthUoWPort,
    *,
    email: str,
    password: str,
    fullname: str | None = None,
):
    """Create a new user and set their password. Raises if email already registered."""
    existing = await uow.users.get_user_by_email(email)
    if existing is not None:
        raise EmailAlreadyRegistered("email already registered")

    user = await uow.users.create_user(email=email, fullname=fullname)
    password_hash = crypto.hash_password(password)
    now = _utcnow()
    await uow.credentials.upsert_password_hash(
        user_id=user.id,
        password_hash=password_hash,
        changed_at=now,
    )

    await uow.commit()
    return user
