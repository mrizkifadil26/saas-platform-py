from fastapi import FastAPI

from api.http.provider import HTTPProvider
from api.providers.database import DatabaseProvider
from api.settings import get_settings


class Application:
    def __init__(self) -> None:
        self.settings = get_settings()

        self.providers = [
            HTTPProvider(self.settings.http),
            DatabaseProvider(self.settings.db),
        ]

    def build(self) -> FastAPI:
        app = FastAPI(
            title=self.settings.app_name,
            version=self.settings.app_version,
            debug=self.settings.debug,
            lifespan=self._lifespan(),
        )

        for provider in self.providers:
            provider.register(app)

        return app

    def _lifespan(self):
        ...