from dataclasses import dataclass


@dataclass
class ImageVersion:

    """
    Stores post's image version information e.g. - Image URL, Width, Height, etc.
    """

    width: int
    height: int

    url: str

    scans_profile: str
