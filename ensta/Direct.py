from requests import Session, Response
from .containers.Inbox import Inbox
from uuid import uuid4
import string
import random
from .lib.Exceptions import FileTypeError, NetworkError
from json import JSONDecodeError
from pathlib import Path
from ensta.Utils import fb_uploader


class Direct:

    session: Session
    device_id: str

    def __init__(self, session: Session, device_id: str) -> None:
        self.session = session
        self.device_id = device_id

    def inbox(self) -> Inbox:
        """
        Fetches all the chats from inbox.
        :return: Inbox object with chat items and some other data
        """

        raise NotImplementedError()

    def send_text(self, text: str, thread_id: int, silently: bool = False) -> bool:
        """
        Sends a text message in a chat
        :param text: Text message
        :param thread_id: Thread ID of chat to send message to
        :param silently: Whether to send message without any notification
        :return: Boolean (Message sent or not)
        """

        mutation_token: str = str().join(random.choices(string.digits, k=19))

        response: Response = self.session.post(
            url="https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/",
            data={
                "action": "send_item",
                "is_x_transport_forward": False,
                "is_shh_mode": 0,
                "send_silently": silently,
                "thread_ids": f"[{thread_id}]",
                "send_attribution": "inbox",
                "client_context": mutation_token,
                "text": text,
                "device_id": self.device_id,
                "mutation_token": mutation_token,
                "_uuid": str(uuid4()),
                "btt_dual_send": False,
                "is_ae_dual_send": False,
                "offline_threading_id": mutation_token
            }
        )

        try:
            return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            return False

    def fb_upload_image(self, media_path: str) -> int:
        """
        Uploads given image to Instagram and returns MediaID.
        :param media_path: Local path of image
        :return: MediaID (Integer)
        """

        media_path: Path = Path(media_path)

        if media_path.suffix not in (".jpg", ".jpeg"):
            raise FileTypeError(
                "Only jpg and jpeg image types can be uploaded."
            )

        with open(media_path, "rb") as file:
            media_data: bytes = file.read()

        upload_name: str = fb_uploader()
        media_length: str = str(len(media_data))

        response: Response = self.session.post(
            url=f"https://rupload.facebook.com/messenger_image/{upload_name}",
            headers={
                "content-length": media_length,
                "content-type": "application/octet-stream",
                "host": "rupload.facebook.com",
                "x-entity-name": upload_name,
                "x-entity-type": "image/jpeg",
                "x-entity-length": media_length,
                "offset": "0",
                "image_type": "FILE_ATTACHMENT"
            },
            data=media_data
        )

        try:
            return response.json().get("media_id")

        except JSONDecodeError:
            raise NetworkError(
                "Unable to upload image. Make sure there's nothing wrong with the image. "
                "If this problem persists, try using a different account, switch to a different "
                "network, or use reputed proxies."
            )

    def send_photo(self, media_id: int, thread_id: int) -> bool:
        """
        Sends a photo in a chat
        :param media_id: Media ID of photo received by uploading it to 'FB Uploader'
        :param thread_id: Thread ID of chat to send photo to
        :return: Boolean (Photo sent or not)
        """

        mutation_token: str = str().join(random.choices(string.digits, k=19))

        response: Response = self.session.post(
            url="https://i.instagram.com/api/v1/direct_v2/threads/broadcast/photo_attachment/",
            data={
                "action": "send_item",
                "is_x_transport_forward": False,
                "is_shh_mode": 0,
                "thread_ids": f"[{thread_id}]",
                "send_attribution": "inbox",
                "client_context": mutation_token,
                "attachment_fbid": media_id,
                "device_id": self.device_id,
                "mutation_token": mutation_token,
                "_uuid": str(uuid4()),
                "allow_full_aspect_ratio": True,
                "btt_dual_send": False,
                "is_ae_dual_send": False,
                "offline_threading_id": mutation_token
            }
        )

        try:
            return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            return False
