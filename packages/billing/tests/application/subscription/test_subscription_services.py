from datetime import timedelta

import pytest

from billing.application.subscription.commands import (
    CancelSubscriptionCommand,
    CreateSubscriptionCommand,
    GrantSubscriptionCreditsCommand,
    RenewSubscriptionCommand,
)
from billing.application.subscription.exceptions import (
    ActiveSubscriptionAlreadyExists,
    IdempotencyConflict,
    SubscriptionNotFound,
)
from billing.application.subscription.services import (
    SubscriptionApplicationService,
)
from billing.domain.shared.ids import RequestId
from billing.domain.subscription.events import (
    SubscriptionCanceled,
    SubscriptionCreated,
    SubscriptionCreditsGranted,
    SubscriptionRenewed,
)
from billing.domain.subscription.exceptions import (
    DuplicatePeriodGrant,
    InvalidSubscriptionStatus,
)
from billing.domain.subscription.value_objects import (
    SubscriptionId,
)


@pytest.mark.asyncio
async def test_create_subscription_success(
    uow,
    event_publisher,
    idempotency_store,
    user_id,
    plan_code,
    now,
):
    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = await service.create_subscription(
        CreateSubscriptionCommand(
            user_id=user_id,
            plan_code=plan_code,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            provider_subscription_id="prov_sub_123",
            now=now,
        )
    )

    assert result.user_id == str(user_id)
    assert result.plan_code == str(plan_code)
    assert result.status == "active"
    assert result.cancel_at_period_end is False
    assert result.provider_subscription_id == "prov_sub_123"
    assert result.subscription_id in uow.subscription.by_id

    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0], SubscriptionCreated
    )


@pytest.mark.asyncio
async def test_create_subscription_raises_when_active_subscription_exists(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    user_id,
    plan_code,
    now,
):
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    with pytest.raises(ActiveSubscriptionAlreadyExists):
        await service.create_subscription(
            CreateSubscriptionCommand(
                user_id=user_id,
                plan_code=plan_code,
                current_period_start=now,
                current_period_end=now + timedelta(days=30),
                now=now,
            )
        )

    assert uow.committed is False
    assert event_publisher.events == []


@pytest.mark.asyncio
async def test_cancel_subscription_at_period_end_success(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = await service.cancel_subscription(
        CancelSubscriptionCommand(
            subscription_id=active_subscription.subscription_id,
            immediate=False,
            now=now,
        )
    )
    saved = await uow.subscription.get(
        active_subscription.subscription_id
    )

    assert result.subscription_id == str(
        active_subscription.subscription_id
    )
    assert result.cancel_at_period_end is True
    assert saved is not None
    assert saved.cancel_at_period_end is True
    assert saved.status == "active"

    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0], SubscriptionCanceled
    )
    assert event_publisher.events[0].immediate is False


@pytest.mark.asyncio
async def test_cancel_subscription_immediately_success(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = await service.cancel_subscription(
        CancelSubscriptionCommand(
            subscription_id=active_subscription.subscription_id,
            immediate=True,
            now=now,
        )
    )

    saved = await uow.subscription.get(
        active_subscription.subscription_id
    )

    assert result.status == "canceled"
    assert result.cancel_at_period_end is True
    assert saved is not None
    assert saved.status == "canceled"
    assert saved.cancel_at_period_end is True

    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0], SubscriptionCanceled
    )
    assert event_publisher.events[0].immediate is True


@pytest.mark.asyncio
async def test_cancel_subscription_raises_when_not_found(
    uow,
    event_publisher,
    idempotency_store,
    now,
):
    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    with pytest.raises(SubscriptionNotFound):
        await service.cancel_subscription(
            CancelSubscriptionCommand(
                subscription_id=SubscriptionId.new(),
                immediate=False,
                now=now,
            )
        )

    assert uow.committed is False
    assert event_publisher.events == []


@pytest.mark.asyncio
async def test_renew_subscription_success(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    await uow.subscription.save(active_subscription)

    next_period_start = (
        active_subscription.current_period_end
    )
    next_period_end = next_period_start + timedelta(days=30)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = await service.renew_subscription(
        RenewSubscriptionCommand(
            subscription_id=active_subscription.subscription_id,
            next_period_start=next_period_start,
            next_period_end=next_period_end,
            now=now,
        )
    )

    saved = await uow.subscription.get(
        active_subscription.subscription_id
    )

    assert result.status == "active"
    assert result.current_period_start == next_period_start
    assert result.current_period_end == next_period_end

    assert saved is not None
    assert saved.current_period_start == next_period_start
    assert saved.current_period_end == next_period_end

    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0], SubscriptionRenewed
    )


@pytest.mark.asyncio
async def test_renew_subscription_allows_past_due(
    uow,
    event_publisher,
    idempotency_store,
    past_due_subscription,
    now,
):
    await uow.subscription.save(past_due_subscription)

    next_period_start = (
        past_due_subscription.current_period_end
    )
    next_period_end = next_period_start + timedelta(days=30)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = await service.renew_subscription(
        RenewSubscriptionCommand(
            subscription_id=past_due_subscription.subscription_id,
            next_period_start=next_period_start,
            next_period_end=next_period_end,
            now=now,
        )
    )

    assert result.status == "active"
    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0], SubscriptionRenewed
    )


