import json
import random
import string
import requests
from requests import Session
from requests import Response
from json import JSONDecodeError
from .PasswordEncryption import PasswordEncryption
from .lib.Exceptions import (AuthenticationError, NetworkError)


def new_session_id(username: str, password: str, proxy: dict[str, str] | None = None) -> str:
    request_session: Session = requests.Session()

    if proxy is not None: request_session.proxies.update(proxy)

    encryption = PasswordEncryption(request_session)
    encrypted_password = encryption.encrypt(password)

    data: dict = {
        "enc_password": encrypted_password,
        "optIntoOneTap": False,
        "queryParams": "{}",
        "trustedDeviceRecords": "{}",
        "username": username
    }

    csrf_token: str = "".join(random.choices(string.ascii_letters + string.digits, k=32))

    headers: dict = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "dpr": "1.30208",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/119.0.0.0 Safari/537.36",
        "sec-ch-ua-full-version-list": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                       "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": "\"\"",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua-platform-version": "\"15.0.0\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "viewport-width": "1475",
        "x-asbd-id": "129477",
        "x-csrftoken": csrf_token,
        "x-ig-app-id": "936619743392459",
        "x-ig-www-claim": "0",
        "x-instagram-ajax": "1009977574",
        "x-requested-with": "XMLHttpRequest",
        "x-web-device-id": "25532C62-8BBC-4927-B6C5-02631D6E05BF",
        "cookie": f"dpr=1.3020833730697632; csrftoken={csrf_token}",
        "Referer": "https://www.instagram.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    http_response: Response = request_session.post(
        "https://www.instagram.com/api/v1/web/accounts/login/ajax/",
        data=data,
        headers=headers
    )

    try:
        response_json: dict = http_response.json()

        if response_json.get("status", "") != "ok": raise AuthenticationError("User doesn't exist.")

        if response_json.get("user", False) is False or response_json.get("authenticated", False) is False:
            raise AuthenticationError("Invalid password.")

        session_id: str = http_response.cookies.get("sessionid", "")
        rur: str = http_response.cookies.get("rur", "")
        mid: str = http_response.cookies.get("mid", "")
        user_id: str = response_json.get("userId", "")
        ig_did: str = response_json.get("ig_did", "")

        if session_id == "" or user_id == "": raise AuthenticationError("Unable to login.")

        return json.dumps({
            "session_id": session_id,
            "rur": rur,
            "mid": mid,
            "user_id": user_id,
            "ig_did": ig_did,
            "username": username
        })

    except JSONDecodeError:
        raise NetworkError("Response got while logging in was not a valid "
                           "json. Are you able to visit Instagram on the web?")
