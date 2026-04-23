from collections.abc import AsyncIterator

from db.config import AppDBSettings
from db.engines import (
    make_app_engine,
    make_app_sessionmaker,
)
from db.sessions import get_app_session

from billing.subscription.infrastructure.persistence.sqlalchemy.sqlalchemy_uow import (
    SQLAlchemyUnitOfWork,
)

cfg = AppDBSettings(
    database_url="postgresql+asyncpg://user:pass@localhost:5432/app",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)
engine = make_app_engine(cfg)
sessionmaker = make_app_sessionmaker(engine)


async def get_subscription_uow() -> AsyncIterator[SQLAlchemyUnitOfWork]:
    async for session in get_app_session(sessionmaker):
        yield SQLAlchemyUnitOfWork(session)
