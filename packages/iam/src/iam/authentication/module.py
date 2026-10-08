from dataclasses import dataclass

from fastapi import APIRouter

from iam.authentication.presentation.http import router


@dataclass(slots=True)
class Module:
    router: APIRouter
    # authenticator: Authenticator
    # access_token_verifier: AccessTokenVerifier


def create_module() -> Module:
    return Module(
        router=router,
    )
