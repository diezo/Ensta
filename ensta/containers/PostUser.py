from dataclasses import dataclass, field


@dataclass(frozen=False)
class PostUser:
    has_anonymous_profile_picture: bool = False
    fbid_v2: str = ""
    transparency_product_enabled: bool = False
    is_favorite: bool = False
    is_unpublished: bool = False
    uid: str = ""
    username: str = ""
    full_name: str = ""
    is_private: bool = False
    is_verified: bool = False
    profile_picture_id: str = ""
    profile_picture_url: str = ""
    account_badges: list = field(default_factory=list)
    feed_post_reshare_disabled: bool = False
    show_account_transparency_details: bool = False
    third_party_downloads_enabled: int = 0
    latest_reel_media: int = 0
