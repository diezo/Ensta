from ensta.structures.AddedComment import AddedComment
from ensta.structures.AddedCommentUser import AddedCommentUser
from .AddedCommentUserParser import parse_added_comment_user


def parse_added_comment(information: dict) -> AddedComment:

    comment_dict: dict = information.get("comment")
    user: AddedCommentUser = parse_added_comment_user(comment_dict.get("user"))

    return AddedComment(
        comment_id=comment_dict.get("pk"),
        user_id=str(comment_dict.get("user_id")),
        type=comment_dict.get("type"),
        did_report_as_spam=comment_dict.get("did_report_as_spam"),
        created_at=comment_dict.get("created_at"),
        created_at_utc=comment_dict.get("created_at_utc"),
        content_type=comment_dict.get("content_type"),
        status=comment_dict.get("status"),
        bit_flags=comment_dict.get("bit_flags"),
        share_enabled=comment_dict.get("share_enabled"),
        is_ranked_comment=comment_dict.get("is_ranked_comment"),
        media_id=str(comment_dict.get("media_id")),
        restricted_status=comment_dict.get("restricted_status"),
        is_created_by_media_owner=comment_dict.get("is_created_by_media_owner"),
        user=user,
        text=comment_dict.get("text"),
        is_covered=comment_dict.get("is_covered"),
        comment_creation_key=information.get("comment_creation_key")
    )
