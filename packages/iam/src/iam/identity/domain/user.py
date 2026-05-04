from dataclasses import dataclass

from iam.identity.domain.value_objects.user_id import UserId
from iam.shared.domain.aggregate_root import AggregateRoot


@dataclass
class User(AggregateRoot[UserId]): ...
