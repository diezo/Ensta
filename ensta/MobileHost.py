from requests import Session, Response
from .Credentials import Credentials
from .lib.Exceptions import AuthenticationError
from uuid import uuid4
from json import  JSONDecodeError


class MobileHost:

    session: Session
    credentials: Credentials

    bearer: str
    user_id: str
    username: str
    phone_id: str
    device_id: str
    identifier: str

    credentials_refresh_max_cycle: int = 3

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

        self.setup_headers()

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

    def authorize(self) -> bool:  # TODO: Implement

        return True

        response: Response = self.session.post(
            url="https://i.instagram.com/api/v1/wwwgraphql/ig/query/"
        )

        return response.status_code == 200

    def setup_headers(self) -> None:

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

    def change_profile_picture(self, upload_id: str) -> bool:
        """
        Changes your profile picture to a new one.
        :param upload_id: Returned by get_upload_id() method
        :return: Boolean (Successfully changed or not)
        """

        headers: dict = {
            "accept-encoding": "gzip",
            "accept-language": "en-US",
            "connection": "Keep-Alive",
            "content-length": "115",  # TODO: May not work
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

            print(response.json())

            return response.json().get("status", "") == "ok"

        except JSONDecodeError: return False
