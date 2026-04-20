from db.config.settings import AppDBSettings
from db.engines.app import make_app_engine, make_app_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine


def test_make_app_engine():
    cfg = AppDBSettings(database_url="sqlite+aiosqlite:///./test_app.db")
    engine = make_app_engine(cfg)

    assert isinstance(engine, AsyncEngine)


def test_make_app_sessionmaker():
    cfg = AppDBSettings(database_url="sqlite+aiosqlite:///./test_app.db")
    engine = make_app_engine(cfg)
    sessionmaker = make_app_sessionmaker(engine)

    assert sessionmaker is not None
