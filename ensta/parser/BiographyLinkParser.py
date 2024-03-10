from ensta.structures.ReturnedBioLink import ReturnedBioLink


def parse_biography_link(information: dict) -> ReturnedBioLink:

    link = ReturnedBioLink(
        link_id=information.get("link_id"),
        url=information.get("url"),
        lynx_url=information.get("lynx_url"),
        link_type=information.get("link_type"),
        title=information.get("title"),
        is_pinned=information.get("is_pinned"),
        open_external_url_with_in_app_browser=information.get("open_external_url_with_in_app_browser"),
        click_id=information.get("click_id")
    )

    return link
