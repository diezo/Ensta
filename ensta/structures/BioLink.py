from dataclasses import dataclass


@dataclass
class BioLink:

    """
    Stores a single input biography link's information e.g. - URL, Title, etc.
    """

    url: str
    title: str = ""
