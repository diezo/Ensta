from ensta.structures import Caption


def parse_caption(information: dict) -> Caption:

    return Caption(
        bit_flags=information.get("bit_flags"),
        created_at=information.get("created_at"),
        created_at_utc=information.get("created_at_utc"),
        did_report_as_spam=information.get("did_report_as_spam"),
        is_ranked_comment=information.get("is_ranked_comment"),
        id=information.get("pk"),
        share_enabled=information.get("share_enabled"),
        content_type=information.get("content_type"),
        media_id=str(information.get("media_id")),
        status=information.get("status"),
        type=information.get("type"),
        user_id=str(information.get("user_id")),
        text=information.get("text"),
        is_covered=information.get("is_covered"),
        private_reply_status=information.get("private_reply_status")
    )
