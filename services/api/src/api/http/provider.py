from api.http.settings import HTTPSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORS

from identity.authentication import routes as authn_routes
from identity.registrations import routes as registration_routes
from identity.sessions import routes as sessions_routes

from .middlewares import (
    RequestIdMiddleware as RequestId,
    SecurityHeadersMiddleware as SecurityHeaders,
)
from .routes import health_routes


class HTTPProvider:
    def __init__(self, settings: HTTPSettings) -> None:
        self.settings = settings

    def register(self, app: FastAPI) -> None:
        self._register_middleware(app)
        self._register_exception_handlers(app)
        self._register_routes(app)

    def _register_middleware(self, app: FastAPI) -> None:
        app.add_middleware(RequestId)
        app.add_middleware(SecurityHeaders)

        app.add_middleware(
            CORS,
            allow_origins=self.settings.cors.allow_origins,
            allow_credentials=self.settings.cors.allow_credentials,
            allow_methods=self.settings.cors.allow_methods,
            allow_headers=self.settings.cors.allow_headers,
        )

    def _register_exception_handlers(self, app: FastAPI) -> None:
        # app.add_exception_handler(Exception, unexpected_exception_handler)
        # registry = HTTPErrorRegistry(
        #     REGISTRATION_ERRORS,
        # )

        # app.add_exception_handler(
        #     DomainError,
        #     create_error_handler(registry),
        # )

        ...

    def _register_routes(self, app: FastAPI) -> None:
        app.include_router(health_routes())

        app.include_router(registration_routes())
        app.include_router(authn_routes())
        app.include_router(sessions_routes())
