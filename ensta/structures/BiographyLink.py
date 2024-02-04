from dataclasses import dataclass

@dataclass
class BiographyLink:

    """
    Stores a single biography link's information e.g. - Link Title, Link URL, Link ID, etc.
    """

    link_id: int
    url: str
    lynx_url: str
    link_type: str
    title: str
    is_pinned: bool
    open_external_url_with_in_app_browser: bool
    click_id: str
