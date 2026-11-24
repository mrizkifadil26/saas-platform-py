from dataclasses import dataclass

from authlib.integrations.starlette_client import OAuth

from identity.identity.application.dto import ExternalProfile
from identity.identity.application.ports import IdentityProviderClient
from identity.identity.domain.enums import IdentityProvider


@dataclass(frozen=True, slots=True)
class OIDCProviderConfig:
    provider: IdentityProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    server_metadata_url: str

    scopes: tuple[str, ...] = (
        "openid",
        "email",
        "profile",
    )


class AuthlibOIDCProvider(IdentityProviderClient):
    # name: IdentityProvider = IdentityProvider.GOOGLE
    def __init__(
        self,
        config: OIDCProviderConfig,
    ) -> None:
        self._config = config

        oauth: OAuth = OAuth()
        oauth.register(  # type: ignore
            name="oidc",
            client_id=config.client_id,
            client_secret=config.client_secret,
            server_metadata_url=config.server_metadata_url,
            client_kwargs={
                "scope": " ".join(config.scopes),
            },
        )

        self._client = oauth.create_client("oidc") # type: ignore

    async def authenticate(
        self,
        *,
        authorization_code: str,
        redirect_uri: str,
    ) -> ExternalProfile:
        try:
            token = await self._client.fetch_access_token(
                code=authorization_code,
                redirect_uri=self._config.redirect_uri,
            )

    async def authorization_url(
        self,
        *,
        state: str,
        nonce: str,
    ) -> str:
        result = await self._client.create_authorization_url(
            redirect_uri=self._config.redirect_uri,
            state=state,
            nonce=nonce,
        )

        return result["url"]
