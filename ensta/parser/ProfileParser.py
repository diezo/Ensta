from ensta.structures.Profile import Profile
from .BiographyLinkParser import parse_biography_link


def parse_profile(information: dict) -> Profile:

    user: dict = information.get("user", {})

    profile = Profile(
        full_name=user.get("full_name"),
        username=user.get("username"),
        is_private=user.get("is_private"),
        user_id=user.get("pk"),
        is_profile_picture_expansion_enabled=user.get("is_profile_picture_expansion_enabled"),
        is_opal_enabled=user.get("is_opal_enabled"),
        is_verified=user.get("is_verified"),
        profile_pic_url=user.get("profile_pic_url"),
        biography=user.get("biography"),
        bio_links=tuple(
            parse_biography_link(link) for link in user.get("bio_links", [])
        ),
        account_type=user.get("account_type"),
        is_business=user.get("is_business"),
        media_count=user.get("media_count"),
        following_count=user.get("following_count"),
        follower_count=user.get("follower_count")
    )

    return profile
