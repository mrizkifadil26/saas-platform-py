from collections import defaultdict, deque
from typing import Deque, Optional

from packages.taskqueue.src.taskqueue.port import ReservedJob


class _Job:
    provider_job_id: int
    body: str

class InMemoryTaskQueue:
    """
    Test queue. Supports delay semantics by putting delayed jobs into a side bucket
    and only releasing them when tick_delay() is called (keeps tests deterministic).
    """
    def __init__(self) -> None:
        self._queues: dict[str, Deque[_Job]] = defaultdict(deque)
        self._delayed: dict[str, Deque[_Job]] = defaultdict(deque)
        self._next_id = 1

        self.deleted: set[int] = set()

    def put(
        self,
        queue: str,
        body: str,
        *,
        delay: int = 0,
        ttr: int = 60,
        priority: int = 2**31,
    ) -> int:
        job = _Job()
        job.provider_job_id = self._next_id
        job.body = body
        self._next_id += 1

        if delay > 0:
            self._delayed[queue].append(job)
        else:
            self._queues[queue].append(job)

        return job.provider_job_id

    def tick_delay(self) -> None:
        """
        Release all delayed jobs into their respective queues.
        """
        for queue, jobs in self._delayed.items():
            while jobs:
                job = jobs.popleft()
                self._queues[queue].append(job)

    def reserve(self, queue: str, *, timeout: int = 5) -> Optional[ReservedJob]:
        if not self._queues[queue]:
            return None

        job = self._queues[queue].popleft()
        return ReservedJob(
            provider_job_id=job.provider_job_id,
            body=job.body,
            queue=queue,
        )
    
    def delete(self, provider_job_id: int) -> None:
        self.deleted.add(provider_job_id)