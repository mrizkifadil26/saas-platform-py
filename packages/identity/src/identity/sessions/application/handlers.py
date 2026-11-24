from dataclasses import dataclass

from identity.sessions.application.commands import RefreshSession
from identity.sessions.application.dto import RefreshSessionResult
from identity.sessions.application.ports import AccessTokenIssuer, RefreshTokenHasher, SessionRepository
from identity.shared.application.command_bus.contracts import CommandHandler
from identity.shared.application.request_context import RequestContext


@dataclass(slots=True)
class RefreshSessionHandler(
    CommandHandler[
        RefreshSession,
        RefreshSessionResult,
    ]
):
    sessions: SessionRepository
    
    refresh_token_hasher: RefreshTokenHasher
    refresh_token_issuer: RefreshTokenIssuer
    access_token_issuer: AccessTokenIssuer
    
    async def __call__(
        self,
        command: RefreshSession,
        *,
        context: RequestContext,
    ) -> RefreshSessionResult:
        token_hash = self.refresh_token_hasher.hash(
            command.refresh_token
        )

        result = self.sessions.find_by_refresh_token_hash(token_hash);

        if result is None:
            # TODO: refresh failed -> raise Invalid Refresh Token
            ...

        if result.is_expired: ...
        if session.is_revoked: ...

        new_refresh_token = self.refresh_token_issuer.issue()
        new_refresh_token_hash = self.refresh_token_hasher.hash(new_refresh_token)

        await self.sessions.rotate_refresh_token(
            refresh_token_id=refresh_token.id,
            new_token_hash=new_refresh_token_hash,
        )

        # sessions.revoke(old_session)
        # sessions.create(new_session)

        access_token = self.access_token_issuer.issue(
            user_id=,
            session_id=,
            # TODO: organization if we use multi-tenant
            # org_id=,
        )


        return RefreshSessionResult(
            access_token=,
            access_token_expires_in=,
            refresh_token=,
            refresh_token_max_age=,
        )
