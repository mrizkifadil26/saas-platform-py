from collections.abc import Callable
from typing import TypeVar

import pytest

from iam.shared.domain.value_object import ValueObject

T = TypeVar(
    "T",
    bound=ValueObject[str],
)


def assert_valid_string_value_object(
    factory: Callable[[str], T],
    value: str,
) -> None:
    obj = factory(value)

    assert obj.value == value
    assert str(obj) == value


def assert_trims_whitespace(
    factory: Callable[[str], T],
    value: str,
) -> None:
    obj = factory(f"   {value}   ")

    assert obj.value == value


def assert_rejects_empty(
    factory: Callable[[str], T],
    exception_type: type[Exception],
    message: str,
) -> None:
    for value in ("", "   "):
        with pytest.raises(
            exception_type,
            match=message,
        ):
            factory(value)
