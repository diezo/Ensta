import json
from json import JSONDecodeError
from requests import Session, Response
from uuid import uuid4
from .PasswordEncryption import PasswordEncryption
from .lib.Exceptions import AuthenticationError
from requests.models import CaseInsensitiveDict
from .SessionManager import SessionManager
import pyotp
import ntplib


class Credentials:
    """
    Takes identifier-password and returns Credentials.

    - Should be called with identifier and password.
    - If stored session exists, validates it (not authenticates), and returns Credentials.
    - Otherwise logs in using given identifier and password, stores it in file, and returns Credentials.
    - Raises appropriate exceptions where needed.
    """

    session: Session
    user_agent: str
    totp_token: str

    bearer: str
    user_id: str
    username: str
    phone_id: str
    stored_identifier: str

    device_id: str = "android-d105ec84a512642c"

    def __init__(
        self,
        identifier: str,
        password: str,
        user_agent: str,
        session: Session,
        save_folder: str,
        totp_token: str,
        session_data: str,
        logging: bool = False
    ) -> None:

        self.session = session
        self.user_agent = user_agent
        self.totp_token = totp_token

        # Existing Stored Credentials?
        if session_data is not None: stored_dict: dict = json.loads(session_data)
        else: stored_dict: dict = SessionManager.load_from_file(identifier, password, save_folder)

        stored_dict_valid: bool = True

        # Validate StoredDict
        for key in ("bearer", "user_id", "username", "phone_id", "identifier", "device_id"):
            if key not in stored_dict.keys(): stored_dict_valid: bool = False

        # Load From StoredDict
        if stored_dict_valid and stored_dict.get("identifier") == identifier:
            if logging: print("Loading from stored file...")
            self.bearer = stored_dict.get("bearer")
            self.user_id = stored_dict.get("user_id")
            self.username= stored_dict.get("username")
            self.phone_id = stored_dict.get("phone_id")
            self.stored_identifier = stored_dict.get("identifier")

        # Create New Session
        else:
            if logging: print("Creating new session...")
            self.login(identifier, password, save_folder)


    def login(self, identifier: str, password: str, save_folder: str) -> None:
        """
        Takes identifier and password, authenticates, stores new session in file, and returns a bunch of session data.
        :param identifier: Username or Email
        :param password: Password
        :param save_folder: Folder path to store new session in. Empty to skip storing session.
        :return: Tuple of session data
        """

        phone_id: str = str(uuid4())
        guid: str = str(uuid4())
        encrypted_password = PasswordEncryption(self.session).encrypt(password)

        response: Response = self.session.post(
            url="https://i.instagram.com/api/v1/accounts/login/",
            headers={
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "user-agent": self.user_agent,
                "host": "i.instagram.com",
            },
            data={
                "jazoest": "22506",
                "country_codes": "[{\"country_code\":\"1\",\"source\":[\"default\"]}]",
                "phone_id": phone_id,
                "enc_password": encrypted_password,
                "username": identifier,
                "adid": "00000000-0000-0000-0000-000000000000",
                "guid": guid,
                "device_id": self.device_id,
                "google_tokens": "[]",
                "login_attempt_count": "0"
            }
        )

        try:
            user_info: dict | None = None
            response_headers: CaseInsensitiveDict[str] | None = None

            # Parse Response Body Into A JSON
            response_dict: dict = response.json()

            # Request Failed
            if response_dict.get("status", "fail") != "ok":

                # Other Than 2FA?
                if response_dict.get("error_type", "") != "two_factor_required":
                    raise AuthenticationError(
                        f"Login failed with given credentials.\n"
                        f"Response: {response_dict}"
                    )

                # 2FA Required
                user_info, response_headers = self.handle_2fa(
                    information=response_dict.get("two_factor_info", {}),
                    phone_id=phone_id,
                    guid=guid
                )

            # Request Succeeded: Collect Data
            if user_info is None: user_info: dict = response_dict.get("logged_in_user", dict())

            if response_headers is None: self.bearer: str = response.headers.get("ig-set-authorization")
            else: self.bearer: str = response_headers.get("ig-set-authorization")

            self.user_id: str = str(user_info.get("pk"))
            self.phone_id = phone_id
            self.username: str = user_info.get("username")
            self.stored_identifier = identifier

            # Save Session in File
            if save_folder != "":
                SessionManager.save_to_file(
                    folder_name=save_folder,
                    identifier=identifier,
                    password=password,
                    phone_id=phone_id,
                    instance=self
                )

        # Response Body Not A Valid JSON
        except JSONDecodeError:
            raise AuthenticationError(
                "Response I got didn't parse into a JSON. Maybe you're being rate "
                "limited. Change WiFi or use reputed proxies."
            )

    def handle_2fa(
        self,
        information: dict,
        phone_id: str,
        guid: str
    ) -> tuple[dict, CaseInsensitiveDict[str]]:

        # Only TOTP Supported: No SMS, No WhatsApp
        if information.get("totp_two_factor_on", False) is False:
            raise AuthenticationError(
                "Only TOTP-based 2FA is supported till now."
            )

        # TODO: Remove when implemented
        raise NotImplementedError("TOTP 2FA not implemented yet!")

        # TOTP Token Supplied? Take Input | Use That
        if self.totp_token is None: code: str = input("Enter TOTP Code: ")
        else: code: str = self.new_totp_code(self.totp_token)

        while True:
            user_info, response_headers = self.bypass_totp(
                code=code,
                two_factor_identifier=information.get("two_factor_identifier"),
                phone_id=phone_id,
                guid=guid
            )

            if user_info is not None and response_headers is not None: break

            if self.totp_token is None:
                code: str = input(
                    "Unable to verify code.\n\n"
                    "Enter TOTP Code: "
                )

            else:
                raise AuthenticationError(
                    "Unable to verify TOTP 2FA Code. Is the totp_token correct?"
                )

        return user_info, response_headers

    @staticmethod
    def new_totp_code(token: str) -> str:
        """
        Generates a new TOTP Code for the current time using secret token.

        :param token: TOTP Token generated by Instagram stored secretly in the Authenticator App.
        :return: Generated Code
        """

        current_time: int = int(ntplib.NTPClient().request("time.google.com", version=3).tx_time)

        return str(
            pyotp.TOTP(token).at(current_time)
        )

    def bypass_totp(self, code: str, two_factor_identifier: str, phone_id: str, guid: str) -> tuple[dict, CaseInsensitiveDict[str]]:

        response: Response = self.session.post(
            url="https://i.instagram.com/api/v1/accounts/two_factor_login/",
            headers={
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "accept-encoding": "gzip",
                "connection": "Keep-Alive"
            },
            data={
                "signed_body": "SIGNATURE." + json.dumps(
                    {
                        "verification_code": code,
                        "phone_id": phone_id,
                        "two_factor_identifier": two_factor_identifier,
                        "trust_this_device": "1",
                        "guid": guid,
                        "device_id": self.device_id,
                        "waterfall_id": str(uuid4()),
                        "verification_method": "3"  # '3' For TOTP-Based 2FA
                    }
                )
            }
        )

        # TODO
        """
        Return logged_in_user_info and response headers.
        Error: CSRF Token missing or incorrect.
        """

        raise Exception(response.json())
