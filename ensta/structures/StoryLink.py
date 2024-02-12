from dataclasses import dataclass


@dataclass
class StoryLink:

    url: str
    title: str = ""

    tap_state_str_id: str = "link_sticker_default"
    type: str = "story_link"
    is_sticker: bool = True
    link_type: str = "web"
    tap_state: int = 0

    x: float = 0.5
    y: float = 0.49980468
    z: float = 0

    width: float = 0.45520985
    height: float = 0.06875
    rotation: float = 0.0
