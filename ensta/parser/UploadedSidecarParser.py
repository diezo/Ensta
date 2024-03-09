from ensta.structures import UploadedSidecar, Caption, ImageVersion, CarouselMedia
from .CaptionParser import parse_caption
from .ImageVersionsParser import parse_image_versions
from .CarouselMediaParser import parse_carousel_media


def parse_uploaded_sidecar(information: dict) -> UploadedSidecar:

    media: dict = information.get("media", {})

    caption: Caption = parse_caption(media.get("caption", {}))
    image_versions: list[ImageVersion] = parse_image_versions(media.get("image_versions2", {}).get("candidates", []))
    carousel_media: list[CarouselMedia] = parse_carousel_media(media.get("carousel_media", []))

    return UploadedSidecar(
        taken_at=media.get("taken_at"),
        primary_key=media.get("pk"),
        media_id=media.get("id"),
        device_timestamp=media.get("device_timestamp"),
        caption_is_edited=media.get("caption_is_edited"),
        like_and_view_counts_disabled=media.get("like_and_view_counts_disabled"),
        has_hidden_comments=media.get("has_hidden_comments"),
        is_post_live_clips_media=media.get("is_post_live_clips_media"),
        has_shared_to_fb=media.get("has_shared_to_fb"),
        is_unified_video=media.get("is_unified_video"),
        is_quiet_post=media.get("is_quiet_post"),
        media_type=media.get("media_type"),
        share_url=f"https://instagram.com/p/{media.get('code')}" if media.get("code", "") != "" else None,
        code=media.get("code"),
        caption=caption,
        image_versions=image_versions,
        original_width=media.get("original_width"),
        original_height=media.get("original_height"),
        can_view_more_preview_comments=media.get("can_view_more_preview_comments"),

        # Specific for Sidecar
        sidecar_id=information.get("client_sidecar_id"),
        carousel_media=carousel_media,
        carousel_media_count=media.get("carousel_media_count"),
        carousel_media_ids=media.get("carousel_media_ids"),
        carousel_media_pending_post_count=media.get("carousel_media_pending_post_count")
    )
