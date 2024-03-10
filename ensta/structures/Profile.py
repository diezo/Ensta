from dataclasses import dataclass
from .ReturnedBioLink import ReturnedBioLink


@dataclass
class Profile:

    """
    Stores someone's profile information e.g. - Full name, Username, Biography, etc.
    """

    full_name: str
    username: str
    is_private: bool
    user_id: str
    is_profile_picture_expansion_enabled: bool
    is_opal_enabled: bool
    is_verified: bool
    profile_pic_url: str
    biography: str
    bio_links: tuple[ReturnedBioLink, ...]
    account_type: int
    is_business: bool
    media_count: int
    following_count: int
    follower_count: int
