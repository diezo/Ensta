from dataclasses import dataclass


@dataclass
class PrivateInfo:

    """
    Stores your account's private information e.g. - Full Name, Email, Phone Number, etc.
    """

    full_name: str
    is_private: bool
    user_id: str
    username: str
    biography: str
    show_fb_link_on_profile: bool
    account_type: int
    country_code: int
    custom_gender: str
    email: str
    gender: int
    has_anonymous_profile_picture: bool
    profile_pic_id: str
    phone_number: str
    national_number: int
    is_verified: bool
    profile_pic_url: str
    trusted_username: str
    trust_days: int
