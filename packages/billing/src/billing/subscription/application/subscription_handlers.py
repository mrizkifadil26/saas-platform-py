from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.application._event_utils import pull_events
from billing.subscription.application.exceptions import SubscriptionNotFound
from billing.subscription.application.subscription_commands import (
    CancelSubscriptionCommand,
    ChangeSubscriptionPlanCommand,
    CreateSubscriptionCommand,
    RenewSubscriptionCommand,
)
from billing.subscription.application.subscription_dto import (
    SubscriptionDTO,
)
from billing.subscription.application.subscription_mappers import SubscriptionMapper
from billing.subscription.application.subscription_queries import GetSubscriptionQuery
from billing.subscription.application.subscription_uow import SubscriptionUnitOfWork
from billing.subscription.domain.subscription_factory import SubscriptionFactory
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.plan_id import PlanId
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId


class CreateSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: SubscriptionUnitOfWork,
        id_generator: IdGenerator,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher

        # self.subscription_repository = subscription_repository
        # self.idempotency_store = idempotency_store

    def handle(
        self,
        command: CreateSubscriptionCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")

        items = [
            SubscriptionMapper.command_item_to_domain(item) for item in command.items
        ]

        subscription = SubscriptionFactory.create_subscription(
            subscription_id=SubscriptionId(self._id_generator.generate()),
            # TODO: should implement customer_id than user_id
            user_id=UserId(command.user_id),
            plan_id=PlanId(command.plan_id),
            period_start=command.period_start,
            period_end=command.period_end,
            items=items,
            provider_subscription_id=command.provider_subscription_id,
            trial=command.trial,
        )

        with self._uow:
            self._uow.subscriptions.save(subscription)
            self._uow.commit()

        # self.idempotency_store.store(command.idempotency_key)

        events = pull_events(subscription)
        self._event_publisher.publish(events)

        return SubscriptionMapper.domain_to_dto(subscription)


class RenewSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: SubscriptionUnitOfWork,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

        # self.idempotency_store = idempotency_store

    def handle(
        self,
        command: RenewSubscriptionCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")
        subscription_id = SubscriptionId(command.subscription_id)

        with self._uow:
            subscription = self._uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFound(
                    f"Subscription not found: {command.subscription_id}"
                )

            next_period = BillingPeriod(
                start_at=command.next_period_start,
                end_at=command.next_period_end,
            )

            updated_subscription = subscription.renew(
                next_billing_period=next_period,
                occurred_at=self._clock.now(),
            )

            self._uow.subscriptions.save(updated_subscription)
            self._uow.commit()

        # self.idempotency_store.store(command.idempotency_key)

        events = pull_events(updated_subscription)
        self._event_publisher.publish(events)

        return SubscriptionMapper.domain_to_dto(subscription)


class ChangeSubscriptionPlanHandler:
    def __init__(
        self,
        *,
        uow: SubscriptionUnitOfWork,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

        # self.idempotency_store = idempotency_store

    def handle(
        self,
        command: ChangeSubscriptionPlanCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")
        subscription_id = SubscriptionId(command.subscription_id)
        new_plan_id = PlanId(command.new_plan_id)

        with self._uow:
            subscription = self._uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFound(
                    f"Subscription not found: {command.subscription_id}"
                )

            updated_subscription = subscription.change_plan(
                new_plan_id=new_plan_id,
                occurred_at=self._clock.now(),
            )

            self._uow.subscriptions.save(updated_subscription)
            self._uow.commit()

        # self.idempotency_store.store(command.idempotency_key)

        events = pull_events(updated_subscription)
        self._event_publisher.publish(events)

        return SubscriptionMapper.domain_to_dto(subscription)


class CancelSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: SubscriptionUnitOfWork,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

        # self.idempotency_store = idempotency_store

    def handle(
        self,
        command: CancelSubscriptionCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")
        subscription_id = SubscriptionId(command.subscription_id)

        with self._uow:
            subscription = self._uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFound(
                    f"Subscription not found: {command.subscription_id}"
                )

            updated_subscription = subscription.cancel(
                immediate=command.immediate,
                occurred_at=self._clock.now(),
            )

            self._uow.subscriptions.save(updated_subscription)
            self._uow.commit()

        # self.idempotency_store.store(command.idempotency_key)

        events = pull_events(updated_subscription)
        self._event_publisher.publish(events)

        return SubscriptionMapper.domain_to_dto(updated_subscription)


class GetSubscriptionHandler:
    def __init__(self, *, uow: SubscriptionUnitOfWork) -> None:
        self._uow = uow

    def handle(self, query: GetSubscriptionQuery) -> SubscriptionDTO:
        subscription_id = SubscriptionId(query.subscription_id)
        with self._uow:
            subscription = self._uow.subscriptions.get(
                subscription_id,
            )
            if subscription is None:
                raise SubscriptionNotFound(
                    f"Subscription not found: {query.subscription_id}"
                )

        return SubscriptionMapper.domain_to_dto(subscription)
