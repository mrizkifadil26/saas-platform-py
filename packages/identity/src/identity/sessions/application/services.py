from identity.accounts.domain.value_objects import UserId
from identity.sessions.domain.value_objects import RefreshToken, SessionId


class SessionService:
    async def create(
        self,
        *,
        user_id: UserId,
    ) -> TokenPair: ...

    async def refresh(
        self,
        *,
        refresh_token: RefreshToken,  # TODO: is it in str or bytes?
    ) -> TokenPair: ...

    async def revoke(
        self,
        *,
        session_id: SessionId,
    ) -> None: ...
