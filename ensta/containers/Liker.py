from dataclasses import dataclass


@dataclass(frozen=True)
class Liker:

    user_id: str = None
    username: str = None
    full_name: str = None
    is_private: bool = None
    badges: list = None
    is_verified: bool = None
    profile_picture_id: str = None
    profile_picture_url: str = None
    latest_reel_media: int = None
