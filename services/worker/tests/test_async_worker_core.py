import pytest
import asyncio

from taskqueue import InMemoryTaskQueue, JobEnvelope
from worker.core import AsyncWorkerCore
from worker.config import WorkerConfig
from worker.context import WorkerContext


@pytest.mark.asyncio
async def test_success_deletes_handle():
    q = InMemoryTaskQueue()
    h = q.put("default", JobEnvelope(type="ok").to_json())

    called = {"n": 0}

    def ok_handler(_ctx, _env):
        called["n"] += 1

    cfg = WorkerConfig(queue="default", concurrency=1)
    ctx = WorkerContext(queue=q)
    w = AsyncWorkerCore(q=q, handlers={"ok": ok_handler}, cfg=cfg, ctx=ctx)

    assert await w.tick() is True
    await asyncio.sleep(0.1)

    assert called["n"] == 1
    assert h in q.deleted


@pytest.mark.asyncio
async def test_failure_retries_with_bumped_attempt():
    q = InMemoryTaskQueue()
    h = q.put("default", JobEnvelope(type="fail", retries=1, max_retries=3).to_json())

    def fail_handler(_ctx, _env):
        raise RuntimeError("boom")

    cfg = WorkerConfig(queue="default", concurrency=1)
    ctx = WorkerContext(queue=q)
    w = AsyncWorkerCore(q=q, handlers={"fail": fail_handler}, cfg=cfg, ctx=ctx)

    assert await w.tick() is True
    await asyncio.sleep(0.1)

    assert h in q.deleted
    assert q.reserve("default") is None

    q.tick_delay("default")
    rj = q.reserve("default")
    assert rj is not None
    env = JobEnvelope.from_json(rj.body)
    assert env.retries == 2
