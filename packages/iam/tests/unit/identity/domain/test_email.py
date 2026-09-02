import pytest

from iam.identity.domain.value_objects import Email
from iam.shared.domain.exceptions import ValidationError
from tests.contracts.domain.string_value_object import (
    assert_rejects_empty,
    assert_trims_whitespace,
    assert_valid_string_value_object,
)


class TestEmail:
    def test_string_value_object_contract(self) -> None:
        assert_valid_string_value_object(
            Email,
            "user@example.com",
        )

        assert_trims_whitespace(
            Email,
            "user@example.com",
        )

        assert_rejects_empty(
            Email,
            ValidationError,
            "Email address cannot be empty",
        )

    def test_normalizes_lowercase(self) -> None:
        email = Email(
            "USER@Example.COM",
        )

        assert email.value == "user@example.com"

    def test_raises_when_empty(self) -> None:
        with pytest.raises(
            ValidationError,
            match="Email address cannot be empty",
        ):
            Email("")

    @pytest.mark.parametrize(
        "value",
        [
            "invalid",
            "missing-at-sign.com",
            "@example.com",
            "user@",
            "user@example",
            "user @example.com",
            "user@example .com",
        ],
    )
    def test_raises_when_email_format_is_invalid(
        self,
        value: str,
    ) -> None:
        with pytest.raises(ValidationError):
            Email(value)

    def test_raises_when_email_exceeds_max_length(self) -> None:
        local = "a" * 64
        domain = "b" * 252

        value = f"{local}@{domain}.com"

        with pytest.raises(
            ValidationError,
            match="Email address too long",
        ):
            Email(value)

    def test_raises_when_local_part_exceeds_max_length(self) -> None:
        value = f"{'a' * 65}@example.com"

        with pytest.raises(
            ValidationError,
            match="Email local part exceeds maximum length",
        ):
            Email(value)

    def test_raises_when_domain_exceeds_max_length(self) -> None:
        domain = ("a" * 252) + ".com"
        value = f"user@{domain}"

        with pytest.raises(
            ValidationError,
            match="Email domain exceeds maximum length",
        ):
            Email(value)

    def test_accepts_local_part_at_max_length(self) -> None:
        value = f"{'a' * 64}@example.com"

        email = Email(value)

        assert email.value == value

    def test_accepts_domain_at_max_length(self) -> None:
        domain = ("a" * 251) + ".com"
        value = f"user@{domain}"

        email = Email(value)

        assert email.value == value

    def test_accepts_email_at_max_length(self) -> None:
        local = "a" * 64
        domain = "b" * 251

        value = f"{local}@{domain}.com"

        email = Email(value)

        assert email.value == value
