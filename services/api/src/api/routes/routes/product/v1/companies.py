from fastapi import APIRouter, Depends, Query

from api.dummy import dummy_company
from api.schemas.companies import CompanyOut
from api.security.api_key_auth import ApiKeyContext, require_api_key


router = APIRouter()


@router.get("/lookup", response_model=CompanyOut)
async def lookup_company(
    domain: str = Query(..., min_length=3),
    _: ApiKeyContext = Depends(require_api_key),
):
    return dummy_company(domain)


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(
    company_id: str,
    _: ApiKeyContext = Depends(require_api_key),
):
    domain = f"{company_id}.example"
    return dummy_company(domain)
