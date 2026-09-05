import asyncio
from dataclasses import dataclass

from iam.shared.application.unit_of_work import UnitOfWork
from iam.shared.infrastructure.outbox.repository import SQLAlchemyOutboxRepository

from .dispatcher import OutboxDispatcher


@dataclass(slots=True)
class OutboxWorker:
    MAX_ATTEMPTS = 10

    dispatcher: OutboxDispatcher
    uow_factory: UnitOfWork

    async def run(self) -> None:
        while True:
            async with self.uow_factory:
                repository = SQLAlchemyOutboxRepository(self.uow_factory.session)
                messages = await repository.claim_batch(
                    limit=100,
                )

                if not messages:
                    await asyncio.sleep(1)
                    continue

                for message in messages:
                    try:
                        await self.dispatcher.dispatch(message)

                        await repository.mark_published(
                            message["id"],
                        )
                    except Exception as exc:
                        await repository.mark_failed(message["id"], error=str(exc))
