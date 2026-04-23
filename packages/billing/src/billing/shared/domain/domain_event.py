import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from billing.shared.domain.time import utc_now


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=utc_now)

    @property
    def event_name(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["event_name"] = self.event_name
        data["occurred_at"] = self.occurred_at.isoformat()
        return data
