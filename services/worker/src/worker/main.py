import asyncio
import os

from .core import AsyncWorkerCore
from .config import WorkerConfig
from .context import WorkerContext
from .handlers import registry
from taskqueue_beanstalk import BeanstalkConfig, BeanstalkTaskQueue


async def main_async() -> None:
    cfg = WorkerConfig.from_env()

    host = os.getenv("BEANSTALK_HOST", "127.0.0.1")
    port = int(os.getenv("BEANSTALK_PORT", "11300"))

    q = BeanstalkTaskQueue(
        BeanstalkConfig(host=host, port=port),
    )
    ctx = WorkerContext(queue=q)

    worker = AsyncWorkerCore(q, handlers=registry(), cfg=cfg, ctx=ctx)
    await worker.run_forever()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
