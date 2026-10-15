from datetime import UTC, datetime, timedelta
from uuid import uuid4

from iam.shared.application.messaging.publisher import MessagePublisher

from .repository import OutboxRepository


class OutboxPublisher:
    def __init__(
        self,
        repository: OutboxRepository,
        publisher: MessagePublisher,
    ) -> None:
        # TODO: put some validation stuff here
        self._repository = repository
        self._publisher = publisher

    async def publish(
        self,
        *,
        limit: int = 100,
        lease_duration: timedelta = timedelta(minutes=1),
    ) -> int:
        worker_id = str(uuid4())
        now = datetime.now(UTC)

        messages = await self._repository.claim(
            limit=limit,
            worker_id=worker_id,
            lease_until=now + lease_duration,
        )

        published = 0
        for outbox_message in messages:
            # try:
            await self._publisher.publish(outbox_message.message)
            # except RetryableError:
            # retry()
            # except PermanentError:
            # mark_failed()

            await self._repository.mark_published(
                message_id=outbox_message.message.metadata.message_id,
            )

            published += 1

        return published
