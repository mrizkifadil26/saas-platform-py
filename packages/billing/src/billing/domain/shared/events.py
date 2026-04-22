import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from billing.domain.shared.time import utc_now


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    event_id: str = field(
        default_factory=lambda: uuid.uuid4().hex,
    )
    occurred_at: datetime = field(default_factory=utc_now)

    @property
    def event_name(self) -> str:
        return self.__class__.__name__

    def as_metadata(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_at": self.occurred_at.isoformat(),
        }
