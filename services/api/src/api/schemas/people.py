from pydantic import BaseModel


class PersonOut(BaseModel):
    id: str
    full_name: str
    title: str
    email: str | None
    company_domain: str
