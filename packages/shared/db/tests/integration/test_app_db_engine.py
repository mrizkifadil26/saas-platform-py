from sqlalchemy.ext.asyncio import AsyncEngine


def test_create_app_engine_returns_async_engine(app_engine: AsyncEngine) -> None:
    assert isinstance(app_engine, AsyncEngine)
