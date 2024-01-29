from .BaseResponseData import BaseResponseData
from .Shared import SharingFrictionInfo
from typing import Any, List
from dataclasses import dataclass


@dataclass
class Comment(BaseResponseData):
    pk: str
    user: Any
    is_covered: bool
    child_comment_count: int
    restricted_status: int
    parent_comment_id: Any
    has_translation: Any
    has_liked_comment: bool
    text: str
    created_at: int
    comment_like_count: int
    giphy_media_info: Any


@dataclass
class Caption(BaseResponseData):
    pk: str
    text: str


@dataclass
class PostDetail(BaseResponseData):
    code: str
    pk: str
    id: str
    ad_id: Any
    taken_at: int
    inventory_source: Any
    video_versions: List
    facepile_top_likers: List
    is_dash_eligible: int
    number_of_qualities: int
    video_dash_manifest: str
    image_versions2: Any
    is_paid_partnership: bool
    sponsor_tags: Any
    original_height: int
    original_width: int
    organic_tracking_token: str
    user: Any
    group: Any
    comments_disabled: Any
    like_and_view_counts_disabled: bool
    can_viewer_reshare: bool
    product_type: str
    media_type: int
    usertags: Any
    media_overlay_info: Any
    carousel_media: Any
    location: Any
    has_audio: bool
    clips_metadata: Any
    clips_attribution_info: Any
    has_liked: bool
    carousel_parent_id: Any
    top_likers: List[str]
    like_count: int
    view_count: Any
    owner: Any
    social_context: Any
    saved_collection_ids: Any
    has_viewer_saved: Any
    ig_media_sharing_disabled: bool
    feed_demotion_control: Any
    feed_recs_demotion_control: Any
    photo_of_you: Any
    caption: Caption
    can_reshare: Any
    expiring_at: Any
    link: Any
    story_cta: Any
    logging_info_token: Any
    sharing_friction_info: SharingFrictionInfo
    carousel_media_count: Any
    can_see_insights_as_brand: bool
    coauthor_producers: Any
    follow_hashtag_info: Any
    affiliate_info: Any
    preview: Any
    comment_count: int
    comments: List[Comment]
    boosted_status: str
    boost_unavailable_identifier: Any
    boost_unavailable_reason: Any
    caption_is_edited: bool
    main_feed_carousel_starting_media_id: Any
    commenting_disabled_for_viewer: bool
    title: Any
    accessibility_caption: Any
    audience: Any
    media_cropping_info: Any
    thumbnails: Any
    timeline_pinned_user_ids: Any
    upcoming_event: Any
