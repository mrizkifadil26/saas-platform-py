from datetime import timedelta
from unittest.mock import Mock

import pytest

from iam.identity.application import RegisterUserCommand, RegisterUserUseCase
from iam.identity.application.exceptions import UserAlreadyExistsError
from iam.identity.domain import User
from iam.identity.domain.value_objects import Email
from tests.factories.shared import make_datetime
from tests.support.fakes.clock import FakeClock
from tests.support.fakes.user_repository import InMemoryUserRepository
from tests.support.fakes.verification_repository import (
    InMemoryEmailVerificationRepository,
)


@pytest.mark.asyncio
async def test_should_register_user():
    now = make_datetime()

    user_repository = InMemoryUserRepository()
    verification_repository = InMemoryEmailVerificationRepository()

    token_generator = Mock()
    token_generator.generate.return_value = "generated-token"

    token_hasher = Mock()
    token_hasher.hash.return_value = "hashed-token"

    use_case = RegisterUserUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    command = RegisterUserCommand(
        email="test@example.com",
    )
    result = await use_case.execute(command)

    stored = await user_repository.find_by_email(
        Email("test@example.com"),
    )

    # Domain state
    assert stored is not None
    assert stored.email == Email("test@example.com")
    assert stored.created_at == now
    assert stored.is_email_verified is False

    # Application result
    assert result.user.id == stored.id.value
    assert result.user.email == stored.email.value
    assert result.user.is_verified is False
    assert result.user.created_at == now

    assert result.email_verification_required is True
    assert result.verification_expires_at == now + timedelta(
        minutes=15,
    )


@pytest.mark.asyncio
async def test_should_raise_when_user_already_exists():
    now = make_datetime()

    user_repository = InMemoryUserRepository()
    verification_repository = InMemoryEmailVerificationRepository()

    existing_user = User.register(
        email=Email("test@example.com"),
        registered_at=now,
    )

    await user_repository.save(existing_user)

    token_generator = Mock()
    token_hasher = Mock()

    use_case = RegisterUserUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=FakeClock(now),
    )

    email = "test@example.com"
    command = RegisterUserCommand(
        email=email,
    )

    with pytest.raises(
        UserAlreadyExistsError,
        match=f"User already exists: {email}",
    ):
        await use_case.execute(command)

    token_generator.generate.assert_not_called()
    token_hasher.hash.assert_not_called()

    stored_users, total = await user_repository.list(
        limit=100,
        offset=0,
    )

    assert total == 1
    assert stored_users == [existing_user]
