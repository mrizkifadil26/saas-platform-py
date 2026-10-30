from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class IdentityBase(DeclarativeBase):
    metadata = MetaData(schema="identity")
