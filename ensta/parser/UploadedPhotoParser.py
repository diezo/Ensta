from ensta.structures import UploadedPhoto, Caption, ImageVersion
from .CaptionParser import parse_caption
from .ImageVersionsParser import parse_image_versions


def parse_uploaded_photo(information: dict) -> UploadedPhoto:

    caption: Caption = parse_caption(information.get("caption", {}))
    image_versions: list[ImageVersion] = parse_image_versions(information.get("image_versions2", {}).get("candidates", []))

    return UploadedPhoto(
        taken_at=information.get("taken_at"),
        primary_key=information.get("pk"),
        media_id=information.get("id"),
        device_timestamp=information.get("device_timestamp"),
        caption_is_edited=information.get("caption_is_edited"),
        like_and_view_counts_disabled=information.get("like_and_view_counts_disabled"),
        has_hidden_comments=information.get("has_hidden_comments"),
        is_post_live_clips_media=information.get("is_post_live_clips_media"),
        has_shared_to_fb=information.get("has_shared_to_fb"),
        is_unified_video=information.get("is_unified_video"),
        is_quiet_post=information.get("is_quiet_post"),
        media_type=information.get("media_type"),
        share_url=f"https://instagram.com/p/{information.get('code')}" if information.get("code", "") != "" else None,
        code=information.get("code"),
        caption=caption,
        image_versions=image_versions,
        original_width=information.get("original_width"),
        original_height=information.get("original_height"),
        can_view_more_preview_comments=information.get("can_view_more_preview_comments")
    )
