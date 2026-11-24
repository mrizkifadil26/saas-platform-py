from fastapi import FastAPI

from db import Database
from db.settings import BaseDBSettings


class DatabaseProvider:
    def __init__(self, settings: BaseDBSettings) -> None:
        self.settings = settings

    def register(self, app: FastAPI) -> None:
        app.state.database = Database.create(
            cfg=self.settings,
        )
