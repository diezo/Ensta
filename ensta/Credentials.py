import json
from json import JSONDecodeError
from requests import Session, Response
import os
from uuid import uuid4
from .PasswordEncryption import PasswordEncryption
from .lib.Exceptions import AuthenticationError


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
            save_file: str,
            logging: bool = False
    ) -> None:

        self.session = session
        self.user_agent = user_agent

        # Existing Stored Credentials?
        stored_dict: dict = self.fetch_stored_dict(save_file)
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
            self.login(identifier, password, save_file)

    @staticmethod
    def fetch_stored_dict(save_file: str) -> dict:
        """
        Reads the stored session file content and returns its JSON.
        :param save_file: File Path
        :return: JSON Content or None
        """

        # File Doesn't Exist
        if not os.path.exists(save_file) or not os.path.isfile(save_file): return dict()

        # Read File Content
        with open(save_file, "r") as file:
            content: str = file.read().strip()

        # Is Content A Valid JSON?
        try: return json.loads(content)

        # File Content Not A Valid JSON
        except JSONDecodeError: return dict()


    def login(self, identifier: str, password: str, save_file: str) -> None:
        """
        Takes identifier and password, authenticates, stores new session in file, and returns a bunch of session data.
        :param identifier: Username or Email
        :param password: Password
        :param save_file: File path to store new session in. Empty to skip storing session.
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
            # Parse Response Body Into A JSON
            response_dict: dict = response.json()

            # Request Failed
            if response_dict.get("status", "fail") != "ok":

                raise AuthenticationError(
                    f"Login failed with given credentials.\nError: \"{response_dict.get('error_title', 'unknown')}\"\n"
                    f"Message: \"{response_dict.get('message', 'unknown')}\""
                )

            # Request Succeeded: Collect Data
            user_info: dict = response_dict.get("logged_in_user", dict())

            self.bearer: str = response.headers.get("ig-set-authorization")
            self.user_id: str = str(user_info.get("pk"))
            self.username: str = user_info.get("username")
            self.phone_id = phone_id
            self.stored_identifier = identifier

            # Save Session in File
            if save_file != "":
                with open(save_file, "w") as file:
                    file.write(
                        json.dumps({
                            "bearer": self.bearer,
                            "user_id": self.user_id,
                            "username": self.username,
                            "identifier": identifier,
                            "phone_id": phone_id,
                            "device_id": self.device_id
                        })
                    )

        # Response Body Not A Valid JSON
        except JSONDecodeError:
            raise AuthenticationError(
                "Response I got didn't parse into a JSON. Maybe you're being rate "
                "limited. Change WiFi or use reputed proxies."
            )
