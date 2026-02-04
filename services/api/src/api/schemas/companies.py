from pydantic import BaseModel


class CompanyOut(BaseModel):
    id: str
    name: str
    domain: str
    industry: str
    employee_count: int
