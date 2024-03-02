from dataclasses import dataclass
from .Following import Following


@dataclass
class Followings:

    """
    Stores fetched followings information e.g. - List, Next Cursor, List Length, etc.
    """

    list: list[Following]
    next_cursor: int
    big_list: bool
    list_length: int
    hashtag_count: int
    has_more: bool
    should_limit_list_of_followers: bool
    use_clickable_see_more: bool
