from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from iam.identity.application import VerifyEmailCommand, VerifyEmailUseCase
from iam.identity.application.exceptions import (
    EmailVerificationExpiredError,
    InvalidEmailVerificationTokenError,
)
from iam.identity.application.use_cases import UserNotFoundError
from iam.identity.domain import EmailVerification, User
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationTokenHash,
    UserId,
)


@pytest.mark.asyncio
async def test_should_verify_user_email():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    hashed_token = EmailVerificationTokenHash("hashed-token")
    token_hasher.hash.return_value = hashed_token

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )

    verification = EmailVerification.create(
        user_id=user.id,
        token_hash=hashed_token,
        created_at=now,
        ttl_minutes=15,
    )
    verification_repository.find_by_token_hash.return_value = verification

    user_repository.find_by_id.return_value = user

    use_case = VerifyEmailUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = VerifyEmailCommand(
        token="raw-token",
    )
    result = await use_case.execute(command)

    assert result.email_verified is True

    user_repository.save.assert_awaited_once_with(user)
    verification_repository.save.assert_awaited_once_with(verification)


@pytest.mark.asyncio
async def test_should_raise_when_token_invalid():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    hashed_token = EmailVerificationTokenHash("hashed-invalid-token")
    token_hasher.hash.return_value = hashed_token

    verification_repository.find_by_token_hash.return_value = None

    use_case = VerifyEmailUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = VerifyEmailCommand(
        token="invalid-token",
    )

    with pytest.raises(InvalidEmailVerificationTokenError):
        await use_case.execute(command)

    verification_repository.find_by_token_hash.assert_awaited_once()

    user_repository.find_by_id.assert_not_called()

    user_repository.save.assert_not_awaited()
    verification_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_should_raise_when_verification_expired():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    hashed_token = EmailVerificationTokenHash("hashed-token")
    token_hasher.hash.return_value = hashed_token

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )

    verification = EmailVerification.create(
        user_id=user.id,
        token_hash=hashed_token,
        created_at=now - timedelta(minutes=16),
        ttl_minutes=15,
    )
    verification_repository.find_by_token_hash.return_value = verification

    user_repository.find_by_id.return_value = user

    use_case = VerifyEmailUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = VerifyEmailCommand(
        token="invalid-token",
    )

    with pytest.raises(EmailVerificationExpiredError):
        await use_case.execute(command)

    verification_repository.find_by_token_hash.assert_awaited_once()

    user_repository.find_by_id.assert_not_awaited()

    user_repository.save.assert_not_awaited()
    verification_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_should_raise_when_user_not_found():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    hashed_token = EmailVerificationTokenHash("hashed-token")
    token_hasher.hash.return_value = hashed_token

    verification = EmailVerification.create(
        user_id=UserId.generate(),
        token_hash=hashed_token,
        created_at=now,
        ttl_minutes=15,
    )
    verification_repository.find_by_token_hash.return_value = verification

    user_repository.find_by_id.return_value = None

    use_case = VerifyEmailUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = VerifyEmailCommand(
        token="invalid-token",
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(command)

    verification_repository.find_by_token_hash.assert_awaited_once()

    user_repository.find_by_id.assert_awaited_once_with(
        verification.user_id,
    )

    user_repository.save.assert_not_awaited()
    verification_repository.save.assert_not_awaited()
