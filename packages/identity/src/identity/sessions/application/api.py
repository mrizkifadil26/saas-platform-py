from datetime import datetime
from typing import Protocol

from identity.identity.domain.value_objects import UserId
from identity.sessions.application.dto import IssuedSession


class SessionIssuer(Protocol):
    async def issue(
        self,
        *,
        user_id: UserId,
        issued_at: datetime,
    ) -> IssuedSession: ...
