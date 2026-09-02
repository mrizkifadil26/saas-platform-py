from datetime import datetime
from typing import Protocol

from iam.identity.domain.value_objects import UserId
from iam.sessions.application.dto import IssuedSession


class SessionIssuer(Protocol):
    async def issue(
        self,
        *,
        user_id: UserId,
        issued_at: datetime,
    ) -> IssuedSession: ...
