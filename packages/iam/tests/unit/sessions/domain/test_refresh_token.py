from datetime import timedelta

from iam.sessions.domain import RefreshToken
from iam.sessions.domain.value_objects import (
    RefreshTokenHash,
    RefreshTokenId,
    SessionId,
)
from tests.factories.sessions import make_refresh_token
from tests.factories.shared import make_datetime


class TestRefreshTokenCreate:
    def test_create_creates_refresh_token(self) -> None:
        session_id = SessionId.generate()
        token_hash = RefreshTokenHash(
            "hashed-refresh-token",
        )
        created_at = make_datetime()
        expires_at = created_at + timedelta(days=15)

        token = RefreshToken.create(
            session_id=session_id,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
        )

        assert token.id is not None
        assert token.session_id == session_id
        assert token.token_hash == token_hash
        assert token.created_at == created_at
        assert token.expires_at == expires_at
        assert token.revoked_at is None
        assert token.replaced_by_token_id is None
        assert token.parent_token_id is None
        assert token.used_at is None

    def test_create_uses_parent_token_when_given(self) -> None:
        parent_token_id = RefreshTokenId.generate()

        token = RefreshToken.create(
            session_id=SessionId.generate(),
            token_hash=RefreshTokenHash(
                "hashed-refresh-token",
            ),
            created_at=make_datetime(),
            expires_at=make_datetime(day=16),
            parent_token_id=parent_token_id,
        )

        assert token.parent_token_id == parent_token_id


class TestRefreshTokenRevoked:
    def test_is_revoked_returns_false_when_not_revoked(self) -> None:
        token = make_refresh_token()

        assert token.is_revoked is False

    def test_is_revoked_returns_true_when_revoked(self) -> None:
        token = make_refresh_token(
            revoked_at=make_datetime(day=2),
        )

        assert token.is_revoked is True


class TestRefreshTokenExpired:
    def test_is_expired_returns_false_before_expiration(self) -> None:
        now = make_datetime()
        token = make_refresh_token(
            expires_at=now + timedelta(hours=1),
        )

        assert token.is_expired(now=now) is False

    def test_is_expired_returns_true_at_expiration(self) -> None:
        now = make_datetime()
        token = make_refresh_token(
            expires_at=now,
        )

        assert token.is_expired(now=now) is True

    def test_is_expired_returns_true_after_expiration(self) -> None:
        now = make_datetime()
        token = make_refresh_token(
            expires_at=now - timedelta(seconds=1),
        )

        assert token.is_expired(now=now) is True


class TestRefreshTokenActive:
    def test_is_active_returns_true_when_not_expired_or_revoked(self) -> None:
        now = make_datetime()

        token = make_refresh_token(
            expires_at=now + timedelta(days=1),
        )

        assert token.is_active(now=now) is True

    def test_is_active_returns_false_when_expired(self) -> None:
        now = make_datetime()

        token = make_refresh_token(
            expires_at=now,
        )

        assert token.is_active(now=now) is False

    def test_is_active_returns_false_when_revoked(self) -> None:
        now = make_datetime()

        token = make_refresh_token(
            expires_at=now + timedelta(days=1),
            revoked_at=now,
        )

        assert token.is_active(now=now) is False


class TestRefreshTokenRevoke:
    def test_revoke_sets_revoked_at(self) -> None:
        token = make_refresh_token()
        revoked_at = make_datetime(day=2)

        token.revoke(
            revoked_at=revoked_at,
        )

        assert token.revoked_at == revoked_at
        assert token.is_revoked is True

    def test_revoke_sets_replacement_token(self) -> None:
        token = make_refresh_token()
        replacement_id = RefreshTokenId.generate()
        revoked_at = make_datetime(day=2)

        token.revoke(
            revoked_at=revoked_at,
            replaced_by=replacement_id,
        )

        assert token.revoked_at == revoked_at
        assert token.replaced_by_token_id == replacement_id

    def test_revoke_does_nothing_when_already_revoked(self) -> None:
        first_revoked_at = make_datetime(day=2)
        replacement_id = RefreshTokenId.generate()

        token = make_refresh_token(
            revoked_at=first_revoked_at,
            replaced_by_token_id=replacement_id,
        )

        token.revoke(
            revoked_at=make_datetime(day=3),
            replaced_by=RefreshTokenId.generate(),
        )

        assert token.revoked_at == first_revoked_at
        assert token.replaced_by_token_id == replacement_id


class TestRefreshTokenMarkUsed:
    def test_mark_used_sets_used_at(self) -> None:
        token = make_refresh_token()
        used_at = make_datetime(day=2)

        token.mark_used(
            used_at=used_at,
        )

        assert token.used_at == used_at
