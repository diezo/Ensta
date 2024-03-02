from dataclasses import dataclass
from .Follower import Follower


@dataclass
class Followers:

    """
    Stores fetched followers information e.g. - List, Next Cursor, List Length, etc.
    """

    list: list[Follower]
    next_cursor: int
    big_list: bool
    list_length: int
    has_more: bool
    should_limit_list_of_followers: bool
    use_clickable_see_more: bool
    show_spam_follow_request_tab: bool
