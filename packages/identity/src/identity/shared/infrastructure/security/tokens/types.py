from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    subject: str
    session_id: str
    issued_at: datetime
    expires_at: datetime
    issuer: str
    audience: str
    scopes: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "sub": self.subject,
            "sid": self.session_id,
            "iat": self.issued_at,
            "exp": self.expires_at,
            "iss": self.issuer,
            "aud": self.audience,
            "scope": " ".join(self.scopes),
        }

    @classmethod
    def from_payload(
        cls,
        payload: Mapping[str, Any],
    ) -> AccessTokenClaims:
        subject = payload.get("sub")
        session_id = payload.get("sid")
        issuer = payload.get("iss")
        audience = payload.get("aud")
        issued_at = payload.get("iat")
        expires_at = payload.get("exp")

        if not isinstance(subject, str):
            raise ValueError("Missing or invalid 'sub' claim")

        if not isinstance(session_id, str):
            raise ValueError("Missing or invalid 'sid' claim")

        if not isinstance(issuer, str):
            raise ValueError("Missing or invalid 'iss' claim")

        if not isinstance(audience, str):
            raise ValueError("Missing or invalid 'aud' claim")

        if not isinstance(issued_at, datetime):
            raise ValueError("Missing or invalid 'iat' claim")

        if not isinstance(expires_at, datetime):
            raise ValueError("Missing or invalid 'exp' claim")

        scope = payload.get("scope", "")

        if not isinstance(scope, str):
            raise ValueError("Invalid 'scope' claim")

        scopes = tuple(scope.split()) if scope else ()

        return cls(
            subject=subject,
            session_id=session_id,
            issued_at=issued_at,
            expires_at=expires_at,
            issuer=issuer,
            audience=audience,
            scopes=scopes,
        )
