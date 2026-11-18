from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from identity.shared.infrastructure.messaging.publisher import MessagePublisher
from identity.shared.infrastructure.time.clock import Clock

from .repository import OutboxPublisherRepository


class OutboxRetryPolicy(Protocol):
    def retry_at(
        self,
        *,
        attempts: int,
        now: datetime,
    ) -> datetime: ...


@dataclass(frozen=True, slots=True)
class PublishBatchResult:
    claimed: int
    published: int
    failed: int
    lost_leases: int


@dataclass(slots=True)
class OutboxPublisher:
    repository: OutboxPublisherRepository
    publisher: MessagePublisher
    retry_policy: OutboxRetryPolicy
    clock: Clock

    async def publish_batch(
        self,
        *,
        limit: int = 100,
        locked_until: datetime,
    ) -> PublishBatchResult:
        now = self.clock.now()

        messages = await self.repository.claim_batch(
            limit=limit,
            now=now,
            locked_until=locked_until,
        )

        published = 0
        failed = 0
        lost_leases = 0

        for message in messages:
            try:
                await self.publisher.publish(
                    message_id=message.id,
                    message_type=message.message_type,
                    payload=message.payload,
                )
            except Exception as exc:
                failed += 1

                retry_at = self.retry_policy.retry_at(
                    attempts=message.attempts,
                    now=self.clock.now(),
                )

                await self.repository.mark_failed(
                    message.id,
                    error=str(exc),
                    retry_at=retry_at,
                )
            else:
                acknowledged = await self.repository.mark_published(
                    message.id,
                    published_at=self.clock.now(),
                )

                if acknowledged:
                    published += 1
                else:
                    lost_leases += 1

        return PublishBatchResult(
            claimed=len(messages),
            published=published,
            failed=failed,
            lost_leases=lost_leases,
        )
