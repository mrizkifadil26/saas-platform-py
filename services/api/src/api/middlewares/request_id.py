from uuid import UUID, uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestIdMiddleware:
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

        headers = dict(scope.get("headers", []))
        request_id = get_request_id(headers.get(b"x-request-id"))

        scope.setdefault("state", {})["request_id"] = request_id.decode()

        async def send_with_request_id(message: Message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id))
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_request_id)


def get_request_id(value: bytes | None) -> bytes:
    if value is None:
        return str(uuid4()).encode()

    try:
        return str(UUID(value.decode())).encode()
    except (ValueError, UnicodeDecodeError):
        return str(uuid4()).encode()
