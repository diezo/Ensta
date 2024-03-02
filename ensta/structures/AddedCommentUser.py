from dataclasses import dataclass


@dataclass
class AddedCommentUser:

    """
    Stores information of user who added the comment (you) e.g. - User ID, Username, Full Name, etc.
    """

    user_id: str
    username: str
    full_name: str
    is_private: bool
    has_onboarded_to_text_post_app: bool
    fbid_v2: str
    is_verified: bool
    profile_picture_id: str
    profile_picture_url: str
    is_mentionable: bool
    latest_reel_media: int
    latest_besties_reel_media: int
