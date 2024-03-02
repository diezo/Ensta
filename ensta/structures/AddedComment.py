from dataclasses import dataclass
from .AddedCommentUser import AddedCommentUser


@dataclass
class AddedComment:

    """
    Stores information about the comment you posted e.g. - Comment ID, Text, Comment Type etc.
    """

    comment_id: str
    user_id: str
    type: int
    did_report_as_spam: bool
    created_at: int
    created_at_utc: int
    content_type: str
    status: str
    bit_flags: int
    share_enabled: bool
    is_ranked_comment: bool
    media_id: str
    restricted_status: int
    is_created_by_media_owner: bool
    user: AddedCommentUser
    text: str
    is_covered: bool
    comment_creation_key: str
