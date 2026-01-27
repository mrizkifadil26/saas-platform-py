import asyncio
from typing import Dict
from taskqueue import (
    TaskQueue,
    ReservedJob,
    JobEnvelope,
    SupportsBury,
    should_bury,
    compute_delay_seconds,
)

from .config import WorkerConfig
from .handlers import Handler
from .context import WorkerContext


class AsyncWorkerCore:
    def __init__(
        self, q: TaskQueue, handlers: Dict[str, Handler], cfg: WorkerConfig, ctx: WorkerContext
    ):
        self.q = q
        self.handlers = handlers
        self.cfg = cfg
        self.ctx = ctx
        self.sem = asyncio.Semaphore(cfg.concurrency)
        self._stop = asyncio.Event()

    async def _deadletter(self, rj: ReservedJob, reason: str) -> None:
        dl_body = JobEnvelope(
            type="deadletter",
            payload={"reason": reason, "queue": rj.queue, "original": rj.body},
        ).to_json()

        await asyncio.to_thread(
            lambda: self.q.put(
                self.cfg.dead_letter_queue,
                dl_body,
                delay=0,
                ttr=self.cfg.ttr,
                priority=self.cfg.priority,
            )
        )
        await asyncio.to_thread(self.q.delete, rj.handle)

    async def _bury_or_deadletter(self, rj: ReservedJob, reason: str) -> None:
        if isinstance(self.q, SupportsBury):
            await asyncio.to_thread(self.q.bury, rj.handle)
        else:
            await self._deadletter(rj, reason)

    async def _process_one(self, rj: ReservedJob) -> None:
        async with self.sem:
            try:
                env = JobEnvelope.from_json(rj.body)
            except Exception:
                await self._bury_or_deadletter(rj, "invalid_json_or_schema")
                return

            handler = self.handlers.get(env.type)
            if handler is None:
                await self._bury_or_deadletter(rj, f"unknown_job_type:{env.type}")
                return

            try:
                handler(self.ctx, env)
                await asyncio.to_thread(self.q.delete, rj.handle)
            except Exception:
                if should_bury(env.retries, env.max_retries):
                    await self._bury_or_deadletter(rj, "handler_exception")
                    return

                delay = compute_delay_seconds(env.retries)
                next_env = env.bump_attempt()

                await asyncio.to_thread(
                    lambda: self.q.put(
                        rj.queue,
                        next_env.to_json(),
                        delay=int(delay),
                        ttr=self.cfg.ttr,
                        priority=self.cfg.priority,
                    )
                )

                await asyncio.to_thread(self.q.delete, rj.handle)

    async def tick(self) -> bool:
        rj = await asyncio.to_thread(
            lambda: self.q.reserve(self.cfg.queue, timeout=self.cfg.reserve_timeout)
        )
        if rj is None:
            return False

        asyncio.create_task(self._process_one(rj))
        return True

    async def run_forever(self) -> None:
        while not self._stop.is_set():
            await self.tick()
            await asyncio.sleep(0)  # yield to event loop

    def stop(self) -> None:
        self._stop.set()
