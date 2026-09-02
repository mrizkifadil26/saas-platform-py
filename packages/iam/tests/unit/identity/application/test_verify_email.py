from datetime import timedelta
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
    EmailVerificationToken,
    EmailVerificationTokenHash,
    UserId,
)
from tests.factories.shared import make_datetime
from tests.support.fakes.clock import FakeClock


@pytest.mark.asyncio
async def test_should_verify_user_email():
    now = make_datetime()

    user_repository = AsyncMock()
    verification_repository = AsyncMock()
    token_hasher = Mock()

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
        clock=FakeClock(now),
    )

    command = VerifyEmailCommand(
        token="raw-token",
    )
    result = await use_case.execute(command)

    assert result.email_verified is True
    assert user.is_email_verified is True

    token_hasher.hash.assert_called_once_with(
        EmailVerificationToken("raw-token"),
    )

    user_repository.save.assert_awaited_once_with(user)
    verification_repository.save.assert_awaited_once_with(verification)


@pytest.mark.asyncio
async def test_should_raise_when_token_invalid():
    now = make_datetime()

    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()

    hashed_token = EmailVerificationTokenHash("hashed-invalid-token")
    token_hasher.hash.return_value = hashed_token

    verification_repository.find_by_token_hash.return_value = None

    use_case = VerifyEmailUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    command = VerifyEmailCommand(
        token="invalid-token",
    )

    with pytest.raises(InvalidEmailVerificationTokenError):
        await use_case.execute(command)

    token_hasher.hash.assert_called_once_with(
        EmailVerificationToken("invalid-token"),
    )

    user_repository.find_by_id.assert_not_called()
    user_repository.save.assert_not_awaited()

    verification_repository.find_by_token_hash.assert_awaited_once_with(
        hashed_token,
    )
    verification_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_should_raise_when_verification_expired():
    now = make_datetime()

    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()
    hashed_token = EmailVerificationTokenHash("hashed-token")
    token_hasher.hash.return_value = hashed_token

    verification = EmailVerification.create(
        user_id=UserId.generate(),
        token_hash=hashed_token,
        created_at=now - timedelta(minutes=16),
        ttl_minutes=15,
    )
    verification_repository.find_by_token_hash.return_value = verification

    use_case = VerifyEmailUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    command = VerifyEmailCommand(
        token="raw-token",
    )

    with pytest.raises(EmailVerificationExpiredError):
        await use_case.execute(command)

    verification_repository.find_by_token_hash.assert_awaited_once_with(
        hashed_token,
    )

    user_repository.find_by_id.assert_not_awaited()
    user_repository.save.assert_not_awaited()
    verification_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_should_raise_when_user_not_found():
    now = make_datetime()

    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_hasher = Mock()
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
        clock=FakeClock(now),
    )

    command = VerifyEmailCommand(
        token="raw-token",
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(command)

    verification_repository.find_by_token_hash.assert_awaited_once_with(
        hashed_token,
    )

    user_repository.find_by_id.assert_awaited_once_with(
        verification.user_id,
    )

    user_repository.save.assert_not_awaited()
    verification_repository.save.assert_not_awaited()
