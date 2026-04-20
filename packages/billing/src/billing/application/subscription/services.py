import hashlib
import json

from billing.application.exceptions import (
    SubscriptionNotFound,
)

from billing.application.subscription.commands import (
    CancelSubscriptionCommand,
    CreateSubscriptionCommand,
    GrantSubscriptionCreditsCommand,
    RenewSubscriptionCommand,
)
from billing.application.subscription.dto import (
    SubscriptionDTO,
    SubscriptionGrantDTO,
    to_subscription_dto,
    to_subscription_grant_dto,
)
from billing.application.subscription.exceptions import (
    ActiveSubscriptionAlreadyExists,
    IdempotencyConflict,
)
from billing.application.subscription.interfaces import (
    EventPublisher,
    IdempotencyStore,
    SubscriptionApplicationUnitOfWork,
)
from billing.domain.credits.value_objects import GrantId
from billing.domain.shared.time import utc_now
from billing.domain.subscription.domain_services import (
    cancel_subscription,
    create_subscription,
    grant_subscription_credits,
    renew_subscription,
)
from billing.domain.subscription.entities import (
    Subscription,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


class SubscriptionApplicationService:
    def __init__(
        self,
        uow: SubscriptionApplicationUnitOfWork,
        event_publisher: EventPublisher | None = None,
        idempotency_store: IdempotencyStore | None = None,
    ):
        self.uow = uow
        self.event_publisher = event_publisher
        self.idempotency_store = idempotency_store

    def create_subscription(
        self,
        cmd: CreateSubscriptionCommand,
    ) -> SubscriptionDTO:
        now = cmd.now or utc_now()

        existing = (
            self.uow.subscription.get_active_for_user(
                cmd.user_id
            )
        )
        if existing is not None:
            raise ActiveSubscriptionAlreadyExists(
                f"User {cmd.user_id} already has an active subscription"
            )

        result = create_subscription(
            subscription_id=SubscriptionId.new(),
            user_id=cmd.user_id,
            plan_code=cmd.plan_code,
            current_period_start=cmd.current_period_start,
            current_period_end=cmd.current_period_end,
            now=now,
            provider_subscription_id=cmd.provider_subscription_id,
        )

        self.uow.subscription.save(result.subscription)
        self._publish(result.event)
        self.uow.commit()

        return to_subscription_dto(result.subscription)

    def cancel_subscription(
        self,
        cmd: CancelSubscriptionCommand,
    ) -> SubscriptionDTO:
        now = cmd.now or utc_now()

        subscription = self._get_subscription_or_raise(
            cmd.subscription_id
        )
        result = cancel_subscription(
            subscription=subscription,
            now=now,
            immediate=cmd.immediate,
        )

        self.uow.subscription.save(result.subscription)
        self._publish(result.event)
        self.uow.commit()

        return to_subscription_dto(result.subscription)

    def renew_subscription(
        self,
        cmd: RenewSubscriptionCommand,
    ) -> SubscriptionDTO:
        now = cmd.now or utc_now()

        subscription = self._get_subscription_or_raise(
            cmd.subscription_id
        )
        result = renew_subscription(
            subscription=subscription,
            next_period_start=cmd.next_period_start,
            next_period_end=cmd.next_period_end,
            now=now,
        )

        self.uow.subscription.save(result.subscription)
        self._publish(result.event)
        self.uow.commit()

        return to_subscription_dto(result.subscription)

    def grant_subscription_credits(
        self,
        cmd: GrantSubscriptionCreditsCommand,
    ) -> SubscriptionGrantDTO:
        now = cmd.now or utc_now()

        subscription = self._get_subscription_or_raise(
            cmd.subscription_id
        )

        if (
            cmd.request_id is not None
            and self.idempotency_store is not None
        ):
            key = self._idempotency_key_for_grant(cmd)
            fingerprint = self._grant_fingerprint(cmd)

            existing = self.idempotency_store.get(key)
            if existing is not None:
                if existing != fingerprint:
                    raise IdempotencyConflict(
                        f"Conflicting request for request_id {cmd.request_id}"
                    )

                # Same request repeated. Domain grant creation is not re-run because
                # this layer owns idempotency and should short-circuit duplicates.
                # Caller can load fresh ledger state elsewhere if needed.
                raise IdempotencyConflict(
                    f"Request request_id={cmd.request_id} already processed"
                )

        result = grant_subscription_credits(
            grant_id=GrantId.new(),
            subscription=subscription,
            request_id=cmd.request_id,
            now=now,
        )

        self.uow.subscription.save(result.subscription)

        # NOTE:
        # This service only handles subscription application flow.
        # Persisting the credit grant belongs to credits application/infra.
        # For now we only emit the event and return the grant DTO.
        # self.uow.credit_grants.save(result.grant)
        self._publish(result.event)

        if (
            cmd.request_id is not None
            and self.idempotency_store is not None
        ):
            self.idempotency_store.save(
                self._idempotency_key_for_grant(cmd),
                self._grant_fingerprint(cmd),
            )

        self.uow.commit()

        return to_subscription_grant_dto(result)

    def get_subscription(
        self,
        subscription_id: SubscriptionId,
    ) -> SubscriptionDTO:
        subscription = self._get_subscription_or_raise(
            subscription_id
        )
        return to_subscription_dto(subscription)

    def _get_subscription_or_raise(
        self,
        subscription_id: SubscriptionId,
    ) -> Subscription:
        subscription = self.uow.subscription.get(
            subscription_id
        )

        if subscription is None:
            raise SubscriptionNotFound(
                f"Subscription {subscription_id} not found"
            )

        return subscription

    def _publish(self, event: object) -> None:
        if self.event_publisher is not None:
            self.event_publisher.publish(event)

    @staticmethod
    def _idempotency_key_for_grant(
        cmd: GrantSubscriptionCreditsCommand,
    ) -> str:
        return f"subscription:grant:{cmd.request_id}"

    @staticmethod
    def _grant_fingerprint(
        cmd: GrantSubscriptionCreditsCommand,
    ) -> str:
        raw = json.dumps(
            {
                "subscription_id": str(cmd.subscription_id),
                "request_id": str(cmd.request_id),
            },
            sort_keys=True,
        ).encode("utf-8")

        return hashlib.sha256(raw).hexdigest()
