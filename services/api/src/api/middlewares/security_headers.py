from uuid import UUID, uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message: Message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"x-frame-options", b"DENY"),
                        (
                            b"referrer-policy",
                            b"strict-origin-when-cross-origin",
                        ),
                    ]
                )

                message = {
                    **message,
                    "headers": headers,
                }

            await send(message)

        await self.app(scope, receive, send_with_request_id)


def get_request_id(value: bytes | None) -> bytes:
    if value is None:
        return str(uuid4()).encode()

    try:
        return str(UUID(value.decode())).encode()
    except (ValueError, UnicodeDecodeError):
        return str(uuid4()).encode()
