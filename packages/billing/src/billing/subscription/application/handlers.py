from billing.pricing.application.catalogs import SubscriptionPricingCatalog
from billing.shared.application.clock import Clock
from billing.shared.application.event_publisher import EventPublisher
from billing.shared.application.id_generator import IdGenerator
from billing.shared.application.uow import BillingUoW
from billing.shared.domain.value_objects.user_id import UserId
from billing.subscription.application.commands import (
    CancelSubscriptionCommand,
    ChangeSubscriptionPlanCommand,
    CreateSubscriptionCommand,
    RenewSubscriptionCommand,
)
from billing.subscription.application.dto import (
    SubscriptionDTO,
)
from billing.subscription.application.exceptions import SubscriptionNotFoundError
from billing.subscription.application.mappers import (
    SubscriptionMapper,
)
from billing.subscription.application.queries import GetSubscriptionQuery
from billing.subscription.domain.subscription_factory import SubscriptionFactory
from billing.subscription.domain.subscription_item import SubscriptionItem
from billing.subscription.domain.value_objects.billing_period import BillingPeriod
from billing.subscription.domain.value_objects.feature_code import FeatureCode
from billing.subscription.domain.value_objects.plan_code import PlanCode
from billing.subscription.domain.value_objects.product_code import ProductCode
from billing.subscription.domain.value_objects.subscription_id import SubscriptionId
from billing.subscription.domain.value_objects.subscription_item_id import (
    SubscriptionItemId,
)


class CreateSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        id_generator: IdGenerator,
        pricing_catalog: SubscriptionPricingCatalog,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._id_generator = id_generator
        self._pricing_catalog = pricing_catalog
        self._clock = clock
        self._event_publisher = event_publisher
        # self.idempotency_store = idempotency_store

    async def handle(
        self,
        command: CreateSubscriptionCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")

        now = self._clock.now()
        items = [
            SubscriptionItem(
                item_id=SubscriptionItemId(item.item_id),
                product_code=ProductCode(item.product_code),
                feature_code=FeatureCode(item.feature_code),
                quantity=item.quantity,
            )
            for item in command.items
        ]

        subscription = SubscriptionFactory.create_subscription(
            subscription_id=SubscriptionId(self._id_generator.generate()),
            # TODO: should implement customer_id than user_id
            user_id=UserId(command.user_id),
            # TODO: should use plan_id instead of plan_code later
            # plan_id=PlanId(command.plan_id),
            plan_code=PlanCode(command.plan_code),
            period_start=command.period_start,
            period_end=command.period_end,
            items=items,
            provider_subscription_id=command.provider_subscription_id,
            trial=command.trial,
            occurred_at=now,
        )

        async with self._uow as uow:
            await uow.subscriptions.save(subscription)
            events = subscription.pull_domain_events()

            await uow.commit()

        # TODO: later should use await
        self._event_publisher.publish(events)

        return SubscriptionMapper.to_dto(subscription)


class RenewSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher
        # self.idempotency_store = idempotency_store

    async def handle(
        self,
        command: RenewSubscriptionCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")

        subscription_id = SubscriptionId(command.subscription_id)

        async with self._uow as uow:
            subscription = await uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(
                    f"Subscription not found: {command.subscription_id}"
                )

            next_period = BillingPeriod(
                start_at=command.next_period_start,
                end_at=command.next_period_end,
            )

            subscription.renew(
                next_billing_period=next_period,
                occurred_at=self._clock.now(),
            )

            await uow.subscriptions.save(subscription)
            events = subscription.pull_domain_events()

            await uow.commit()

        # TODO: later should use await
        self._event_publisher.publish(events)

        return SubscriptionMapper.to_dto(subscription)


class ChangeSubscriptionPlanHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher
        # self.idempotency_store = idempotency_store

    async def handle(
        self,
        command: ChangeSubscriptionPlanCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")

        subscription_id = SubscriptionId(command.subscription_id)
        # new_plan_id = PlanId(command.new_plan_id)
        new_plan_code = PlanCode(command.new_plan_code)

        async with self._uow as uow:
            subscription = await uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(
                    f"Subscription not found: {command.subscription_id}"
                )

            subscription.change_plan(
                # new_plan_id=new_plan_id,
                new_plan_code=new_plan_code,
                occurred_at=self._clock.now(),
            )

            await uow.subscriptions.save(subscription)
            events = subscription.pull_domain_events()

            await uow.commit()

        # TODO: later should use await
        self._event_publisher.publish(events)

        return SubscriptionMapper.to_dto(subscription)


class CancelSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
        clock: Clock,
        event_publisher: EventPublisher,
        # idempotency_store: IdempotencyStore,
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._event_publisher = event_publisher

        # self.idempotency_store = idempotency_store

    async def handle(
        self,
        command: CancelSubscriptionCommand,
    ) -> SubscriptionDTO:
        # TODO: Should idempotency be handled at the application service level instead of the handler level?
        # if self.idempotency_store.exists(command.idempotency_key):
        # raise ValueError("Duplicate request")
        subscription_id = SubscriptionId(command.subscription_id)

        async with self._uow as uow:
            subscription = await uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(
                    f"Subscription not found: {command.subscription_id}"
                )

            subscription.cancel(
                immediate=command.immediate,
                occurred_at=self._clock.now(),
            )

            await uow.subscriptions.save(subscription)
            events = subscription.pull_domain_events()

            await uow.commit()

        # TODO: later should use await
        self._event_publisher.publish(events)

        return SubscriptionMapper.to_dto(subscription)


class GetSubscriptionHandler:
    def __init__(
        self,
        *,
        uow: BillingUoW,
    ) -> None:
        self._uow = uow

    async def handle(self, query: GetSubscriptionQuery) -> SubscriptionDTO:
        subscription_id = SubscriptionId(query.subscription_id)

        async with self._uow as uow:
            subscription = await uow.subscriptions.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(
                    f"Subscription not found: {query.subscription_id}"
                )

        return SubscriptionMapper.to_dto(subscription)
