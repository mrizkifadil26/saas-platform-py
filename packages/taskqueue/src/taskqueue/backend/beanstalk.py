from dataclasses import dataclass
from typing import Optional

import greenstalk

from taskqueue.capabilities import (
    SupportsBury,
    ReservedJob,
    SupportsRelease,
)


@dataclass(frozen=True)
class BeanstalkConfig:
    host: str = "127.0.0.1"
    port: int = 11300


class BeanstalkTaskQueue(SupportsRelease, SupportsBury):
    """
    Implements TaskQueue port using Beanstalkd via greenstalk.
    """

    def __init__(self, config: BeanstalkConfig):
        self._client = greenstalk.Client((config.host, config.port))

        # Initialize connection to Beanstalkd server here
        # e.g., self.connection = beanstalkc.Connection(host=config.host, port=config.port)

    def put(
        self,
        queue: str,
        body: str,
        *,
        delay: int = 0,
        ttr: int = 60,
        priority: int = 0,
    ) -> int:
        self._client.use(queue)
        return int(self._client.put(body, priority=priority, delay=delay, ttr=ttr))

    def reserve(
        self,
        queue: str,
        *,
        timeout: int = 5,
    ) -> Optional[ReservedJob]:
        # NOTE: greenstalk.watch adds to watched set; be aware if you watch many queues.
        self._client.watch(queue)
        try:
            job: greenstalk.Job[str] = self._client.reserve(timeout=timeout)
        except greenstalk.TimedOutError:
            return None

        # job is a greenstalk.Job[str]
        return ReservedJob(
            handle=job,
            body=job.body,
            queue=queue,
        )

    def delete(self, handle: greenstalk.Job[str]) -> None:
        self._client.delete(handle)

    # ✅ Capability methods use the *Job object* via ReservedJob.handle
    def release(
        self,
        job: ReservedJob,
        *,
        delay: int = 0,
        priority: int = 2**31,
    ) -> None:
        self._client.release(job.handle, priority=priority, delay=delay)

    def bury(
        self,
        job: ReservedJob,
        *,
        priority: int = 2**31,
    ) -> None:
        self._client.bury(job.handle, priority=priority)
