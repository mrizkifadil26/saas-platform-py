import hashlib
import json

from billing.application.payg.commands import (
    CreatePaygPurchaseCommand,
)
from billing.application.payg.dto import (
    PaygPurchaseResultDTO,
    to_payg_purchase_result_dto,
)
from billing.application.payg.exceptions import (
    DuplicateRequestError,
    IdempotencyConflictError,
)
from billing.application.payg.interfaces import (
    PaygApplicationUnitOfWork,
)
from billing.application.shared.interfaces import (
    EventPublisher,
    IdempotencyStore,
)
from billing.domain.credits.value_objects import GrantId
from billing.domain.payg.domain_services import (
    create_payg_purchase,
)
from billing.domain.payg.value_objects import PaygPurchaseId
from billing.domain.shared.time import utc_now


class PaygApplicationService:
    def __init__(
        self,
        uow: PaygApplicationUnitOfWork,
        event_publisher: EventPublisher | None = None,
        idempotency_store: IdempotencyStore | None = None,
    ):
        self.uow = uow
        self.event_publisher = event_publisher
        self.idempotency_store = idempotency_store

    async def create_purchase(
        self,
        cmd: CreatePaygPurchaseCommand,
    ) -> PaygPurchaseResultDTO:
        now = cmd.now or utc_now()

        key = self._idempotency_key(str(cmd.request_id))
        fingerprint = self._fingerprint(
            {
                "user_id": str(cmd.user_id),
                "plan_code": str(cmd.plan_code),
                "request_id": str(cmd.request_id),
                "metadata": cmd.metadata or {},
            }
        )

        await self._ensure_idempotent(key, fingerprint)

        async with self.uow:
            result = create_payg_purchase(
                purchase_id=PaygPurchaseId.new(),
                grant_id=GrantId.new(),
                user_id=cmd.user_id,
                plan_code=cmd.plan_code,
                now=now,
                request_id=cmd.request_id,
                metadata=cmd.metadata,
            )

            await self.uow.payg_purchase.save(
                result.purchase
            )
            await self.uow.ledger.save_grant(result.grant)
            await self.uow.commit()

        await self._store_idempotency(key, fingerprint)
        await self._publish_many([result.event])

        return to_payg_purchase_result_dto(result)

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
        await self.idempotency_store.save(key, fingerprint)

    async def _publish_many(
        self,
        events: list[object],
    ) -> None:
        if self.event_publisher is None or not events:
            return
        await self.event_publisher.publish_many(events)

    @staticmethod
    def _idempotency_key(request_id: str) -> str:
        return f"billing:payg:create_purchase:{request_id}"

    @staticmethod
    def _fingerprint(payload: dict) -> str:
        raw = json.dumps(
            payload,
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
