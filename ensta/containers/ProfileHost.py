from dataclasses import dataclass
from .Profile import Profile


@dataclass(frozen=False)
class ProfileHost(Profile):

    blocked_by_viewer: bool = None
    followed_by_viewer: bool = None
    follows_viewer: bool = None
    has_blocked_viewer: bool = None
    has_requested_viewer: bool = None
    is_guardian_of_viewer: bool = None
    is_supervised_by_viewer: bool = None
    requested_by_viewer: bool = None
    mutual_follower_count: int = None
