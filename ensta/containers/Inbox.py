from dataclasses import dataclass
from .DirectThread import DirectThread


@dataclass(frozen=False)
class Inbox:

    unseen_count: int = None
    unseen_count_timestamp: int = None
    threads: list[DirectThread] = None
