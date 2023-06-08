from dataclasses import dataclass, field
from ..containers import FollowListPerson


@dataclass(frozen=True)
class FollowPersonListResponse:

    success: bool = field(default=False)
    users: list[FollowListPerson] = field(default=list)
