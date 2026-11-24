from typing import Annotated, cast

from fastapi import Depends, Request

from identity.shared.application.command_bus.bus import CommandBus
from identity.shared.application.request_context import RequestContext


def get_command_bus(request: Request) -> CommandBus:
    return cast(
        CommandBus,
        request.app.state.command_bus,
    )

def get_request_context(
    request: Request,
) -> RequestContext:
    return RequestContext(
        request_id=request.state.request_id,
        client_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
    )

def get_client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


CommandBusDep = Annotated[
    CommandBus,
    Depends(get_command_bus),
]


RequestContextDep = Annotated[
    RequestContext,
    Depends(get_request_context),
]