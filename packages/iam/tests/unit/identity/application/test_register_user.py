from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from iam.identity.application import RegisterUserCommand, RegisterUserUseCase
from iam.identity.application.exceptions import UserAlreadyExistsError


@pytest.mark.asyncio
async def test_should_register_user():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_generator = Mock()
    token_hasher = Mock()
    clock = Mock()

    now = datetime.fromisoformat("2026-05-23T10:00:00+00:00")
    clock.now.return_value = now

    user_repository.find_by_email.return_value = None

    token_generator.generate.return_value = "generated-token"
    token_hasher.hash.return_value = "hashed-token"

    use_case = RegisterUserUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = RegisterUserCommand(
        email="test@example.com",
    )
    result = await use_case.execute(command)

    assert result.user.email == "test@example.com"
    assert result.email_verification_required is True

    user_repository.save.assert_awaited_once()
    verification_repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_raise_when_user_already_exists():
    user_repository = AsyncMock()
    verification_repository = AsyncMock()

    token_generator = Mock()
    token_hasher = Mock()
    clock = Mock()

    now = datetime.fromisoformat("2026-05-23T10:00:00+00:00")
    clock.now.return_value = now

    existing_user = Mock()

    user_repository.find_by_email.return_value = existing_user

    use_case = RegisterUserUseCase(
        user_repository=user_repository,
        verification_repository=verification_repository,
        token_generator=token_generator,
        token_hasher=token_hasher,
        clock=clock,
    )

    command = RegisterUserCommand(
        email="test@example.com",
    )

    with pytest.raises(UserAlreadyExistsError):
        await use_case.execute(command)

    user_repository.save.assert_not_awaited()
    verification_repository.save.assert_not_awaited()
