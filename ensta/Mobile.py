from requests import Session, Response
from .Credentials import Credentials
from .lib.Exceptions import AuthenticationError, FileTypeError, NetworkError
from uuid import uuid4
from json import JSONDecodeError
import time
from pathlib import Path
import string
import datetime
import json
from .parser.ProfileParser import parse_profile
from .parser.FollowersParser import parse_followers
from .parser.FollowingsParser import parse_followings
from .parser.AddedCommentParser import parse_added_comment
from .parser.UploadedPhotoParser import parse_uploaded_photo
from .parser.UploadedSidecarParser import parse_uploaded_sidecar
from .parser.PrivateInfoParser import parse_private_info
from .structures import (
    Profile, StoryLink, Followers, Followings, AddedComment, UploadedPhoto, SidecarChild, UploadedSidecar,
    BioLink, PrivateInfo
)
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
        totp_token: str = None,
        session_data: str = None
    ) -> None:
        """
        This classes uses Instagram's Mobile API. Authentication is required using username and password.
        :param identifier: Account's Username or Email (For Login)
        :param password: Account's Password (For Login)
        :param proxy: (Optional) 'Requests' library compatible proxy dictionary.
        :param save_folder: Directory where login sessions should be stored. Pass "" to disable storing sessions.
        :param skip_auth_check: When 'True', checks whether the stored session is still valid. If no session is stored, it doesn't skip login.
        :param logging: Enables logging for debugging.
        :param totp_token: (Optional) Secret Token if TOTP-based 2FA is enabled on your account. Secret token looks like "823JAJID992JKD9JKJ", it's not the temporary code generated every 30 seconds by your Authenticator app.
        :param session_data: (Optional) Session Data string to be used instead of the saved session inside 'ensta-sessions' directory. Useful when persistent storage isn't allowed on your device.
        """

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

    def follow(self, identifier: str) -> bool:
        """
        Follows a user
        :param identifier: Username or UserID of target (UserID Recommended)
        :return: Boolean (Followed or not)
        """

        user_id: str = self.profile(identifier).user_id

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

    def unfollow(self, identifier: str) -> bool:
        """
        Unfollows a user by user_id
        :param identifier: Username or UserID of target (UserID Recommended)
        :return: Boolean (Unfollowed or not)
        """

        user_id: str = self.profile(identifier).user_id

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

    def block(self, identifier: str) -> bool:
        """
        Blocks a user
        :param identifier: Username or UserID of target (UserID Recommended)
        :return: Boolean (Blocked or not)
        """

        user_id: str = self.profile(identifier).user_id

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

    def unblock(self, identifier: str) -> bool:
        """
        Unblocks a user
        :param identifier: Username or UserID of target (UserID Recommended)
        :return: Boolean (Unblocked or not)
        """

        user_id: str = self.profile(identifier).user_id

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

    def change_biography(self, text: str) -> bool:
        """
        Sets a new biography to your account
        :param text: New biography
        :return: Boolean (Updated or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/accounts/set_biography/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "device_id": self.device_id,
                        "_uuid": str(uuid4()),
                        "raw_text": text
                    }
                )
            }
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to change biography. Make sure the new biography doesn't contain any "
                "illegal words not characters that are not permitted. Maybe try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def switch_to_public_account(self) -> bool:
        """
        Switches your account type to 'public'. Anyone one view your profile.
        :return: Boolean (Switched or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/accounts/set_public/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4())
                    }
                )
            }
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to switch to public. Maybe you've switched account privacy too many times. "
                "Maybe try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def switch_to_private_account(self) -> bool:
        """
        Switches your account type to 'private'. Only your followers can view your profile.
        :return: Boolean (Switched or not)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/accounts/set_private/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4())
                    }
                )
            }
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to switch to private. Maybe you've switched account privacy too many times. "
                "Maybe try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def username_to_userid(self, username: str) -> str:
        """
        Converts username to user_id.
        :param: username: Target username
        :return: user_id
        """

        return self.profile(username).user_id

    def userid_to_username(self, user_id: str) -> str:
        """
        Converts user_id to username.
        :param: user_id: Target user_id
        :return: username
        """

        return self.profile(user_id).username

    def like(self, media_id: str) -> bool:
        """
        Likes a post or reel
        :param: media_id: Media ID of post or reel
        :return: True/False
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/media/{media_id}/like/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4()),
                        "delivery_class": "organic",
                        "tap_source": "double_tap_media",
                        "media_id": media_id,
                        "source_of_like": "double_tap_media",
                        "carousel_index": "0",
                        "radio_type": "wifi-none",
                        "normalized_position_x": "0.5124817",
                        "normalized_position_y": "0.6305241",
                        "is_carousel_bumped_post": "false",
                        "container_module": "feed_contextual_profile",
                        "feed_position": "0"
                    }
                ),
                "d": "1"
            }
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to like media. Maybe try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def unlike(self, media_id: str) -> bool:
        """
        Unlikes a post or reel
        :param: media_id: Media ID of post or reel
        :return: True/False
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/media/{media_id}/unlike/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4()),
                        "delivery_class": "organic",
                        "tap_source": "button",
                        "media_id": media_id,
                        "carousel_index": "0",
                        "radio_type": "wifi-none",
                        "is_carousel_bumped_post": "false",
                        "container_module": "feed_contextual_profile",
                        "feed_position": "0"
                    }
                ),
                "d": "0"
            }
        )

        try: return response.json().get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError(
                "Unable to unlike media. Maybe try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def followers(self, identifier: str, next_cursor: str | int | None = None) -> Followers:
        """
        Get followers list of an account
        :param: identifier: Username or UserID (UserID Recommended)
        :return: Followers Object
        """

        next_cursor: str = str(next_cursor) if next_cursor is not None else None
        user_id: str = self.profile(identifier).user_id
        max_id_line: str = f"&max_id={next_cursor}" if next_cursor is not None else ""

        response: Response = self.session.get(
            url=f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?enable_groups=true{max_id_line}"
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Response status was not ok.\n"
                    f"Response Dict: {response_dict}"
                )

            return parse_followers(response_dict)

        except JSONDecodeError:
            raise NetworkError(
                "Unable to get followers list. Make sure either the account is public or you're "
                "already following the target user. Also, make sure the user hasn't blocked or "
                "restricted you. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def followings(self, identifier: str, next_cursor: str | int | None = None) -> Followings:
        """
        Get followings list of an account
        :param: identifier: Username or UserID (UserID Recommended)
        :return: Followings Object
        """

        next_cursor: str = str(next_cursor) if next_cursor is not None else None
        user_id: str = self.profile(identifier).user_id
        max_id_line: str = f"&max_id={next_cursor}" if next_cursor is not None else ""

        response: Response = self.session.get(
            url=f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?enable_groups=true"
                f"&includes_hashtags=true{max_id_line}"
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Response status was not ok.\n"
                    f"Response Dict: {response_dict}"
                )

            return parse_followings(response_dict)

        except JSONDecodeError:
            raise NetworkError(
                "Unable to get followings list. Make sure either the account is public or you're "
                "already following the target user. Also, make sure the user hasn't blocked or "
                "restricted you. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def comment(self, text: str, media_id: str) -> AddedComment:
        """
        Comment on a post or reel.
        :param: media_id: Media ID of post or reel
        :param: text: Comment text
        :return: True/False
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/media/{media_id}/comment/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4()),
                        "comment_text": text
                    }
                )
            }
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Couldn't add comment.\n"
                    f"Response JSON: {response_dict}"
                )

            return parse_added_comment(response_dict)

        except JSONDecodeError:
            raise NetworkError(
                "Unable to add comment. Maybe your comment contains offensive words. "
                "If not, try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def upload_photo(self, upload_id: str, caption: str = "", alt_text: str = "", location_id: str = "") -> UploadedPhoto:
        """
        Uploads a single photo post.
        :param upload_id: Returned by get_upload_id(image_path)
        :param caption: Caption text
        :param alt_text: Custom Accessibility Caption Text
        :param location_id: Facebook place ID of location
        :return: Uploaded Photo's Information
        """

        body: dict = {
            "_uid": self.user_id,
            "device_id": self.device_id,
            "_uuid": str(uuid4()),
            "custom_accessibility_caption": alt_text,
            "source_type": "4",
            "caption": caption,
            "upload_id": upload_id
        }

        # Add Location ID
        if location_id != "": body["location"] = f"{{\"facebook_places_id\":\"{location_id}\"}}"

        # Hit Endpoint
        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/media/configure/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(body)
            }
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":

                if f"NodeInvalidTypeException: Node backed by fbid {location_id}" in response_dict.get("message", ""):
                    raise NetworkError(
                        f"Location ID {location_id} doesn't exist on facebook places."
                    )

                raise NetworkError(
                    "Unable to upload photo.\n"
                    f"Response: {response_dict}"
                )

            return parse_uploaded_photo(response_dict.get("media", {}))

        except JSONDecodeError:
            raise NetworkError(
                "Unable to upload photo. Is the upload_id correct? Are all other configurations "
                "correct? Are you using a valid image? Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def upload_sidecar(self, children: list[SidecarChild], caption: str = "", location_id: str = "") -> UploadedSidecar:
        """
        Uploads a sidecar post (multiple photos in a single post).
        :param children: Each photo's information (SidecarChild Object)
        :param caption: Caption text
        :param location_id: Facebook place ID of location
        :return: Uploaded Sidecar's Information
        """

        body: dict = {
            "_uid": self.user_id,
            "device_id": self.device_id,
            "_uuid": str(uuid4()),
            "client_sidecar_id": str(int(time.time() * 1000)),
            "source_type": "4",
            "caption": caption,
            "children_metadata": [
                {
                    "upload_id": child.upload_id,
                    "source_type": "4",
                    "custom_accessibility_caption": child.alt_text,
                } for child in children
            ]
        }

        # Add Location ID
        if location_id != "": body["location"] = f"{{\"facebook_places_id\":\"{location_id}\"}}"

        # Hit Endpoint
        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/media/configure_sidecar/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(body)
            }
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":

                if f"NodeInvalidTypeException: Node backed by fbid {location_id}" in response_dict.get("message", ""):
                    raise NetworkError(
                        f"Location ID {location_id} doesn't exist on facebook places."
                    )

                raise NetworkError(
                    "Unable to upload sidecar.\n"
                    f"Response: {response_dict}"
                )

            return parse_uploaded_sidecar(response_dict)

        except JSONDecodeError:
            raise NetworkError(
                "Unable to upload sidecar. Are the upload_id's correct? Are all other configurations "
                "correct? Are you using valid images? Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def add_bio_links(self, bio_links: list[BioLink]) -> list[int]:
        """
        Adds new external links to your bio.
        :param bio_links: List of InputBioLink Objects
        :return: List of Link IDs (Integers)
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/accounts/update_bio_links/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4()),
                        "updated_links": [
                            {
                                "url": link.url,
                                "title": link.title,
                                "link_type": "external"
                            } for link in bio_links
                        ]
                    }
                )
            }
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Bio link(s) not removed.\n"
                    f"Response: {response_dict}"
                )

            try: return [
                link.get("link_id", 0) for link in response_dict.get("user", {}).get("bio_links", [])[-len(bio_links):]
            ]
            except IndexError: return []

        except JSONDecodeError:
            raise NetworkError(
                "Unable to add bio link(s). Maybe you're not allowed to add "
                "bio links to your profile. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def add_bio_link(self, url: str, title: str = "") -> int:
        """
        Adds a single external link to your bio.
        :param url: Link URL
        :param title: Optional Link Title
        :return: Link ID (Integer)
        """

        return self.add_bio_links([BioLink(url=url, title=title)])[0]

    def remove_bio_links(self, link_ids: list[int]) -> bool:
        """
        Removes existing external links from your bio.
        :param link_ids: List of Link IDs to remove
        :return: Boolean
        """

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/accounts/remove_bio_links/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "_uid": self.user_id,
                        "_uuid": str(uuid4()),
                        "link_ids": link_ids
                    }
                )
            }
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Bio link(s) not removed.\n"
                    f"Response: {response_dict}"
                )

            return True

        except JSONDecodeError:
            raise NetworkError(
                "Unable to remove bio link(s). Maybe you're not allowed to remove "
                "bio links from your profile. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def remove_bio_link(self, link_id: int) -> bool:
        """
        Removes an existing external link from your bio.
        :param link_id: Link ID
        :return: Boolean
        """

        return self.remove_bio_links([link_id])

    def clear_bio_links(self) -> bool:
        """
        Removes all external links from your bio.
        :return: Boolean
        """

        return self.remove_bio_links([link.link_id for link in self.profile(self.username).bio_links])

    def private_info(self) -> PrivateInfo:
        """
        Get your account's private information.
        :return: PrivateInfo Object
        """

        response: Response = self.session.get(f"https://i.instagram.com/api/v1/accounts/current_user/?edit=true")

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Couldn't fetch private info.\n"
                    f"Response: {response_dict}"
                )

            return parse_private_info(response_dict.get("user", {}))

        except JSONDecodeError:
            raise NetworkError(
                "Unable to fetch private info. Are you logged in? Try using another account, switch "
                "to a different network, or use reputed proxies."
            )

    def update_display_name(self, display_name: str) -> bool:
        """
        Updates your profile's display name.
        :param display_name: New display name
        :return: Boolean
        """

        private_info: PrivateInfo = self.private_info()

        response: Response = self.session.post(
            url=f"https://i.instagram.com/api/v1/accounts/edit_profile/",
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "primary_profile_link_type": "PrimaryProfileLinkType_unspecified",
                        "phone_number": private_info.phone_number,
                        "username": private_info.username,
                        "show_fb_link_on_profile": private_info.show_fb_link_on_profile,
                        "first_name": display_name,
                        "_uid": self.user_id,
                        "device_id": self.device_id,
                        "biography": private_info.biography,
                        "_uuid": str(uuid4()),
                        "email": private_info.email
                    }
                )
            }
        )

        try:
            response_dict: dict = response.json()

            if response_dict.get("status", "") != "ok":
                raise NetworkError(
                    "Display name not updated.\n"
                    f"Response: {response_dict}"
                )

            return True

        except JSONDecodeError:
            raise NetworkError(
                "Unable to update display name. Maybe you've already reached the "
                "weekly limit to update your display name. Try using another account, switch "
                "to a different network, or use reputed proxies."
            )
