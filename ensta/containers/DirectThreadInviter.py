from dataclasses import dataclass


@dataclass(frozen=False)
class DirectThreadInviter:

    user_id: str = None
    username: str = None
    full_name: str = None
    profile_picture_url: str = None
    profile_picture_id: str = None
    is_private: bool = None
    is_verified: bool = None
    allowed_commenter_type: str = None
    reel_auto_archive: str = None
    has_onboarded_to_text_post_app: bool = None
    third_party_downloads_enabled: int = None
    has_anonymous_profile_picture: bool = None
    all_media_count: int = None
    liked_clips_count: int = None
    reachability_status: int = None
    has_encrypted_backup: bool = None
