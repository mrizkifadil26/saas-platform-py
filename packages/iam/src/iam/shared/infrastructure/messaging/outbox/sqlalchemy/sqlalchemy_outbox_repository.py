from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from iam.shared.application.messaging.message import MessageEnvelope, MessageMetadata
from iam.shared.application.messaging.outbox import OutboxRepository
from iam.shared.application.messaging.outbox.message import OutboxMessage

from .models import OutboxMessageModel


class SQLAlchemyOutboxRepository(OutboxRepository):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(
        self,
        message: MessageEnvelope[Any],
    ) -> None:
        model = OutboxMessageModel(
            id=message.metadata.message_id,
            # TODO: should change it to more message type instead of just topic
            topic=message.message_type,
            payload=dict(message.payload),
            # occurred_at=message.occurred_at,
            # correlation_id=message.correlation_id,
            # causation_id=message.causation_id,
            attempts=0,
            # available_at=now,
        )

        self._session.add(model)

    async def claim(
        self,
        *,
        limit: int,
        worker_id: str,
        lease_until: datetime,
    ) -> Sequence[OutboxMessage]:
        now = datetime.now(UTC)

        stmt = (
            select(OutboxMessageModel)
            .where(
                OutboxMessageModel.published_at.is_(None),
                # TODO: should change it to available_at
                # OutboxModel.available_at <= now,
                OutboxMessageModel.created_at <= now,
                or_(
                    # TODO: should change into locked_until
                    # OutboxMessageModel.locked_until.is_(None),
                    # OutboxMessageModel.locked_until < now,
                    OutboxMessageModel.locked_at.is_(None),
                    OutboxMessageModel.locked_at < now,
                ),
            )
            .order_by(OutboxMessageModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        for row in rows:
            # TODO: add lease support
            # row.locked_by = worker_id
            # row.locked_until = lease_until
            row.locked_at = lease_until
            row.attempts += 1

        await self._session.commit()

        return [
            self._to_domain(row)  # force split
            for row in rows
        ]

    async def mark_published(
        self,
        *,
        message_id: UUID,
    ) -> None:
        now = datetime.now(UTC)

        stmt = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.id == message_id,
            )
            .values(
                # published_at=now,
                created_at=now,
                locked_until=None,
                locked_by=None,
                last_error=None,
            )
        )

        await self._session.execute(stmt)
        await self._session.commit()

    async def mark_failed(
        self,
        *,
        message_id: UUID,
        available_at: datetime,
        error: str,
    ) -> None:
        stmt = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.id == message_id,
            )
            .values(
                # available_at=available_at,
                next_attempt_at=available_at,
                locked_until=None,
                locked_by=None,
                last_error=error,
            )
        )

        await self._session.execute(stmt)
        await self._session.commit()

    @staticmethod
    def _to_domain(
        model: OutboxMessageModel,
    ) -> OutboxMessage:

        message = MessageEnvelope(
            # TODO: should explicitly stored it as message type
            message_type=model.topic,
            payload=model.payload,
            metadata=MessageMetadata(
                message_id=model.id,
                # TODO: should rename it to occurred_at
                occurred_at=model.created_at,
                # TODO: should implement this later
                # correlation_id=model.correlation_id,
                # causation_id=model.causation_id,
            ),
        )

        return OutboxMessage(
            message=message,
            attempts=model.attempts,
            # TODO: should replace it with available_at
            # available_at=model.available_at,
            available_at=model.created_at,
        )
