from taskqueue import JobEnvelope
from typing import Callable, Dict
from .context import WorkerContext


Handler = Callable[[WorkerContext, JobEnvelope], None]


def noop(_ctx: WorkerContext, _job: JobEnvelope) -> None:
    return None


def registry() -> Dict[str, Handler]:
    return {"noop": noop}