@pytest.mark.asyncio
async def test_renew_subscription_raises_for_canceled_subscription(
    uow,
    event_publisher,
    idempotency_store,
    canceled_subscription,
    now,
):
    await uow.subscription.save(canceled_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    with pytest.raises(InvalidSubscriptionStatus):
        await service.renew_subscription(
            RenewSubscriptionCommand(
                subscription_id=canceled_subscription.subscription_id,
                next_period_start=now,
                next_period_end=now + timedelta(days=30),
                now=now,
            )
        )

    assert uow.committed is False
    assert event_publisher.events == []


@pytest.mark.asyncio
async def test_get_subscription_success(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
):
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    result = await service.get_subscription(
        active_subscription.subscription_id
    )

    assert result.subscription_id == str(
        active_subscription.subscription_id
    )
    assert result.user_id == str(
        active_subscription.user_id
    )
    assert result.plan_code == str(
        active_subscription.plan_code
    )
    assert result.status == active_subscription.status


@pytest.mark.asyncio
async def test_get_subscription_raises_when_not_found(
    uow,
    event_publisher,
    idempotency_store,
):
    subscription_id = SubscriptionId.new()

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    with pytest.raises(SubscriptionNotFound):
        await service.get_subscription(subscription_id)


@pytest.mark.asyncio
async def test_grant_subscription_credits_success(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    request_id = RequestId("req-sub-grant-1")

    result = await service.grant_subscription_credits(
        GrantSubscriptionCreditsCommand(
            subscription_id=active_subscription.subscription_id,
            request_id=request_id,
            now=now,
        )
    )

    saved = await uow.subscription.get(
        active_subscription.subscription_id
    )

    assert result.subscription_id == str(
        active_subscription.subscription_id
    )
    assert result.user_id == str(
        active_subscription.user_id
    )
    assert result.plan_code == str(
        active_subscription.plan_code
    )
    assert result.request_id == str(request_id)
    assert result.grant_id
    assert (
        result.expires_at
        == active_subscription.current_period_end
    )

    assert saved is not None
    assert (
        saved.last_granted_period_start
        == active_subscription.current_period_start
    )

    assert len(uow.credit_grant.items) == 1
    assert uow.committed is True
    assert len(event_publisher.events) == 1
    assert isinstance(
        event_publisher.events[0],
        SubscriptionCreditsGranted,
    )

    idem_key = f"subscription:grant:{request_id}"
    assert idem_key in idempotency_store.data


@pytest.mark.asyncio
async def test_grant_subscription_credits_raises_duplicate_period_grant(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    active_subscription.last_granted_period_start = (
        active_subscription.current_period_start
    )
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    with pytest.raises(DuplicatePeriodGrant):
        await service.grant_subscription_credits(
            GrantSubscriptionCreditsCommand(
                subscription_id=active_subscription.subscription_id,
                request_id=RequestId("req-sub-grant-2"),
                now=now,
            )
        )

    assert len(uow.credit_grant.items) == 0
    assert uow.committed is False
    assert event_publisher.events == []


@pytest.mark.asyncio
async def test_grant_subscription_credits_raises_when_same_request_replayed(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    await uow.subscription.save(active_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    cmd = GrantSubscriptionCreditsCommand(
        subscription_id=active_subscription.subscription_id,
        request_id=RequestId("req-sub-grant-3"),
        now=now,
    )

    await service.grant_subscription_credits(cmd)

    with pytest.raises(IdempotencyConflict):
        await service.grant_subscription_credits(cmd)

    assert len(uow.credit_grant.items) == 1


@pytest.mark.asyncio
async def test_grant_subscription_credits_raises_when_request_id_reused_with_different_payload(
    uow,
    event_publisher,
    idempotency_store,
    active_subscription,
    now,
):
    await uow.subscription.save(active_subscription)

    other_subscription = type(active_subscription)(
        subscription_id=SubscriptionId.new(),
        user_id=active_subscription.user_id,
        plan_code=active_subscription.plan_code,
        status="active",
        current_period_start=active_subscription.current_period_start,
        current_period_end=active_subscription.current_period_end,
        cancel_at_period_end=False,
        provider_subscription_id="prov_sub_other",
        last_granted_period_start=None,
    )
    await uow.subscription.save(other_subscription)

    service = SubscriptionApplicationService(
        uow=uow,
        event_publisher=event_publisher,
        idempotency_store=idempotency_store,
    )

    request_id = RequestId("req-sub-grant-4")

    await service.grant_subscription_credits(
        GrantSubscriptionCreditsCommand(
            subscription_id=active_subscription.subscription_id,
            request_id=request_id,
            now=now,
        )
    )

    with pytest.raises(IdempotencyConflict):
        await service.grant_subscription_credits(
            GrantSubscriptionCreditsCommand(
                subscription_id=other_subscription.subscription_id,
                request_id=request_id,
                now=now,
            )
        )

    assert len(uow.credit_grant.items) == 1
