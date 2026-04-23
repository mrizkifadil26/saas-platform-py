import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.integration.testing_models import AppTestModel


@pytest.mark.asyncio
async def test_app_session_can_insert_and_query(
    app_session: AsyncSession,
) -> None:
    model = AppTestModel(name="hello-app")

    app_session.add(model)
    await app_session.commit()

    result = await app_session.execute(
        select(AppTestModel).where(AppTestModel.name == "hello-app"),
    )
    found = result.scalar_one()

    assert found.name == "hello-app"
