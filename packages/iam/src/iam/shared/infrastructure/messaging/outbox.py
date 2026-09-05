from dataclasses import asdict
from typing import Any

from iam.shared.domain import DomainEvent


def serialize_domain_event(
    event: DomainEvent,
) -> dict[str, Any]:
    return {
        "event_type": type(event).__name__,
        "payload": asdict(event),
        "occurred_at": event.occurred_at,
    }
