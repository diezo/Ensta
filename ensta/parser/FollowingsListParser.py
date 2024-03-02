from ensta.structures.Following import Following


def parse_followings_list(items: list[dict]) -> list[Following]:

    followings = list()

    for item in items:

        followings.append(
            Following(
                user_id=str(item.get("pk")),
                username=item.get("username"),
                full_name=item.get("full_name"),
                is_private=item.get("is_private"),
                fbid_v2=item.get("fbid_v2"),
                third_party_downloads_enabled=item.get("third_party_downloads_enabled"),
                profile_picture_id=item.get("profile_pic_id"),
                profile_picture_url=item.get("profile_pic_url"),
                is_verified=item.get("is_verified"),
                has_anonymous_profile_picture=item.get("has_anonymous_profile_picture"),
                latest_reel_media=item.get("latest_reel_media"),
                is_favorite=item.get("is_favorite")
            )
        )

    return followings
