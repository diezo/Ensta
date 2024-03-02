from dataclasses import dataclass


@dataclass
class Follower:

    """
    Stores single follower information e.g. - Full Name, Username, Profile Picture Url, etc.
    """

    user_id: str
    username: str
    full_name: str
    is_private: bool
    fbid_v2: str
    third_party_downloads_enabled: int
    profile_picture_id: str
    profile_picture_url: str
    is_verified: bool
    has_anonymous_profile_picture: bool
    latest_reel_media: int
