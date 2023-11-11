from dataclasses import dataclass


@dataclass(frozen=True)
class PrivateInfo:

    first_name: str = None
    last_name: str = None
    email: str = None
    is_email_confirmed: bool = None
    is_phone_confirmed: bool = None
    username: str = None
    phone_number: str = None
    gender: str = None
    birthday: str = None
    fb_birthday: str = None
    biography: str = None
    external_url: str = None
    chaining_enabled: bool = None
    presence_disabled: bool = None
    business_account: bool = None
    user_tag_review_enabled: bool = None
    custom_gender: str = None
    trusted_username: str = None
    trust_days: int = None
