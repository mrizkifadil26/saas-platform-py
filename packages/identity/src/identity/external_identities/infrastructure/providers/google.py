from dataclasses import dataclass

from google_auth_oauthlib.flow import Flow
from identity.identity.application.ports import IdentityProviderClient
from identity.identity.domain.enums import IdentityProvider
from identity.shared.domain.email import EmailAddress

# GOOGLE_USERNFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleAuthenticationError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class GoogleOIDCSettings:
    client_id: str
    client_secret: str
    redirect_uri: str

    @property
    def scopes(self) -> tuple[str, ...]:
        return (
            "openid",
            "email",
            "profile",
        )


@dataclass(slots=True)
class GoogleOIDCProvider(IdentityProviderClient):
    settings: GoogleOIDCSettings

    name: IdentityProvider = IdentityProvider.GOOGLE

    def authorization_url(
        self,
        *,
        redirect_uri: str,
        state: str,
    ) -> str:
        flow = self._create_flow(
            redirect_uri=redirect_uri,
        )

        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="select_account",
            state=state,
        )

        return authorization_url

    async def authenticate(
        self,
        *,
        auhtorization_code: str,
        redirect_uri: str,
    ) -> ExternalProfile:
        token = await self.client.exchange_code(
            code=code,
            redirect_uri=redirect_uri,
        )

        profile = await self.client.get_userinfo(
            access_token=token.access_token,
        )

        return ExternalProfile(
            provider=IdentityProvider.GOOGLE,
            subject=profile.sub,
            email=EmailAddress(profile.email),
            email_verified=profile.email_verified,
            name=profile.name,
        )

    def _create_flow(
        self,
        *,
        redirect_uri: str,
    ) -> Flow:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.settings.client_id,
                    "client_secret": self.settings.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=list(self.settings.scopes),
            redirect_uri=self.settings.redirect_uri,
        )

        flow.redirect_uri = redirect_uri

        return flow
