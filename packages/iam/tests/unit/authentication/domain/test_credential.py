from typing import Any

import pytest

from iam.authentication.domain import Credential, CredentialStatus, CredentialType
from iam.authentication.domain.value_objects import PasswordHash
from iam.identity.domain.value_objects import UserId
from tests.factories.authentication import make_credential
from tests.factories.shared import make_datetime


class TestCredentialPassword:
    def test_password_creates_active_password_credential(self) -> None:
        user_id = UserId.generate()
        password_hash = PasswordHash("hashed-password")
        created_at = make_datetime()

        credential = Credential.password(
            user_id=user_id,
            secret_hash=password_hash,
            created_at=created_at,
        )

        assert credential.id is not None
        assert credential.user_id == user_id
        assert credential.type is CredentialType.PASSWORD
        assert credential.secret_hash == password_hash
        assert credential.status is CredentialStatus.ACTIVE
        assert credential.created_at == created_at
        assert credential.updated_at is None
        assert credential.attributes == {}

    def test_password_uses_given_attributes(self) -> None:
        attributes: dict[str, Any] = {
            "algorithm": "argon2",
            "version": 1,
        }

        credential = Credential.password(
            user_id=UserId.generate(),
            secret_hash=PasswordHash("hashed-password"),
            created_at=make_datetime(),
            attributes=attributes,
        )

        assert credential.attributes == attributes


class TestCredentialActive:
    def test_is_active_returns_true_when_active(self) -> None:
        credential = make_credential()

        assert credential.is_active is True

    @pytest.mark.parametrize(
        "status",
        [
            CredentialStatus.DISABLED,
            CredentialStatus.COMPROMISED,
        ],
    )
    def test_is_active_returns_false_when_not_active(
        self,
        status: CredentialStatus,
    ) -> None:
        credential = make_credential()
        credential.status = status

        assert credential.is_active is False


class TestCredentialChangePassword:
    def test_change_password_updates_hash_and_timestamp(self) -> None:
        credential = make_credential(
            secret_hash=PasswordHash("old-password-hash"),
        )
        new_hash = PasswordHash("new-password-hash")
        changed_at = make_datetime(day=2)

        credential.change_password(
            new_hash,
            at=changed_at,
        )

        assert credential.secret_hash == new_hash
        assert credential.updated_at == changed_at


class TestCredentialDisable:
    def test_disable_changes_status_and_timestamp(self) -> None:
        credential = make_credential()

        disabled_at = make_datetime(day=2)

        credential.disable(
            at=disabled_at,
        )

        assert credential.status is CredentialStatus.DISABLED
        assert credential.updated_at == disabled_at

    def test_disable_does_nothing_when_already_disabled(self) -> None:
        credential = make_credential()

        first_disabled_at = make_datetime(day=2)
        second_disabled_at = make_datetime(day=3)

        credential.disable(
            at=first_disabled_at,
        )
        credential.disable(
            at=second_disabled_at,
        )

        assert credential.status is CredentialStatus.DISABLED
        assert credential.updated_at == first_disabled_at


class TestCredentialMarkCompromised:
    def test_mark_compromised_changes_status_and_timestamp(self) -> None:
        credential = make_credential()

        compromised_at = make_datetime(day=2)
        credential.mark_compromised(
            at=compromised_at,
        )

        assert credential.status is CredentialStatus.COMPROMISED
        assert credential.updated_at == compromised_at


class TestCredentialEnsureActive:
    def test_ensure_active_does_nothing_when_active(self) -> None:
        credential = make_credential()

        credential.ensure_active()

    @pytest.mark.parametrize(
        "status",
        [
            CredentialStatus.DISABLED,
            CredentialStatus.COMPROMISED,
        ],
    )
    def test_ensure_active_raises_when_not_active(
        self,
        status: CredentialStatus,
    ) -> None:
        credential = make_credential()
        credential.status = status

        with pytest.raises(RuntimeError):
            credential.ensure_active()
