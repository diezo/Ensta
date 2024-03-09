from ensta.structures import ImageVersion


def parse_image_versions(candidates: list[dict]) -> list[ImageVersion]:

    versions: list[ImageVersion] = []

    for candidate in candidates:
        versions.append(
            ImageVersion(
                width=candidate.get("width"),
                height=candidate.get("height"),
                url=candidate.get("url"),
                scans_profile=candidate.get("scans_profile"),
            )
        )

    return versions
