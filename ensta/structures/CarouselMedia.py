from dataclasses import dataclass
from .ImageVersion import ImageVersion


@dataclass
class CarouselMedia:

    """
    Stores each uploaded carousel media's information e.g. - Media ID, Uploaded Time, Caption, etc.
    """

    media_id: str
    taken_at: int
    product_type: str
    media_type: int

    image_versions: list[ImageVersion]
    original_width: int
    original_height: int
