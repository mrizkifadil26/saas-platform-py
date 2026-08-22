from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from db.app_db.naming import NAMING_CONVENTION


class AppBase(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
