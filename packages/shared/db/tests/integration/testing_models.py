from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.app_db.base import AppBase


class AppTestModel(AppBase):
    __tablename__ = "app_test_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
