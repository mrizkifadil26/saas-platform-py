from .namespace import CacheNamespace
from .region import CacheRegion

iam = CacheNamespace(
    prefix="iam",
)

permissions = CacheRegion(
    namespace=iam,
    name="permissions",
    version="v1",
    ttl=300,
)

roles = CacheRegion(
    namespace=iam,
    name="roles",
    version="v1",
    ttl=600,
)
