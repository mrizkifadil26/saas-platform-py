from datetime import UTC, datetime


def utc_now() -> datetime:
    """Timezone-aware UTC datetime"""
    return datetime.now(UTC)
