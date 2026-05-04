from collections.abc import Awaitable, Callable
from typing import TypeVar

from iam.shared.application.unit_of_work import UnitOfWork

T = TypeVar("T")


async def transactional(
    unit_of_work: UnitOfWork,
    operation: Callable[[], Awaitable[T]],
) -> T:
    try:
        result = await operation()
        await unit_of_work.commit()
        return result
    except Exception:
        await unit_of_work.rollback()
        raise
