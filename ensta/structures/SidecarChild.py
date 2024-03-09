from dataclasses import dataclass


@dataclass
class SidecarChild:

    """
    Stores single sidecar's child information e.g. - UploadID, Alt Text etc.
    """

    upload_id: str
    alt_text: str = ""
