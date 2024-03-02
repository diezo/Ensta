from ensta.structures.Followings import Followings
from ensta.structures.Following import Following
from .FollowingsListParser import parse_followings_list


def parse_followings(information: dict) -> Followings:

    followings_list: list[Following] = parse_followings_list(information.get("users"))

    return Followings(
        list=followings_list,
        next_cursor=information.get("next_max_id"),
        big_list=information.get("big_list"),
        list_length=information.get("page_size"),
        hashtag_count=information.get("hashtag_count"),
        has_more=information.get("has_more"),
        should_limit_list_of_followers=information.get("should_limit_list_of_followers"),
        use_clickable_see_more=information.get("use_clickable_see_more"),
    )
