from dataclasses import dataclass
from http import HTTPStatus
from typing import Any


@dataclass(frozen=True, slots=True)
class HTTPError:
    status: HTTPStatus
    code: str
    message: str
    headers: dict[str, str] | None = None
    details: dict[str, Any] | None = None
