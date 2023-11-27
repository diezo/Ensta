from .PostUser import PostUser
from dataclasses import dataclass, field


@dataclass(frozen=False)
class Post:
    share_url: str = ""
    taken_at: int = 0
    post_id: str = ""
    media_type: int = 0
    code: str = ""
    caption_is_edited: bool = False
    original_media_has_visual_reply_media: bool = False
    like_and_view_counts_disabled: bool = False
    can_viewer_save: bool = False
    profile_grid_control_enabled: bool = False
    is_comments_gif_composer_enabled: bool = False
    comment_threading_enabled: bool = False
    comment_count: int = 0
    has_liked: bool = False
    user: PostUser = field(default_factory=PostUser)
    can_viewer_reshare: bool = False
    like_count: int = 0
    top_likers: list[str] = field(default_factory=list)
    caption_text: str = ""
    is_caption_covered: bool = False
    caption_created_at: int = 0
    caption_share_enabled: bool = False
    caption_did_report_as_spam: bool = False
    is_paid_partnership: bool = False
    show_shop_entrypoint: bool = False
    deleted_reason: int = 0
    integrity_review_decision: str = ""
    ig_media_sharing_disabled: bool = False
    has_shared_to_fb: int = 0
    is_unified_video: bool = False
    should_request_ads: bool = False
    is_visual_reply_commenter_notice_enabled: bool = False
    commerciality_status: str = ""
    explore_hide_comments: bool = False
    has_delayed_metadata: bool = False
    location_latitude: float = 0
    location_longitude: float = 0
