from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import OutboxMessageModel


class SQLAlchemyOutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def claim_batch(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.published_at.is_(None))
            .order_by(OutboxMessageModel.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            {
                "id": model.id,
                "topic": model.topic,
                "payload": model.payload,
                "created_at": model.created_at,
                "published_at": model.published_at,
                "attempts": model.attempts,
                "next_attempt_at": model.next_attempt_at,
                "locked_at": model.locked_at,
                "last_error": model.last_error,
            }
            for model in models
        ]

    async def mark_failed(self, message_id: UUID, error: str) -> None:
        message = await self._session.get(
            OutboxMessageModel,
            message_id,
        )

        if message is None:
            return

        message.attempts += 1
        message.last_error = error
        message.locked_at = None

        delay = min(
            60 * (2**message.attempts),
            3600,
        )

        message.next_attempt_at = datetime.now(UTC) + timedelta(seconds=delay)

        await self._session.commit()

    async def mark_published(self, message_id: UUID) -> None:
        message = await self._session.get(
            OutboxMessageModel,
            message_id,
        )

        if message is None:
            return

        message.published_at = datetime.now(UTC)
        message.locked_at = None

        await self._session.commit()
