from ensta.structures.Followers import Followers
from ensta.structures.Follower import Follower
from .FollowersListParser import parse_followers_list


def parse_followers(information: dict) -> Followers:

    followers_list: list[Follower] = parse_followers_list(information.get("users"))

    return Followers(
        list=followers_list,
        next_cursor=information.get("next_max_id"),
        big_list=information.get("big_list"),
        list_length=information.get("page_size"),
        has_more=information.get("has_more"),
        should_limit_list_of_followers=information.get("should_limit_list_of_followers"),
        use_clickable_see_more=information.get("use_clickable_see_more"),
        show_spam_follow_request_tab=information.get("show_spam_follow_request_tab")
    )
