from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Optional

from taskqueue.port import ReservedJob


@dataclass
class _Job:
    handle: int
    body: str


class InMemoryTaskQueue:
    """
    Test queue. Supports delay semantics by putting delayed jobs into a side bucket
    and only releasing them when tick_delay() is called (keeps tests deterministic).

    This queue also supports:
    - delete(handle): acknowledge/remove job
    - release(job, delay=...): re-enqueue the same body (optionally delayed)
    - bury(job): mark job as buried (not re-enqueued)
    """

    def __init__(self) -> None:
        self._queues: dict[str, Deque[_Job]] = defaultdict(deque)
        self._delayed: dict[str, Deque[_Job]] = defaultdict(deque)
        self._next_id = 1

        # Observability for tests
        self.deleted: set[int] = set()
        self.buried: set[int] = set()
        self.released: list[tuple[int, int]] = []  # (handle, delay)

    def put(
        self,
        queue: str,
        body: str,
        *,
        delay: int = 0,
        ttr: int = 60,
        priority: int = 2**31,
    ) -> int:
        handle = self._next_id
        self._next_id += 1

        job = _Job(handle=handle, body=body)

        if delay > 0:
            self._delayed[queue].append(job)
        else:
            self._queues[queue].append(job)

        return handle

    def tick_delay(self, queue: str) -> None:
        """
        Move all delayed jobs from the delayed queue to the active queue.
        This method processes all jobs that are waiting in the delayed queue for
        the specified queue and transfers them to the main task queue for execution.
        Args:
            queue (str): The name of the queue to process delayed jobs for.
        Returns:
            None
        """
        jobs = self._delayed[queue]
        while jobs:
            job = jobs.popleft()
            self._queues[queue].append(job)

    def reserve(self, queue: str, *, timeout: int = 5) -> Optional[ReservedJob]:
        if not self._queues[queue]:
            return None

        job = self._queues[queue].popleft()
        return ReservedJob(
            handle=job.handle,
            body=job.body,
            queue=queue,
        )

    def delete(self, handle: int) -> None:
        self.deleted.add(handle)

    # ---- Optional capabilities (portable semantics) ----
    def release(
        self, job: ReservedJob, *, delay: int = 0, priority: int = 2**31
    ) -> None:
        """
        Provider-like 'release': re-enqueue the same job body.
        For determinism, delayed release goes into the delayed bucket.
        """
        handle = int(job.handle)
        self.released.append((handle, delay))
        self.put(job.queue, job.body, delay=delay)

    def bury(self, job: ReservedJob, *, priority: int = 2**31) -> None:
        """
        Provider-like 'bury': job is considered dead-lettered and will not run again.
        """
        self.buried.add(int(job.handle))
