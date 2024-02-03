from base64 import b64encode
from uuid import uuid4
from requests import Session


class Mobile:

    user_id: str
    mobile_session_id: str
    session: Session

    user_agent: str = "Instagram 317.0.0.24.109 Android (31/12; 640dpi; 1440x3056; " \
                      "OnePlus; GM1911; OnePlus7Pro; qcom; en_US; 562739837)"

    def __init__(self, user_id: str, mobile_session_id: str, proxy: dict | None = None) -> None:
        self.user_id, self.mobile_session_id = user_id, mobile_session_id
        self.session = Session()

        if proxy is not None: self.session.proxies.update(proxy)

    @property
    def basic_headers(self) -> dict:

        b64_encoded: bytes = b64encode(
            f"{{\"ds_user_id\":\"{self.user_id}\",\"sessionid\":\"{self.mobile_session_id}\"}}".encode("utf-8")
        )

        bearer_token: str = f"IGT:2:{b64_encoded.decode('utf-8')}"

        return {
            "authorization": f"Bearer {bearer_token}",
            "host": "i.instagram.com",
            "ig-intended-user-id": self.user_id,
            "ig-u-ds-user-id": self.user_id,
            "user-agent": self.user_agent,
            "x-ig-device-id": str(uuid4()),
            "x-ig-device-locale": "en_US",
            "x-ig-family-device-id": str(uuid4()),
            "x-fb-connection-type": "WIFI",
            "x-fb-http-engine": "Tigon-TCP-Fallback",
            "x-ig-android-id": "android-d105ec84a512642c",
        }
