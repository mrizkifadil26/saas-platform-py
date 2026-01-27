from dataclasses import dataclass
from taskqueue import TaskQueue

@dataclass(frozen=True)
class WorkerContext:
    queue: TaskQueue