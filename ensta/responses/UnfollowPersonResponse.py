from dataclasses import dataclass, field


@dataclass(frozen=True)
class UnfollowPersonResponse:

    success: bool = field(default=False),
    unfollowed: bool = field(default=False)
