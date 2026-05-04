from dataclasses import dataclass
from typing import Any, Optional, Protocol


@dataclass(frozen=True)
class ReservedJob:
    handle: Any  # opaque provider handle (Job, receipt handle, tag, id...)
    body: str
    queue: str  # tube/queue name


class TaskQueue(Protocol):
    """
    Provider-agnostic queue port.
    provider_job_id is whatever the provider uses (beanstalk job id, etc).
    """

    def put(
        self,
        queue: str,
        body: str,
        *,
        delay: int = 0,
        ttr: int = 60,
        priority: int = 2**31,
    ) -> Any: ...
    def reserve(self, queue: str, *, timeout: int = 5) -> Optional[ReservedJob]: ...
    def delete(self, handle: Any) -> None: ...
