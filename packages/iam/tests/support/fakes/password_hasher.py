from dataclasses import dataclass, field


@dataclass(slots=True)
class FakePasswordHasher:
    hashes: dict[str, str] = field(
        default_factory=lambda: dict[str, str](),
    )

    async def hash(
        self,
        password: str,
    ) -> str:
        password_hash = f"hashed:{password}"

        self.hashes[password] = password_hash

        return password_hash

    async def verify(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        return password_hash == f"hashed:{password}"
