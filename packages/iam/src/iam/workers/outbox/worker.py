import logging
from dataclasses import dataclass

from iam.shared.infrastructure.outbox.relay import OutboxRelay
from iam.workers.worker import StopSignal, Worker

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class OutboxWorker(Worker):
    relay: OutboxRelay

    async def run(self, stop: StopSignal) -> None:
        logger.info("outbox relay worker started")

        try:
            await self.relay.run_forever(stop.event)
        finally:
            logger.info("outbox relay worker stopped")
