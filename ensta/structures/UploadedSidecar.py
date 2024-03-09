from dataclasses import dataclass
from .Caption import Caption
from .ImageVersion import ImageVersion
from .CarouselMedia import CarouselMedia


@dataclass
class UploadedSidecar:

    """
    Stores uploaded sidecar's information e.g. - Sidecar ID, Media ID, Uploaded Time, Caption, etc.
    """

    taken_at: int
    primary_key: str
    media_id: str
    device_timestamp: int
    caption_is_edited: bool
    like_and_view_counts_disabled: bool
    has_hidden_comments: bool
    is_post_live_clips_media: bool
    has_shared_to_fb: bool
    is_unified_video: bool
    is_quiet_post: bool
    media_type: int
    share_url: str
    code: str
    caption: Caption
    image_versions: list[ImageVersion]
    original_width: int
    original_height: int
    can_view_more_preview_comments: bool

    # Specific for Sidecar
    sidecar_id: str
    carousel_media: list[CarouselMedia]
    carousel_media_count: int
    carousel_media_ids: list[int]
    carousel_media_pending_post_count: int
