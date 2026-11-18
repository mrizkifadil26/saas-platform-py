

# class AuthenticationAttemptRepository(Protocol):
#     async def save(
#         self,
#         attempt: AuthenticationAttempt,
#     ) -> None: ...

#     async def list_recent_by_user_id(
#         self,
#         user_id: UserId,
#         limit: int = 10,
#     ) -> list[AuthenticationAttempt]: ...

#     async def count_recent_failures(
#         self,
#         *,
#         email: Email,
#         since: datetime,
#     ) -> int: ...


