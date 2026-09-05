from datetime import timedelta

MAX_ATTEMPTS = 10


def retry_delay(attempt: int) -> timedelta:
    seconds = min(
        2**attempt,
        3600,
    )

    return timedelta(
        seconds=seconds,
    )
