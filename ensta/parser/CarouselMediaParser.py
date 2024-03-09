from ensta.structures import CarouselMedia
from .ImageVersionsParser import parse_image_versions


def parse_carousel_media(media: list[dict]) -> list[CarouselMedia]:

    elements: list[CarouselMedia] = []

    for each in media:
        elements.append(
            CarouselMedia(
                media_id=each.get("id"),
                taken_at=each.get("taken_at"),
                product_type=each.get("product_type"),
                media_type=each.get("media_type"),
                image_versions=parse_image_versions(each.get("image_versions2", {}).get("candidates", [])),
                original_width=each.get("original_width"),
                original_height=each.get("original_height")
            )
        )

    return elements
