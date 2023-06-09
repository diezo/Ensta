from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:

    success: bool = False
    biography: str = None
    country_block: bool = None
    full_name: str = None
    follower_count: int = None
    following_count: int = None
    user_id: str = None
    is_business_account: bool = None
    is_professional_account: bool = None
    is_supervision_enabled: bool = None
    is_joined_recently: bool = None
    is_private: bool = None
    is_verified: bool = None
    profile_picture_url: str = None
    profile_picture_url_hd: str = None
    pronouns: list[str] = None
