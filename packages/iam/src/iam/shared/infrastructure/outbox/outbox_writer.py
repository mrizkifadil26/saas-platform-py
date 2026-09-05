from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from iam.shared.infrastructure.outbox.models import OutboxMessageModel


class SQLAlchemyOutboxWriter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        *,
        id: UUID,
        topic: str,
        payload: dict[str, Any],
    ) -> None:
        message = OutboxMessageModel(
            id=id,
            topic=topic,
            payload=payload,
            created_at=datetime.now(UTC),
        )

        self.session.add(message)
