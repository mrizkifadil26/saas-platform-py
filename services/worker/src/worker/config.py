from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class WorkerConfig:
    queue: str = "default"
    concurrency: int = 4
    reserve_timeout: int = 5
    ttr: int = 60
    priority: int = 2**31
    dead_letter_queue: str = "dead_letter"

    @staticmethod
    def from_env() -> WorkerConfig:
        return WorkerConfig(
            queue=os.getenv("WORKER_QUEUE", "default"),
            concurrency=int(os.getenv("WORKER_CONCURRENCY", "4")),
            reserve_timeout=int(os.getenv("WORKER_RESERVE_TIMEOUT", "5")),
            ttr=int(os.getenv("WORKER_TTR", "60")),
            priority=int(os.getenv("WORKER_PRIORITY", str(2**31))),
            dead_letter_queue=os.getenv("WORKER_DEAD_LETTER_QUEUE", "dead_letter"),
        )