from typing import Any, List
from .Shared import CommentInformTreatment, SharingFrictionInfo
from dataclasses import dataclass
from .BaseResponseData import BaseResponseData


@dataclass(frozen=True)
class PhotoUpload(BaseResponseData):
    raw: dict
    taken_at: int
    pk: str
    id: str
    device_timestamp: int
    client_cache_key: str
    filter_type: int
    caption_is_edited: bool
    like_and_view_counts_disabled: bool
    strong_id__: str
    is_reshare_of_text_post_app_media_in_ig: bool
    has_hidden_comments: bool
    is_post_live_clips_media: bool
    deleted_reason: int
    integrity_review_decision: str
    has_shared_to_fb: int
    is_unified_video: bool
    should_request_ads: bool
    is_visual_reply_commenter_notice_enabled: bool
    commerciality_status: str
    explore_hide_comments: bool
    has_delayed_metadata: bool
    is_quiet_post: bool
    mezql_token: str
    shop_routing_user_id: Any
    can_see_insights_as_brand: bool
    is_organic_product_tagging_eligible: bool
    has_privately_liked: bool
    likers: List
    media_type: int
    code: str
    can_viewer_reshare: bool
    caption: dict  # @TODO caption dataclass
    clips_tab_pinned_user_ids: List  # @TODO
    comment_inform_treatment: CommentInformTreatment
    sharing_friction_info: SharingFrictionInfo
    accessibility_caption: str
    original_media_has_visual_reply_media: bool
    fb_user_tags: Any  # @TODO
    invited_coauthor_producers: List  # @TODO
    can_viewer_save: bool
    is_in_profile_grid: bool
    profile_grid_control_enabled: bool
    featured_products: List  # @TODO
    is_comments_gif_composer_enabled: bool
    highlights_info: Any  # @TODO
    product_suggestions: Any  # @TODO
    user: Any  # @TODO
    image_versions2: Any  # @TODO
    original_width: int
    original_height: int
    enable_media_notes_production: bool
    product_type: str
    is_paid_partnership: bool
    music_metadata: Any  # @TODO
    organic_tracking_token: str
    ig_media_sharing_disabled: bool
    boosted_status: str
    boost_unavailable_identifier: Any  # @TODO
    boost_unavailable_reason: Any  # @TODO
    open_carousel_submission_state: str
    is_open_to_public_submission: bool
    commenting_disabled_for_viewer: bool
    comment_threading_enabled: bool
    max_num_visible_preview_comments: int
    has_more_comments: bool
    preview_comments: List  # @TODO
    comments: List  # @TODO
    comment_count: int
    can_view_more_preview_comments: bool
    hide_view_all_comment_entrypoint: bool
    is_auto_created: bool
    is_cutout_sticker_allowed: bool
    owner: Any  # @TODO
