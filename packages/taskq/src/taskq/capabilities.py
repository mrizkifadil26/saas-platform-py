from typing import Protocol, runtime_checkable

from taskq.port import ReservedJob


@runtime_checkable
class SupportsBury(Protocol):
    def bury(self, job: ReservedJob, *, priority: int = 2**31) -> None: ...


@runtime_checkable
class SupportsRelease(Protocol):
    """
    IMPORTANT: release semantics are provider-specific.
    For portability, prefer delete+reenqueue in WorkerCore.
    """

    def release(
        self, job: ReservedJob, *, delay: int = 0, priority: int = 2**31
    ) -> None: ...


@runtime_checkable
class SupportsPeek(Protocol):
    def peek(self, job: ReservedJob) -> ReservedJob | None: ...


@runtime_checkable
class SupportsKick(Protocol):
    def kick(self, count: int = 1) -> int: ...


@runtime_checkable
class SupportsDelay(Protocol):
    """
    Provider supports delay natively, or the adapter emulates it.
    Compliance tests can check delay behavior when available.
    """

    pass
