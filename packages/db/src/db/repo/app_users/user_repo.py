import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.app_users.user import User


class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        # query = "SELECT * FROM users WHERE id = :user_id"
        stmt = (
            select(User)
            .where(User.id == user_id)
        )
        res = await self.db.execute(stmt)

        return res.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        # query = "SELECT * FROM users WHERE email = :email"
        stmt = (
            select(User)
            .where(User.email == email)
        )
        res = await self.db.execute(stmt)

        return res.scalar_one_or_none()

    async def create_user(
        self,
        *,
        email: str,
        fullname: str | None = None,
    ) -> User:
        u = User(email=email, fullname=fullname)

        self.db.add(u)
        await self.db.flush()
        # await self.db.commit()
        # await self.db.refresh(user)

        return u
