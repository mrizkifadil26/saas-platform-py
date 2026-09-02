from datetime import timedelta

import pytest

from iam.sessions.domain import Session, SessionStatus
from iam.sessions.domain.value_objects import RefreshTokenHash
from tests.factories.identity import make_user_id
from tests.factories.sessions import make_refresh_token, make_session
from tests.factories.shared import make_datetime


class TestSessionCreate:
    def test_create_creates_active_session(self) -> None:
        user_id = make_user_id()
        created_at = make_datetime()

        session = Session.create(
            user_id=user_id,
            created_at=created_at,
        )

        assert session.id is not None
        assert session.user_id == user_id
        assert session.status is SessionStatus.ACTIVE
        assert session.created_at == created_at
        assert session.updated_at == created_at
        assert session.last_activity_at == created_at
        assert session.expires_at == created_at + timedelta(days=30)
        assert session.current_refresh_token_id is None
        assert session.revoked_at is None

    def test_create_uses_given_metadata(self) -> None:
        ip_address = "127.0.0.1"
        user_agent = "pytest"
        device_name = "test-device"

        session = Session.create(
            user_id=make_user_id(),
            created_at=make_datetime(),
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
        )

        assert session.ip_address == ip_address
        assert session.user_agent == user_agent
        assert session.device_name == device_name

    def test_create_sets_expiration_from_ttl(self) -> None:
        created_at = make_datetime()

        session = Session.create(
            user_id=make_user_id(),
            created_at=created_at,
            ttl_days=15,
        )

        assert session.expires_at == created_at + timedelta(days=15)


class TestSessionRevoked:
    def test_is_revoked_returns_false_when_active(self) -> None:
        session = make_session(
            status=SessionStatus.ACTIVE,
        )

        assert session.is_revoked is False

    def test_is_revoked_returns_true_when_revoked(self) -> None:
        session = make_session(
            status=SessionStatus.REVOKED,
        )

        assert session.is_revoked is True


class TestSessionExpired:
    def test_is_expired_returns_false_before_expiration(self) -> None:
        now = make_datetime()
        session = make_session(
            expires_at=now + timedelta(hours=1),
        )

        assert session.is_expired(now) is False

    def test_is_expired_returns_true_at_expiration(self) -> None:
        now = make_datetime()
        session = make_session(
            expires_at=now,
        )

        assert session.is_expired(now) is True

    def test_is_expired_returns_true_after_expiration(self) -> None:
        now = make_datetime()
        session = make_session(
            expires_at=now - timedelta(seconds=1),
        )

        assert session.is_expired(now) is True


class TestSessionActive:
    def test_is_active_returns_true_when_active_and_not_expired(self) -> None:
        now = make_datetime()
        session = make_session(
            status=SessionStatus.ACTIVE,
            expires_at=now + timedelta(hours=1),
        )

        assert session.is_active(now) is True

    def test_is_active_returns_false_when_revoked(self) -> None:
        now = make_datetime()
        session = make_session(
            status=SessionStatus.REVOKED,
            expires_at=now + timedelta(hours=1),
        )

        assert session.is_active(now) is False

    def test_is_active_returns_false_when_expired(self) -> None:
        now = make_datetime()
        session = make_session(
            status=SessionStatus.ACTIVE,
            expires_at=now,
        )

        assert session.is_active(now) is False


class TestSessionAttachRefreshToken:
    def test_attach_refresh_token_updates_session(self) -> None:
        session = make_session()
        refresh_token = make_refresh_token(
            session_id=session.id,
        )
        now = make_datetime(day=2)

        session.attach_refresh_token(
            refresh_token.id,
            now=now,
        )

        assert session.current_refresh_token_id == refresh_token.id
        assert session.last_activity_at == now
        assert session.updated_at == now


class TestSessionRevoke:
    def test_revoke_changes_status_and_timestamp(self) -> None:
        session = make_session()
        revoked_at = make_datetime(day=2)

        session.revoke(
            revoked_at=revoked_at,
        )

        assert session.status is SessionStatus.REVOKED
        assert session.revoked_at == revoked_at
        assert session.updated_at == revoked_at
        assert session.is_revoked is True


class TestSessionRotateRefreshToken:
    def test_rotate_refresh_token_rotates_token(self) -> None:
        now = make_datetime(day=2)

        session = make_session(
            expires_at=now + timedelta(days=30),
        )
        current_token = make_refresh_token(
            session_id=session.id,
            expires_at=now + timedelta(days=15),
        )

        session.attach_refresh_token(
            current_token.id,
            now=make_datetime(),
        )

        new_token_hash = RefreshTokenHash(
            "new-hashed-refresh-token",
        )
        new_token = session.rotate_refresh_token(
            current_token=current_token,
            new_token_hash=new_token_hash,
            now=now,
            refresh_token_ttl=timedelta(days=15),
        )

        assert new_token.id != current_token.id
        assert new_token.session_id == session.id
        assert new_token.token_hash == new_token_hash
        assert new_token.created_at == now
        assert new_token.expires_at == now + timedelta(days=15)
        assert new_token.parent_token_id == current_token.id

        assert current_token.is_revoked is True
        assert current_token.revoked_at == now
        assert current_token.used_at == now
        assert current_token.replaced_by_token_id == new_token.id

        assert session.current_refresh_token_id == new_token.id
        assert session.last_activity_at == now
        assert session.updated_at == now

    def test_rotate_refresh_token_raises_when_session_revoked(self) -> None:
        now = make_datetime()

        session = make_session(
            status=SessionStatus.REVOKED,
            expires_at=now + timedelta(days=30),
            revoked_at=now,
        )

        current_token = make_refresh_token(
            session_id=session.id,
            expires_at=now + timedelta(days=15),
        )

        # TODO: replace with SessionRevokedError
        with pytest.raises(RuntimeError):
            session.rotate_refresh_token(
                current_token=current_token,
                new_token_hash=RefreshTokenHash(
                    "new-hashed-refresh-token",
                ),
                now=now,
                refresh_token_ttl=timedelta(days=15),
            )

        assert current_token.is_revoked is False
        assert current_token.used_at is None

    def test_rotate_refresh_token_raises_when_session_expired(self) -> None:
        now = make_datetime(day=2)

        session = make_session(
            status=SessionStatus.ACTIVE,
            expires_at=now,
        )

        current_token = make_refresh_token(
            session_id=session.id,
            expires_at=now + timedelta(days=15),
        )

        # TODO: replace with SessionExpiredError
        with pytest.raises(RuntimeError):
            session.rotate_refresh_token(
                current_token=current_token,
                new_token_hash=RefreshTokenHash(
                    "new-hashed-refresh-token",
                ),
                now=now,
                refresh_token_ttl=timedelta(days=15),
            )

        assert current_token.is_revoked is False
        assert current_token.used_at is None
