from dataclasses import dataclass


@dataclass(frozen=False)
class Profile:

    raw: dict = None
    biography: str = None
    biography_links: list = None
    country_block: bool = None
    full_name: str = None
    follower_count: int = None
    following_count: int = None
    user_id: str = None
    category_name: str = None
    is_business_account: bool = None
    is_professional_account: bool = None
    is_supervision_enabled: bool = None
    is_joined_recently: bool = None
    is_private: bool = None
    is_verified: bool = None
    profile_picture_url: str = None
    profile_picture_url_hd: str = None
    pronouns: list[str] = None,
    has_ar_effects: bool = None,
    has_clips: bool = None,
    has_guides: bool = None,
    has_channel: bool = None,
    highlight_count: int = None,
    hide_like_and_view_counts: bool = None,
    is_embeds_disabled: bool = None,
    is_verified_by_mv4b: bool = None,
    should_show_category: bool = None,
    should_show_public_contacts: bool = None,
    show_account_transparency_details: bool = None,
    total_post_count: int = None
