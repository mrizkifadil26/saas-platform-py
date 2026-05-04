from typing import Annotated, AsyncGenerator

from db.app_db.session import AppSessionFactory, get_app_session_factory
from fastapi import Depends

from iam.shared.infrastructure.persistence.sqlalchemy.uow import SqlAlchemyUoW


async def get_unit_of_work(
    session_factory: Annotated[
        AppSessionFactory,
        Depends(get_app_session_factory),
    ],
) -> AsyncGenerator[SqlAlchemyUoW, None]:
    async with session_factory() as session:
        yield SqlAlchemyUoW(session)
