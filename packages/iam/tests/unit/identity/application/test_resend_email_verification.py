from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from iam.identity.application import (
    ResendEmailVerificationCommand,
    ResendEmailVerificationUseCase,
)
from iam.identity.application.exceptions import UserNotFoundError
from iam.identity.application.use_cases import UserEmailAlreadyVerifiedError
from iam.identity.domain import User
from iam.identity.domain.value_objects import (
    Email,
    EmailVerificationToken,
    EmailVerificationTokenHash,
)


@pytest.mark.asyncio
async def test_should_resend_email_verification():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_generator = Mock()
    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    raw_token = EmailVerificationToken("raw-token")
    hashed_token = EmailVerificationTokenHash("hashed-token")

    token_generator.generate.return_value = raw_token
    token_hasher.hash.return_value = hashed_token

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )
    user_repository.find_by_id.return_value = user

    use_case = ResendEmailVerificationUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = ResendEmailVerificationCommand(
        user_id=user.id.value,
    )

    await use_case.execute(command)

    user_repository.find_by_id.assert_awaited_once_with(
        user.id,
    )
    token_generator.generate.assert_called_once()
    token_hasher.hash.assert_called_once_with(raw_token)

    verification_repository.save.assert_awaited_once()
    saved_verification = verification_repository.save.await_args.args[0]

    assert saved_verification.user_id == user.id
    assert saved_verification.token_hash == hashed_token


@pytest.mark.asyncio
async def test_should_raise_when_email_already_verified():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_generator = Mock()
    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    raw_token = EmailVerificationToken("raw-token")
    hashed_token = EmailVerificationTokenHash("hashed-token")

    token_generator.generate.return_value = raw_token
    token_hasher.hash.return_value = hashed_token

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )
    user.mark_email_as_verified(verified_at=now)
    user_repository.find_by_id.return_value = user

    use_case = ResendEmailVerificationUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = ResendEmailVerificationCommand(
        user_id=user.id.value,
    )

    with pytest.raises(UserEmailAlreadyVerifiedError):
        await use_case.execute(command)

    user_repository.find_by_id.assert_awaited_once_with(user.id)

    token_generator.generate.assert_not_called()
    token_hasher.hash.assert_not_called()

    verification_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_should_raise_when_user_not_found():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_generator = Mock()
    token_hasher = Mock()
    clock = Mock()

    now = datetime.now(UTC)
    clock.now.return_value = now

    raw_token = EmailVerificationToken("raw-token")
    hashed_token = EmailVerificationTokenHash("hashed-token")

    token_generator.generate.return_value = raw_token
    token_hasher.hash.return_value = hashed_token

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )
    # user_repository.find_by_id.return_value = user
    user_repository.find_by_id.return_value = None

    use_case = ResendEmailVerificationUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = ResendEmailVerificationCommand(
        user_id=user.id.value,
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(command)

    user_repository.find_by_id.assert_awaited_once_with(user.id)

    token_generator.generate.assert_not_called()
    token_hasher.hash.assert_not_called()

    verification_repository.save.assert_not_awaited()
