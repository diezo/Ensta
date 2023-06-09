from dataclasses import dataclass


@dataclass(frozen=True)
class FollowedStatus:

    following: bool = None
    follow_requested: bool = None
    is_my_follower: bool = None
    previous_following: bool = None
