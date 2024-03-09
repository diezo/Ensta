from dataclasses import dataclass


@dataclass
class Caption:

    """
    Stores post's caption information e.g. - Text, Created At, etc.
    """

    bit_flags: int
    created_at: int
    created_at_utc: int
    did_report_as_spam: bool
    is_ranked_comment: bool
    id: str
    share_enabled: bool
    content_type: str
    media_id: str
    status: str
    type: int
    user_id: str
    text: str
    is_covered: bool
    private_reply_status: int
