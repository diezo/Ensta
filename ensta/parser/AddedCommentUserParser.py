from ensta.structures.AddedCommentUser import AddedCommentUser


def parse_added_comment_user(information: dict) -> AddedCommentUser:

    return AddedCommentUser(
        user_id=str(information.get("pk")),
        username=information.get("username"),
        full_name=information.get("full_name"),
        is_private=information.get("is_private"),
        has_onboarded_to_text_post_app=information.get("has_onboarded_to_text_post_app"),
        fbid_v2=str(information.get("fbid_v2")),
        is_verified=information.get("is_verified"),
        profile_picture_id=information.get("profile_pic_id"),
        profile_picture_url=information.get("profile_pic_url"),
        is_mentionable=information.get("is_mentionable"),
        latest_reel_media=information.get("latest_reel_media"),
        latest_besties_reel_media=information.get("latest_besties_reel_media")
    )
