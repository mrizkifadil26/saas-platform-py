from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from identity.shared.infrastructure.outbox.message import OutboxMessage
from identity.shared.infrastructure.outbox.repository import OutboxPublisherRepository, OutboxWriter
from identity.shared.kernel.events import DomainEvent
from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .models import OutboxMessageModel


class SQLAlchemyOutboxRepository(
    OutboxWriter,
    OutboxPublisherRepository,
):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory

    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                model = self._to_model(message)

                session.add(model)

    async def add_all(
        self,
        messages: Sequence[OutboxMessage],
    ) -> None:
        async with self._session_factory() as session:
            async with session.begin():
                session.add_all(self._to_model(message) for message in messages)

    async def add_event(
        self,
        event: DomainEvent,
    ) -> None:
        raise NotImplementedError

    async def add_events(
        self,
        events: Sequence[DomainEvent],
    ) -> None:
        raise NotImplementedError

    async def claim_batch(
        self,
        *,
        limit: int,
        now: datetime,
        locked_until: datetime,
    ) -> Sequence[OutboxMessage]:
        stmt = (
            select(OutboxMessageModel)
            .where(
                OutboxMessageModel.published_at.is_(None),
                (
                    OutboxMessageModel.available_at.is_(None)
                    | (OutboxMessageModel.available_at <= now)
                ),
                (
                    OutboxMessageModel.locked_until.is_(None)
                    | (OutboxMessageModel.locked_until <= now)
                ),
            )
            .order_by(
                OutboxMessageModel.occurred_at,
                OutboxMessageModel.id,
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        for row in rows:
            row.locked_until = locked_until
            row.attempts += 1

        await self._session.flush()

        return [
            self._to_domain(row)  # force split
            for row in rows
        ]

    async def mark_published(
        self,
        message_id: UUID,
        *,
        published_at: datetime,
    ) -> bool:
        stmt = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.id == message_id,
                OutboxMessageModel.published_at.is_(None),
            )
            .values(
                published_at=published_at,
                locked_until=None,
            )
        )

        raw_result = await self._session.execute(stmt)

        result = cast(CursorResult[Any], raw_result)
        affected_rows: int = result.rowcount

        return affected_rows == 1

    async def mark_failed(
        self,
        message_id: UUID,
        *,
        error: str,
        retry_at: datetime,
    ) -> None:
        stmt = (
            update(OutboxMessageModel)
            .where(
                OutboxMessageModel.id == message_id,
            )
            .values(
                available_at=retry_at,
                locked_until=None,
                last_error=error,
            )
        )

        await self._session.execute(stmt)

    # TODO: add reschedule

    @staticmethod
    def _to_domain(
        model: OutboxMessageModel,
    ) -> OutboxMessage:
        return OutboxMessage(
            id=model.id,
            message_type=model.message_type,
            payload=model.payload,
            occurred_at=model.occurred_at,
            aggregate_type=model.aggregate_type,
            aggregate_id=model.aggregate_id,
            published_at=model.published_at,
            attempts=model.attempts,
            available_at=model.available_at,
            locked_until=model.locked_until,
        )

    @staticmethod
    def _to_model(
        message: OutboxMessage,
    ) -> OutboxMessageModel:
        return OutboxMessageModel(
            id=message.id,
            message_type=message.message_type,
            payload=message.payload,
            occurred_at=message.occurred_at,
            aggregate_type=message.aggregate_type,
            aggregate_id=message.aggregate_id,
            published_at=message.published_at,
            attempts=message.attempts,
            available_at=message.available_at,
            locked_until=message.locked_until,
            # correlation_id=message.correlation_id,
            # causation_id=message.causation_id,
        )


class SQLAlchemyOutboxWriter(OutboxWriter):
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(self, message: OutboxMessage) -> None:
        self._session.add(self._to_model(message))

    async def add_all(
        self,
        messages: Sequence[OutboxMessage],
    ) -> None:
        self._session.add_all(self._to_model(message) for message in messages)

    @staticmethod
    def _to_domain(
        model: OutboxMessageModel,
    ) -> OutboxMessage:
        return OutboxMessage(
            id=model.id,
            message_type=model.message_type,
            payload=model.payload,
            occurred_at=model.occurred_at,
            aggregate_type=model.aggregate_type,
            aggregate_id=model.aggregate_id,
            published_at=model.published_at,
            attempts=model.attempts,
            available_at=model.available_at,
            locked_until=model.locked_until,
        )

    @staticmethod
    def _to_model(
        message: OutboxMessage,
    ) -> OutboxMessageModel:
        return OutboxMessageModel(
            id=message.id,
            message_type=message.message_type,
            payload=message.payload,
            occurred_at=message.occurred_at,
            aggregate_type=message.aggregate_type,
            aggregate_id=message.aggregate_id,
            published_at=message.published_at,
            attempts=message.attempts,
            available_at=message.available_at,
            locked_until=message.locked_until,
            # correlation_id=message.correlation_id,
            # causation_id=message.causation_id,
        )
