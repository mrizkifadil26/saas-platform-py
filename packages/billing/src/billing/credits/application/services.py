import hashlib
import json

from billing.application.credits.commands import (
    ConsumeCreditsCommand,
)
from billing.application.credits.dto import (
    CreditConsumptionDTO,
    to_credit_consumption_dto,
)
from billing.application.credits.exceptions import (
    DuplicateRequestError,
    IdempotencyConflictError,
)
from billing.application.credits.interfaces import (
    CreditsApplicationUnitOfWork,
)
from billing.domain.credits.domain_services import (
    consume_credits,
)
from billing.domain.credits.value_objects import (
    ConsumptionId,
)
from billing.domain.shared.time import utc_now

from billing.shared.application.interfaces import (
    EventPublisher,
    IdempotencyStore,
)


class CreditsApplicationService:
    def __init__(
        self,
        uow: CreditsApplicationUnitOfWork,
        event_publisher: EventPublisher | None = None,
        idempotency_store: IdempotencyStore | None = None,
    ):
        self.uow = uow
        self.event_publisher = event_publisher
        self.idempotency_store = idempotency_store

    async def consume_credits(
        self,
        cmd: ConsumeCreditsCommand,
    ) -> CreditConsumptionDTO:
        now = cmd.now or utc_now()

        key = self._idempotency_key(
            user_id=str(cmd.user_id),
            request_id=str(cmd.request_id),
        )
        fingerprint = self._fingerprint(
            {
                "user_id": str(cmd.user_id),
                "cost": int(cmd.cost),
                "metadata": cmd.metadata or {},
            }
        )

        await self._ensure_idempotent(key, fingerprint)

        async with self.uow:
            grants = await self.uow.grant_repo.list_active_for_user(
                cmd.user_id
            )

            result = consume_credits(
                consumption_id=ConsumptionId.new(),
                user_id=cmd.user_id,
                grants=grants,
                cost=cmd.cost,
                now=now,
                request_id=cmd.request_id,
                metadata=cmd.metadata,
            )

            await self.uow.grant_repo.save_many(
                list(result.touched_grants)
            )
            await self.uow.consumption_repo.save(
                result.consumption
            )
            await self.uow.commit()

        await self._store_idempotency(key, fingerprint)
        await self._publish_many([result.event])

        return to_credit_consumption_dto(result.consumption)

    async def _ensure_idempotent(
        self,
        key: str,
        fingerprint: str,
    ) -> None:
        if self.idempotency_store is None:
            return

        existing = await self.idempotency_store.get(key)
        if existing is None:
            return
        if existing != fingerprint:
            raise IdempotencyConflictError(
                f"Conflicting request for key={key}"
            )
        raise DuplicateRequestError(
            f"Request for key={key} already processed"
        )

    async def _store_idempotency(
        self,
        key: str,
        fingerprint: str,
    ) -> None:
        if self.idempotency_store is None:
            return
        await self.idempotency_store.save(
            key,
            fingerprint,
        )

    async def _publish_many(
        self,
        events: list[object],
    ) -> None:
        if self.event_publisher is None or not events:
            return
        await self.event_publisher.publish_many(events)

    @staticmethod
    def _idempotency_key(
        *,
        user_id: str,
        request_id: str,
    ) -> str:
        return f"billing:credits:consume:{user_id}:{request_id}"

    @staticmethod
    def _fingerprint(payload: dict) -> str:
        raw = json.dumps(
            payload,
            sort_keys=True,
        ).encode("utf-8")

        return hashlib.sha256(raw).hexdigest()
