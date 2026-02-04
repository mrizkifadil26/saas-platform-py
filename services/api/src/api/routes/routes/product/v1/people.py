from fastapi import APIRouter, Depends, Query

from api.dummy import dummy_company, dummy_person
from api.schemas.people import PersonOut
from api.security.api_key_auth import ApiKeyContext, require_api_key


router = APIRouter()


@router.get("/lookup", response_model=PersonOut)
async def lookup_person(
    domain: str = Query(..., min_length=3),
    email: str | None = Query(default=None),
    _: ApiKeyContext = Depends(require_api_key),
):
    return dummy_person(domain, email_hint=email)


@router.get("/{person_id}", response_model=PersonOut)
async def get_person(
    person_id: str,
    _: ApiKeyContext = Depends(require_api_key),
):
    domain = f"{person_id}.example"
    return dummy_company(domain)
