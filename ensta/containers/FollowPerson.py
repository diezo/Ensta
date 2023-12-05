from dataclasses import dataclass


@dataclass(frozen=True)
class FollowPerson:

    has_anonymous_profile_picture: bool = None
    user_id: str = None
    username: str = None
    full_name: str = None
    is_private: bool = None
    is_verified: bool = None
    profile_picture_url: str = None
    badges: list = None
    third_party_downloads_enabled: bool = None
