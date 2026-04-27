from __future__ import annotations

from uuid import uuid4

from billing.shared.domain.aggregate_root import AggregateRoot
from billing.shared.domain.domain_event import DomainEvent
from billing.subscription.application._event_utils import pull_events
from billing.subscription.application.commands import CreateSubscriptionItemCommand
from billing.subscription.application.dto import SubscriptionItemDTO
from billing.subscription.application.mappers import SubscriptionMapper


def test_subscription_mapper_maps_command_and_domain_values(subscription):
    command = CreateSubscriptionItemCommand(
        item_id=str(uuid4()),
        product_code=str(uuid4()),
        feature_code=str(uuid4()),
        quantity=4,
    )

    domain_item = SubscriptionMapper.command_item_to_domain(command)
    dto_item = SubscriptionMapper.domain_item_to_dto(domain_item)
    mapped_back = SubscriptionMapper.dto_item_to_domain(
        SubscriptionItemDTO(
            item_id=dto_item.item_id,
            product_code=dto_item.product_code,
            feature_code=dto_item.feature_code,
            quantity=dto_item.quantity,
        )
    )
    aggregate_dto = SubscriptionMapper.domain_to_dto(subscription)

    assert str(domain_item.item_id) == command.item_id
    assert dto_item.quantity == 4
    assert mapped_back == domain_item
    assert aggregate_dto.subscription_id == str(subscription.subscription_id)
    assert aggregate_dto.items[0].item_id == str(subscription.items[0].item_id)


def test_pull_events_supports_pull_domain_events():
    class SampleAggregate(AggregateRoot[str]):
        pass

    aggregate = SampleAggregate()
    aggregate.record_event(DomainEvent())

    events = pull_events(aggregate)

    assert len(events) == 1
    assert aggregate.domain_events == ()


def test_pull_events_supports_pull_events_and_internal_events():
    class PullEventsOnly:
        def __init__(self) -> None:
            self._events = [1, 2]

        def pull_events(self):
            events = list(self._events)
            self._events.clear()
            return events

    class InternalEventsOnly:
        def __init__(self) -> None:
            self._events = ["a"]

    pull_events_obj = PullEventsOnly()
    internal_obj = InternalEventsOnly()

    assert pull_events(pull_events_obj) == [1, 2]
    assert pull_events_obj._events == []
    assert pull_events(internal_obj) == ["a"]
    assert internal_obj._events == []
