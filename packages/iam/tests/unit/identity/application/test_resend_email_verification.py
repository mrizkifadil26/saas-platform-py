from unittest.mock import Mock

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
    UserId,
)
from tests.factories.shared import make_datetime
from tests.support.fakes.clock import FakeClock
from tests.support.fakes.user_repository import InMemoryUserRepository
from tests.support.fakes.verification_repository import (
    InMemoryEmailVerificationRepository,
)


@pytest.mark.asyncio
async def test_should_resend_email_verification():
    now = make_datetime()

    user_repository = InMemoryUserRepository()
    verification_repository = InMemoryEmailVerificationRepository()

    token_generator = Mock()
    token_hasher = Mock()

    raw_token = EmailVerificationToken("raw-token")
    hashed_token = EmailVerificationTokenHash("hashed-token")

    token_generator.generate.return_value = raw_token
    token_hasher.hash.return_value = hashed_token

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )
    await user_repository.save(user)

    use_case = ResendEmailVerificationUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    command = ResendEmailVerificationCommand(
        user_id=user.id.value,
    )

    await use_case.execute(command)

    token_generator.generate.assert_called_once()
    token_hasher.hash.assert_called_once_with(raw_token)

    saved_verification = await verification_repository.find_by_user_id(
        user.id,
    )

    assert saved_verification is not None
    assert saved_verification.user_id == user.id
    assert saved_verification.token_hash == hashed_token


@pytest.mark.asyncio
async def test_should_raise_when_email_already_verified():
    now = make_datetime()

    user_repository = InMemoryUserRepository()
    verification_repository = InMemoryEmailVerificationRepository()

    token_generator = Mock()
    token_hasher = Mock()

    user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )
    user.mark_email_as_verified(verified_at=now)
    await user_repository.save(user)

    use_case = ResendEmailVerificationUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    command = ResendEmailVerificationCommand(
        user_id=user.id.value,
    )

    with pytest.raises(
        UserEmailAlreadyVerifiedError,
    ):
        await use_case.execute(command)

    token_generator.generate.assert_not_called()
    token_hasher.hash.assert_not_called()

    verification = await verification_repository.find_by_user_id(
        user.id,
    )

    assert verification is None


@pytest.mark.asyncio
async def test_should_raise_when_user_not_found():
    now = make_datetime()

    user_repository = InMemoryUserRepository()
    verification_repository = InMemoryEmailVerificationRepository()

    token_generator = Mock()
    token_hasher = Mock()

    use_case = ResendEmailVerificationUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    command = ResendEmailVerificationCommand(
        user_id=UserId.generate().value,
    )

    with pytest.raises(
        UserNotFoundError,
    ):
        await use_case.execute(command)

    token_generator.generate.assert_not_called()
    token_hasher.hash.assert_not_called()
