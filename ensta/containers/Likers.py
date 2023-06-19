from dataclasses import dataclass
from .Liker import Liker


@dataclass(frozen=True)
class Likers:

    user_count: int = None
    users: list[Liker] = None
