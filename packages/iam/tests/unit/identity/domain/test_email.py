import pytest

from iam.identity.domain.value_objects import Email
from iam.shared.domain.exceptions import ValidationError


def test_should_normalize_email():
    email = Email("  TEST@EXAMPLE.COM ")

    assert email.value == "test@example.com"


def test_should_raise_when_email_invalid():
    with pytest.raises(ValidationError):
        Email("banana-cat")
