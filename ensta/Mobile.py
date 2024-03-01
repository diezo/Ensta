from requests import Session, Response
from .Credentials import Credentials
from .lib.Exceptions import AuthenticationError, FileTypeError, NetworkError
from uuid import uuid4
from json import  JSONDecodeError
from pathlib import Path
import string
import datetime
import json
from .parser.ProfileParser import parse_profile
from .structures import Profile, StoryLink
from .Direct import Direct
from ensta.Utils import time_id, fb_uploader

class Mobile:

    session: Session
    credentials: Credentials

    bearer: str
    user_id: str
    username: str
    phone_id: str
    device_id: str
    identifier: str

    credentials_refresh_max_cycle: int = 3

    authorization_url: str = "https://i.instagram.com/api/v1/wwwgraphql/ig/query/"

    user_agent: str = "Instagram 317.0.0.24.109 Android (31/12; 640dpi; 1440x3056; " \
                      "OnePlus; GM1911; OnePlus7Pro; qcom; en_US; 562739837)"

    def __init__(
        self,
        identifier: str = None,
        password: str = None,
        proxy: dict[str, str] = None,
        save_folder: str = "ensta-sessions",
        skip_auth_check: bool = False,
        logging: bool = False,
        totp_token : str = None,
        session_data: str = None
    ) -> None:

        self.session = Session()

        if proxy: self.session.proxies.update(proxy)

        self.refresh_credentials(
            cycle=1,
            identifier=identifier,
            password=password,
            save_folder=save_folder,
            logging=logging,
            totp_token=totp_token,
            session_data=session_data,
            skip_auth_check=skip_auth_check
        )

    def refresh_credentials(
        self,
        cycle: int,
        identifier: str,
        password: str,
        save_folder: str,
        logging: bool,
        totp_token: str,
        session_data: str,
        skip_auth_check: bool
    ) -> None:

        if logging: print(f"Login Attempt: {cycle} (Max: {self.credentials_refresh_max_cycle})")

        if cycle >= self.credentials_refresh_max_cycle:
            raise AuthenticationError(
                "Reached max number of login attempts while authorizing credentials. "
                "Make sure your network is stable. If required, use reputed proxies."
            )

        self.credentials = Credentials(
            identifier=identifier,
            password=password,
            session=self.session,
            user_agent=self.user_agent,
            save_folder=save_folder,
            totp_token=totp_token,
            session_data=session_data,
            logging=logging
        )

        self.bearer = self.credentials.bearer
        self.user_id = self.credentials.user_id
        self.username = self.credentials.username
        self.phone_id = self.credentials.phone_id
        self.identifier = self.credentials.stored_identifier
        self.device_id = self.credentials.device_id

        self.session.headers.update({
            "authorization": self.credentials.bearer,
            "host": "i.instagram.com",
            "ig-intended-user-id": self.user_id,
            "ig-u-ds-user-id": self.user_id,
            "user-agent": self.user_agent,
            "x-ig-device-id": self.phone_id,
            "x-ig-device-locale": "en_US",
            "x-ig-family-device-id": self.phone_id,
            "x-fb-connection-type": "WIFI",
            "x-fb-http-engine": "Tigon-TCP-Fallback",
            "x-ig-android-id": self.device_id,
        })

        # Authorization: Is the current session even valid?
        if not skip_auth_check:
            if not self.authorize():
                self.refresh_credentials(
                    cycle=cycle + 1,
                    identifier=identifier,
                    password=password,
                    save_folder=save_folder,
                    logging=logging,
                    totp_token=totp_token,
                    session_data=session_data,
                    skip_auth_check=skip_auth_check
                )

    def authorize(self) -> bool:
        return self.session.post(self.authorization_url).status_code == 400

    # TASK: Use FB Uploader; Currently uses Web API
    def get_upload_id(self, media_path: str, arg_upload_id: str | None = None) -> str:
        """
        Uploads the image to Instagram's server using Web API and returns its UploadID.
        :param media_path: Path to the image file (only jpg & jpeg)
        :param arg_upload_id: Custom upload_id (for advanced users)
        :return: UploadID of picture
        """

        media_path: Path = Path(media_path)

        if media_path.suffix not in (".jpg", ".jpeg"):
            raise FileTypeError(
                "Only jpg and jpeg image types are allowed to upload."
            )

        upload_id = arg_upload_id if arg_upload_id is not None else time_id()
        upload_name = fb_uploader(upload_id)

        rupload_params = {
            "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
            "media_type": "1",
            "xsharing_user_ids": "[]",
            "upload_id": upload_id,
            "image_compression": json.dumps({"lib_name": "moz", "lib_version": "3.1.m", "quality": 80})
        }

        with open(media_path, "rb") as file:
            photo_data = file.read()
            photo_length = str(len(photo_data))

        request_headers = {
            "accept-encoding": "gzip",
            "x-instagram-rupload-params": json.dumps(rupload_params),
            "x_fb_photo_waterfall_id": str(uuid4()),
            "x-entity-type": "image/jpeg",
            "offset": "0",
            "x-entity-name": upload_name,
            "x-entity-length": photo_length,
            "content-type": "application/octet-stream",
            "content-length": photo_length
        }

        http_response = self.session.post(
            url=f"https://i.instagram.com/rupload_igphoto/{upload_name}",
            data=photo_data,
            headers=request_headers
        )

        try:
            response_dict: dict = http_response.json()

            if response_dict.get("status", "") != "ok": raise NetworkError("Response json key 'status' not ok.")
            if response_dict.get("upload_id") is None:
                raise NetworkError(
                    "Key 'upload_id' in response json doesn't exist. Make sure there's "
                    "nothing wrong with the image you're uploading."
                )

            return str(response_dict.get("upload_id"))

        except JSONDecodeError: raise NetworkError("Response not a valid json.")

    def change_profile_picture(self, image_path: str) -> bool:
        """
        Changes your profile picture to a new one.
        :param image_path: Path of image to be used
        :return: Boolean (Successfully changed or not)
        """

        upload_id: str = self.get_upload_id(image_path)

        headers: dict = {
            "accept-encoding": "gzip",
            "accept-language": "en-US",
            "connection": "Keep-Alive",
            "content-length": "1",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "priority": "u=3",
            "x-bloks-is-layout-rtl": "false",
            "x-bloks-is-prism-enabled": "false",
            "x-bloks-version-id": "979a6b0480455edae83004a50ceae0a15cbe5e943d3786ec785eb85b693c5300",
            "x-ig-app-id": "567067343352427"
        }

        try:
            response: Response = self.session.post(
                "https://i.instagram.com/api/v1/accounts/change_profile_picture/",
                data={
                    "_uuid": str(uuid4()),
                    "use_fbuploader": False,
                    "remove_birthday_selfie": False,
                    "upload_id": upload_id
                },
                headers=headers
            )

            return response.json().get("status", "") == "ok"

        except JSONDecodeError: return False

    def profile(self, identifier: str) -> Profile:
        """
        Fetches profile information of specified Username or UserID, and returns a Profile Object.
        :param identifier: Username or UserID of target
        :return: Profile Object
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/users/{identifier}/"
                f"{'username' if self.is_username(identifier) else ''}info_stream/",
            headers={
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "accept-encoding": "gzip",
                "accept-language": "en-US",
                "connection": "Keep-Alive"
            },
            data={
                "is_prefetch": False,
                "entry_point": "profile",
                "from_module": "search_typeahead",
                "_uuid": str(uuid4())
            }
        )

        try:
            # Response actually returns two JSON Objects with profile information,
            # but we'll only use the 1st one for now.

            information: dict = tuple(json.loads(data) for data in response.text.strip().split("\n"))[0]

            if information.get("status", "") != "ok":
                raise NetworkError(
                    "Cannot fetch profile. Is the username correct? "
                    "Maybe try logging in with a different account as "
                    "this one may has been flagged."
                )

            return parse_profile(information)

        except JSONDecodeError:
            raise NetworkError(
                "Can't fetch profile info. Make sure username or user-id you supplied is correct. "
                "If this issue persists, try using a different account as probably the current one has "
                "been flagged."
            )

    @staticmethod
    def is_username(identifier: str) -> bool:
        """
        Returns True if the given identifier is a Username, and False if it's a UserID.
        :param identifier: Username or UserID
        :return: Boolean
        """

        return False in tuple(x in string.digits for x in identifier)

    def direct(self) -> Direct:
        """
        Lets you use the direct messaging feature of Instagram
        :return: Direct() class with all the supported methods
        """

        return Direct(
            session=self.session,
            device_id=self.device_id
        )

    def follow(self, user_id: str) -> bool:
        """
        Follows a user by user_id
        :param self: None
        :param user_id: UserID of target user
        :return: Boolean (Followed or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/friendships/create/{user_id}/",
            data="SIGNATURE." + json.dumps(
                {
                    "user_id": user_id,
                    "radio_type": "wifi-none",
                    "device_id": self.device_id,
                    "_uuid": str(uuid4()),
                    "container_module": "profile"
                }
            )
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to follow. Is the user_id correct? Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def unfollow(self, user_id: str) -> bool:
        """
        Unfollows a user by user_id
        :param self: None
        :param user_id: UserID of target user
        :return: Boolean (Unfollowed or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/friendships/destroy/{user_id}/",
            data="SIGNATURE." + json.dumps(
                {
                    "user_id": user_id,
                    "radio_type": "wifi-none",
                    "device_id": self.device_id,
                    "_uuid": str(uuid4()),
                    "container_module": "profile"
                }
            )
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to follow. Is the user_id correct? Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def block(self, user_id: str) -> bool:
        """
        Blocks a user by user_id
        :param self: None
        :param user_id: UserID of target user
        :return: Boolean (Blocked or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/friendships/block/{user_id}/",
            data="SIGNATURE." + json.dumps(
                {
                    "surface": "profile",
                    "is_auto_block_enabled": True,
                    "user_id": user_id,
                    "_uid": self.user_id,
                    "_uuid": str(uuid4()),
                    "container_module": "profile"
                }
            )
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to block. Is the user_id correct? Username should not be used. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def unblock(self, user_id: str) -> bool:
        """
        Unblocks a user by user_id
        :param self: None
        :param user_id: UserID of target user
        :return: Boolean (Unblocked or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/friendships/unblock/{user_id}/",
            data="SIGNATURE." + json.dumps(
                {
                    "user_id": user_id,
                    "_uid": self.user_id,
                    "_uuid": str(uuid4()),
                    "container_module": "search_typeahead"
                }
            )
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to unblock. Is the user_id correct? Username should not be used. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def upload_story(
            self,
            upload_id: str,
            resolution: tuple[int, int] = (1080, 1920),
            entities: list[StoryLink] = None
    ) -> bool:
        """
        Uploads media to story
        :param upload_id: Returned by get_upload_id(media_path)
        :param resolution: Resolution (Width, Height) of device canvas
        :param entities: Entities like stickers, links etc.
        :return: Boolean (Uploaded or not)
        """

        date = datetime.datetime.now()

        data: dict = {
            "supported_capabilities_new": "[{\"name\":\"SUPPORTED_SDK_VERSIONS\",\"value\":\"131.0,132.0,133.0,134.0,135.0,136.0,137.0,138.0,139.0,140.0,141.0,142.0,143.0,144.0,145.0,146.0,147.0,148.0,149.0,150.0,151.0,152.0,153.0,154.0,155.0,156.0,157.0,158.0,159.0\"},{\"name\":\"FACE_TRACKER_VERSION\",\"value\":\"14\"},{\"name\":\"COMPRESSION\",\"value\":\"ETC2_COMPRESSION\"},{\"name\":\"gyroscope\",\"value\":\"gyroscope_enabled\"}]",
            "has_original_sound": "1",
            "camera_entry_point": "12",
            "original_media_type": "1",
            "camera_session_id": str(uuid4()),
            "date_time_digitalized": f"{date.year}:{date.month:02}:{date.day:02} {date.hour:02}:{date.minute:02}:{date.second:02}",
            "camera_model": "sdk_gphone64_x86_64",
            "scene_capture_type": "",
            "timezone_offset": (datetime.datetime.fromtimestamp(date.timestamp() * 1e-3) - datetime.datetime.utcfromtimestamp(date.timestamp() * 1e-3)).seconds,
            "client_shared_at": int(date.timestamp()),
            "story_sticker_ids": "link_sticker_default",
            "configure_mode": "1",
            "source_type": "3",
            "camera_position": "front",
            "_uid": self.user_id,
            "device_id": self.device_id,
            "composition_id": str(uuid4()),
            "_uuid": self.phone_id,
            "creation_surface": "camera",
            "can_play_spotify_audio": "1",
            "date_time_original": f"{date.year}:{date.month:02}:{date.day:02} {date.hour:02}:{date.minute:02}:{date.second:02}",
            "capture_type": "normal",
            "upload_id": upload_id,
            "client_timestamp": int(date.timestamp()),
            "private_mention_sharing_enabled": "1",
            "media_transformation_info": f"{{\"width\":\"{resolution[0]}\",\"height\":\"{resolution[1]}\",\"x_transform\":\"0\",\"y_transform\":\"0\",\"zoom\":\"1.0\",\"rotation\":\"0.0\",\"background_coverage\":\"0.0\"}}",
            "camera_make": "Google",
            "device": {
                "manufacturer": "Google",
                "model": "sdk_gphone64_x86_64",
                "android_version": 31,
                "android_release": "12"
            },
            "edits": {
                "filter_type": 0,
                "filter_strength": 1.0,
                "crop_original_size": [
                    float(resolution[0]),
                    float(resolution[1])
                ]
            },
            "extra": {
                "source_width": resolution[0],
                "source_height": resolution[1]
            }
        }

        tap_models: list[dict] = []

        if entities is not None:
            for entity in entities:

                # A Story Link?
                if isinstance(entity, StoryLink):
                    tap_models.append(
                        {
                            "x": entity.x,
                            "y": entity.y,
                            "z": entity.z,
                            "width": entity.width,
                            "height": entity.height,
                            "rotation": entity.rotation,
                            "type": entity.type,
                            "link_type": entity.link_type,
                            "custom_cta": entity.title if entity.title != "" else entity.url,
                            "url": entity.url,
                            "is_sticker": entity.is_sticker,
                            "tap_state": entity.tap_state,
                            "tap_state_str_id": entity.tap_state_str_id,
                        }
                    )

        if len(tap_models) > 0: data["tap_models"] = tap_models

        response: Response = self.session.post(
            url="https://i.instagram.com/api/v1/media/configure_to_story/",
            data={"signed_body": "SIGNATURE." + json.dumps(data)}
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Failed to publish story. Is your media correct? Are all entities correct? "
                "Maybe you're being rate limited, try using a different account."
            )
