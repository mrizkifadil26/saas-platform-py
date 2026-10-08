from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class IAMBase(DeclarativeBase):
    metadata = MetaData(schema="iam")
