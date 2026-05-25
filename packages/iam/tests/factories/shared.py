from datetime import datetime, timezone


def make_datetime() -> datetime:
    return datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )
