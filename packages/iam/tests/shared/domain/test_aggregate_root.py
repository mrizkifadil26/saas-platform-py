from dataclasses import dataclass

from iam.shared.domain import AggregateRoot, DomainEvent


@dataclass(frozen=True)
class UserCreated(DomainEvent):
    user_id: int


@dataclass(eq=False)
class UserAggregate(AggregateRoot[int]):
    name: str


def test_should_record_domain_event():
    user = UserAggregate(id=1, name="Alice")
    event = UserCreated(user_id=1)
    user.record_event(event)

    assert user.pull_events() == [event]
    assert user.pull_events() == []


def test_should_pull_and_clear_events():
    user = UserAggregate(id=1, name="Alice")

    event1 = UserCreated(user_id=1)
    event2 = UserCreated(user_id=2)

    user.record_event(event1)
    user.record_event(event2)

    events = user.pull_events()

    assert events == [event1, event2]
    assert user.pull_events() == []


def test_should_return_empty_list_when_no_events():
    user = UserAggregate(id=1, name="Alice")

    assert user.pull_events() == []
