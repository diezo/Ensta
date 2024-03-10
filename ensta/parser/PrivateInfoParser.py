from ensta.structures.PrivateInfo import PrivateInfo


def parse_private_info(information: dict) -> PrivateInfo:

    return PrivateInfo(
        full_name=information.get("full_name"),
        is_private=information.get("is_private"),
        user_id=information.get("pk_id"),
        username=information.get("username"),
        biography=information.get("biography"),
        show_fb_link_on_profile=information.get("show_fb_link_on_profile"),
        account_type=information.get("account_type"),
        country_code=information.get("country_code"),
        custom_gender=information.get("custom_gender"),
        email=information.get("email"),
        gender=information.get("gender"),
        has_anonymous_profile_picture=information.get("has_anonymous_profile_picture"),
        profile_pic_id=information.get("profile_pic_id"),
        phone_number=information.get("phone_number"),
        national_number=information.get("national_number"),
        is_verified=information.get("is_verified"),
        profile_pic_url=information.get("profile_pic_url"),
        trusted_username=information.get("trusted_username"),
        trust_days=information.get("trust_days")
    )
