from decimal import Decimal
from re import Pattern


def normalize_text(
    value: str,
    *,
    strip: bool = True,
    lower: bool = False,
    upper: bool = False,
    collapse_spaces: bool = False,
) -> str:
    return ""


def require_not_empty(value: str, field: str) -> str:
    if not value:
        raise ValueError(f"{field} cannot be empty")

    return value


def require_length_between(
    value: str,
    *,
    field: str,
    min_length: int,
    max_length: int,
) -> str: ...


def require_regex(
    value: str,
    pattern: Pattern[str],
    field: str,
) -> str: ...


def require_positive_int(value: int, field: str) -> int: ...


def require_non_negative_decimal(
    value: Decimal,
    field: str,
) -> Decimal: ...
