from dataclasses import dataclass, field


@dataclass(frozen=True)
class FollowPersonResponse:

    success: bool = field(default=False),
    following: bool = field(default=False),
    follow_requested: bool = field(default=False),
    previous_following: bool = field(default=False),
    is_my_follower: bool = field(default=False)
