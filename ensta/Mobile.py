from requests import Session, Response
from .Credentials import Credentials
from .lib.Exceptions import AuthenticationError, FileTypeError, NetworkError
from uuid import uuid4
from json import  JSONDecodeError
from pathlib import Path
import time
import random
import string
import json
from .parser.ProfileParser import parse_profile
from .structures import Profile


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
        identifier: str,
        password: str,
        proxy: dict[str, str] = None,
        save_file: str = "ensta-mobile-session.txt",
        skip_authorization: bool = False,
        logging: bool = False
    ) -> None:

        self.session = Session()

        if proxy: self.session.proxies.update(proxy)

        self.refresh_credentials(
            cycle=1,
            identifier=identifier,
            password=password,
            save_file=save_file,
            logging=logging,
            skip_authorization=skip_authorization
        )

    def refresh_credentials(
        self,
        cycle: int,
        identifier: str,
        password: str,
        save_file: str,
        logging: bool,
        skip_authorization: bool
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
            save_file=save_file,
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
        if not skip_authorization:
            if not self.authorize():
                self.refresh_credentials(
                    cycle=cycle + 1,
                    identifier=identifier,
                    password=password,
                    save_file=save_file,
                    logging=logging,
                    skip_authorization=skip_authorization
                )

    def authorize(self) -> bool:
        return self.session.post(self.authorization_url).status_code == 400

    def get_upload_id(self, media_path: str, arg_upload_id: str | None = None) -> str:  # Web API
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

        upload_id = arg_upload_id if arg_upload_id is not None else str(int(time.time()) * 1000)
        upload_name = f"{upload_id}_0_{random.randint(1000000000, 9999999999)}"

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

    def profile(
        self,
        identifier: str
    ) -> Profile:
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
