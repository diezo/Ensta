from dataclasses import dataclass


@dataclass(frozen=True)
class FollowListPerson:

    has_anonymous_profile_picture: bool
    user_id: str
    username: str
    full_name: str
    is_private: bool
    is_verified: bool
    profile_picture_url: str
    is_possible_scammer: bool
