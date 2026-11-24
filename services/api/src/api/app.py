from fastapi import FastAPI

from api.bootstrap import Application


def create_app() -> FastAPI:
    return Application().build()


app = create_app()
