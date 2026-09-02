from datetime import timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from iam.authentication.application.commands import AuthenticateUserCommand
from iam.authentication.application.use_cases import AuthenticateWithPasswordUseCase
from iam.authentication.domain.value_objects import AccessToken, PasswordHash
from iam.sessions.domain.value_objects import RefreshTokenHash, RefreshTokenSecret
from tests.factories.authentication import make_credential
from tests.factories.shared import make_datetime


@pytest.mark.asyncio
async def test_should_authenticate_with_valid_password() -> None:
    now = make_datetime()

    credential = make_credential(
        secret_hash=PasswordHash("hashed-password"),
    )

    credential_repository = AsyncMock()
    authentication_attempt_repository = AsyncMock()

    credential_verifier = Mock()
    policy = Mock()
    refresh_token_generator = Mock()
    refresh_token_hasher = Mock()
    access_token_issuer = Mock()

    clock = Mock()
    clock.now.return_value = now

    credential_repository.find_password_by_email.return_value = credential
    authentication_attempt_repository.count_recent_failures.return_value = 0

    policy.failure_window.return_value = timedelta(
        minutes=15,
    )

    credential_verifier.verify_password.return_value = True

    refresh_token_generator.generate.return_value = RefreshTokenSecret(
        "refresh-token-secret"
    )
    refresh_token_hasher.hash.return_value = RefreshTokenHash("refresh-token-hash")
    access_token_issuer.issue.return_value = AccessToken("access-token")

    use_case = AuthenticateWithPasswordUseCase(
        credential_repository=credential_repository,
        authentication_attempt_repository=authentication_attempt_repository,
        credential_verifier=credential_verifier,
        policy=policy,
        refresh_token_generator=refresh_token_generator,
        refresh_token_hasher=refresh_token_hasher,
        access_token_issuer=access_token_issuer,
        clock=clock,
    )

    command = AuthenticateUserCommand(
        email="test@example.com",
        password="password",
        ip_address="127.0.0.1",
        user_agent="pytest",
    )

    result = await use_case.execute(command)

    assert result.user_id == credential.user_id.value
    assert result.session_id is not None

    credential_repository.find_password_by_email.assert_awaited_once()
    authentication_attempt_repository.count_recent_failures.assert_awaited_once()
    authentication_attempt_repository.save.assert_awaited_once()

    policy.ensure_not_locked.assert_called_once_with(
        recent_failures=0,
    )

    credential_verifier.verify_password.assert_called_once_with(
        password="password",
        password_hash=credential.secret_hash,
    )

    refresh_token_generator.generate.assert_called_once_with()
    refresh_token_hasher.hash.assert_called_once()
    access_token_issuer.issue.assert_called_once()


def test_should_raise_when_credential_not_found() -> None: ...


def test_should_raise_when_authentication_is_locked() -> None: ...


def test_should_raise_when_password_is_invalid() -> None: ...


def test_should_record_attempt_when_password_is_invalid() -> None: ...
