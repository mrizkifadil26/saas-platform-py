from dataclasses import dataclass

from .namespace import CacheNamespace


@dataclass(frozen=True, slots=True)
class CacheRegion:
    namespace: CacheNamespace
    name: str
    version: str
    ttl: int

    def key(
        self,
        *parts: object,
    ) -> str:
        return self.namespace.key(
            self.name,
            self.version,
            *parts,
        )
