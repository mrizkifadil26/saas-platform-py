from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CacheNamespace:
    prefix: str

    def key(
        self,
        *parts: object,
    ) -> str:
        suffix = ":".join(map(str, parts))
        return f"{self.prefix}:{suffix}"
