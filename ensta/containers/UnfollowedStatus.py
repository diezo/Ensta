from dataclasses import dataclass


@dataclass(frozen=True)
class UnfollowedStatus:

    unfollowed: bool = None
    is_my_follower: bool = None
