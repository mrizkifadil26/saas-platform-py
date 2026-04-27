from __future__ import annotations

from uuid import uuid4

import pytest

from billing.subscription.application.commands import (
    CancelSubscriptionCommand,
    ChangeSubscriptionPlanCommand,
    CreateSubscriptionCommand,
    CreateSubscriptionItemCommand,
    RenewSubscriptionCommand,
)
from billing.subscription.application.exceptions import SubscriptionNotFound
from billing.subscription.application.handlers import (
    CancelSubscriptionHandler,
    ChangeSubscriptionPlanHandler,
    CreateSubscriptionHandler,
    GetSubscriptionHandler,
    RenewSubscriptionHandler,
)
from billing.subscription.application.queries import GetSubscriptionQuery
from billing.subscription.domain.subscription_events import (
    SubscriptionCanceled,
    SubscriptionChanged,
    SubscriptionRenewed,
    SubscriptionStarted,
)


@pytest.mark.asyncio
async def test_create_subscription_handler_saves_commits_publishes_and_returns_dto(
    subscription_uow,
    event_publisher,
    clock,
    id_generator,
    billing_period,
):
    handler = CreateSubscriptionHandler(
        uow=subscription_uow,
        id_generator=id_generator,
        clock=clock,
        event_publisher=event_publisher,
    )

    result = await handler.handle(
        CreateSubscriptionCommand(
            user_id=str(uuid4()),
            plan_id=str(uuid4()),
            period_start=billing_period.start_at,
            period_end=billing_period.end_at,
            items=(
                CreateSubscriptionItemCommand(
                    item_id=str(uuid4()),
                    product_code=str(uuid4()),
                    feature_code=str(uuid4()),
                    quantity=3,
                ),
            ),
            provider_subscription_id="prov_sub_123",
        )
    )

    assert result.subscription_id == id_generator.generate()
    assert result.provider_subscription_id == "prov_sub_123"
    assert len(result.items) == 1
    assert subscription_uow.commit_count == 1
    assert len(subscription_uow.subscriptions.saved) == 1
    assert len(event_publisher.published_batches) == 1
    assert isinstance(event_publisher.published_batches[0][0], SubscriptionStarted)


@pytest.mark.asyncio
async def test_renew_subscription_handler_updates_subscription(
    subscription_uow,
    event_publisher,
    clock,
    subscription,
    next_billing_period,
):
    await subscription_uow.subscriptions.save(subscription)

    handler = RenewSubscriptionHandler(
        uow=subscription_uow,
        clock=clock,
        event_publisher=event_publisher,
    )

    result = await handler.handle(
        RenewSubscriptionCommand(
            subscription_id=str(subscription.subscription_id),
            next_period_start=next_billing_period.start_at,
            next_period_end=next_billing_period.end_at,
        )
    )

    saved = await subscription_uow.subscriptions.get(subscription.subscription_id)

    assert result.current_period_start == next_billing_period.start_at
    assert saved is not None
    assert saved.current_period_end == next_billing_period.end_at
    assert subscription_uow.commit_count == 1
    assert isinstance(event_publisher.published_batches[0][0], SubscriptionRenewed)


@pytest.mark.asyncio
async def test_change_subscription_plan_handler_updates_subscription(
    subscription_uow,
    event_publisher,
    clock,
    subscription,
):
    new_plan_id = str(uuid4())
    await subscription_uow.subscriptions.save(subscription)

    handler = ChangeSubscriptionPlanHandler(
        uow=subscription_uow,
        clock=clock,
        event_publisher=event_publisher,
    )

    result = await handler.handle(
        ChangeSubscriptionPlanCommand(
            subscription_id=str(subscription.subscription_id),
            new_plan_id=new_plan_id,
        )
    )

    saved = await subscription_uow.subscriptions.get(subscription.subscription_id)

    assert result.plan_id == new_plan_id
    assert saved is not None
    assert saved.plan_id.value == new_plan_id
    assert isinstance(event_publisher.published_batches[0][0], SubscriptionChanged)


@pytest.mark.asyncio
async def test_cancel_subscription_handler_handles_immediate_cancellation(
    subscription_uow,
    event_publisher,
    clock,
    subscription,
):
    await subscription_uow.subscriptions.save(subscription)

    handler = CancelSubscriptionHandler(
        uow=subscription_uow,
        clock=clock,
        event_publisher=event_publisher,
    )

    result = await handler.handle(
        CancelSubscriptionCommand(
            subscription_id=str(subscription.subscription_id),
            immediate=True,
        )
    )

    saved = await subscription_uow.subscriptions.get(subscription.subscription_id)

    assert result.status == "canceled"
    assert saved is not None
    assert saved.status == "canceled"
    assert isinstance(event_publisher.published_batches[0][0], SubscriptionCanceled)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("handler_cls", "payload"),
    [
        (
            RenewSubscriptionHandler,
            lambda: RenewSubscriptionCommand(
                subscription_id=str(uuid4()),
                next_period_start=None,  # type: ignore[arg-type]
                next_period_end=None,  # type: ignore[arg-type]
            ),
        ),
        (
            ChangeSubscriptionPlanHandler,
            lambda: ChangeSubscriptionPlanCommand(
                subscription_id=str(uuid4()),
                new_plan_id=str(uuid4()),
            ),
        ),
        (
            CancelSubscriptionHandler,
            lambda: CancelSubscriptionCommand(
                subscription_id=str(uuid4()),
            ),
        ),
    ],
)
async def test_mutating_handlers_raise_not_found_when_missing(
    handler_cls,
    payload,
    subscription_uow,
    event_publisher,
    clock,
):
    handler = handler_cls(
        uow=subscription_uow,
        clock=clock,
        event_publisher=event_publisher,
    )

    with pytest.raises(SubscriptionNotFound):
        await handler.handle(payload())


@pytest.mark.asyncio
async def test_get_subscription_handler_returns_dto_and_raises_when_missing(
    subscription_uow,
    subscription,
):
    await subscription_uow.subscriptions.save(subscription)
    handler = GetSubscriptionHandler(uow=subscription_uow)

    found = await handler.handle(
        GetSubscriptionQuery(subscription_id=str(subscription.subscription_id))
    )

    assert found.subscription_id == str(subscription.subscription_id)

    with pytest.raises(SubscriptionNotFound):
        await handler.handle(GetSubscriptionQuery(subscription_id=str(uuid4())))
