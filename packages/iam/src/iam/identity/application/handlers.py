from iam.identity.application.commands import (
    ActivateUser,
    ChangePassword,
    DeactivateUser,
    RegisterUser,
)
from iam.identity.application.dto import PaginatedUsersDTO, UserDTO
from iam.identity.application.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundByEmailError,
    UserNotFoundError,
)
from iam.identity.application.interfaces import PasswordHasher
from iam.identity.application.queries import GetUserByEmail, GetUserById, ListUsers
from iam.identity.domain.user import User
from iam.identity.domain.user_repository import UserRepository
from iam.identity.domain.value_objects.email_address import EmailAddress
from iam.identity.domain.value_objects.password_hash import PasswordHash


class RegisterUserHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def handle(self, command: RegisterUser) -> None:
        email = EmailAddress(command.email)

        existing_user = await self.user_repository.find_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError(command.email)

        password_hash = PasswordHash(
            self.password_hasher.hash(command.password),
        )

        user = User.register(
            email=email,
            password_hash=password_hash,
        )

        await self.user_repository.save(user)


class ActivateUserHandler:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def handle(self, command: ActivateUser) -> None:
        user = await self.user_repository.find_by_id(command.user_id)
        if user is None:
            raise UserNotFoundError(command.user_id)

        user.activate()
        await self.user_repository.save(user)


class DeactivateUserHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def handle(self, command: DeactivateUser) -> None:
        user = await self.user_repository.find_by_id(command.user_id)

        if user is None:
            raise UserNotFoundError(command.user_id)

        user.disable()

        await self.user_repository.save(user)


class ChangePasswordHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def handle(self, command: ChangePassword) -> None:
        user = await self.user_repository.find_by_id(command.user_id)

        if user is None:
            raise UserNotFoundError(command.user_id)

        new_hash = PasswordHash(
            self.password_hasher.hash(command.new_password),
        )

        user.change_password(new_hash)

        await self.user_repository.save(user)


class GetUserByIdHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def handle(self, query: GetUserById) -> UserDTO:
        user = await self.user_repository.find_by_id(query.user_id)

        if user is None:
            raise UserNotFoundError(query.user_id)

        return UserDTO(
            id=str(user.id),
            email=str(user.email),
            status=str(user.status),
        )


class GetUserByEmailHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def handle(self, query: GetUserByEmail) -> UserDTO:
        email = EmailAddress(query.email)
        user = await self.user_repository.find_by_email(email)

        if user is None:
            raise UserNotFoundByEmailError(query.email)

        return UserDTO(
            id=str(user.id),
            email=str(user.email),
            status=str(user.status),
        )


class ListUsersHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def handle(self, query: ListUsers) -> PaginatedUsersDTO:
        users, total = await self.user_repository.list(
            limit=query.limit,
            offset=query.offset,
        )

        return PaginatedUsersDTO(
            items=[
                UserDTO(
                    id=str(user.id),
                    email=str(user.email),
                    status=str(user.status),
                )
                for user in users
            ],
            limit=query.limit,
            offset=query.offset,
            total=total,
        )
