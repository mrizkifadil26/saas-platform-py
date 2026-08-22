from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from ..naming import NAMING_CONVENTION


class ProductBase(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
