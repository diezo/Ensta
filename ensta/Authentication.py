import json
import random
import string
import requests
import pyotp
import ntplib
from requests import Session
from requests import Response
from json import JSONDecodeError
from .PasswordEncryption import PasswordEncryption
from .lib.Exceptions import (AuthenticationError, NetworkError)
from .WebSession import WebSession


def new_session_id(
    user_identifier: str,  # Username or Email
    password: str,
    proxy: dict[str, str],
    totp_token: str = None
) -> str:
    
    request_session: Session = requests.Session()
    request_session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                                            "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    if proxy is not None: request_session.proxies.update(proxy)

    encryption = PasswordEncryption(request_session)
    encrypted_password = encryption.encrypt(password)

    data: dict = {
        "enc_password": encrypted_password,
        "optIntoOneTap": False,
        "queryParams": "{}",
        "trustedDeviceRecords": "{}",
        "username": user_identifier  # Accepts email as well
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
        url="https://www.instagram.com/api/v1/web/accounts/login/ajax/",
        data=data,
        headers=headers
    )

    try:
        response_json: dict = http_response.json()

        if response_json.get("status", "") != "ok":

            verification_code: int | None = None

            if response_json.get("two_factor_required", False) is True:
            
                if response_json.get("two_factor_info", {}).get("totp_two_factor_on", False) is False:

                    if response_json.get("two_factor_info", {}).get("sms_two_factor_on", False) is False:

                        raise AuthenticationError(
                            "Some other 2FA method is enabled. Only TOTP-based"
                            " (Authenticator App) and SMS-based two factor is supported."
                        )

                    verification_code: int = int(input("SMS 2FA enabled. Enter OTP: "))
    
                if totp_token is None and verification_code is None:
                    raise AuthenticationError("Two-factor is enabled. Please provide the totp_token while logging in.")

                else:
                    tf_data: dict = {
                        "queryParams": '{"next":"/"}',
                        "trust_signal": True,
                        "identifier": response_json.get("two_factor_info", {}).get("two_factor_identifier"),
                        "verification_method": "1",
                        "username": user_identifier,
                        "verificationCode": verification_code if verification_code is not None else

                        pyotp.TOTP(totp_token).at(
                            int(
                                ntplib.NTPClient().request(
                                    "time.google.com",
                                    version=3
                                ).tx_time
                            )
                        )
                    }

                    tf_response: Response = request_session.post(
                        url="https://www.instagram.com/api/v1/web/accounts/login/ajax/two_factor/",
                        data=tf_data,
                        headers={
                            "sec-ch-prefers-color-scheme": "dark",
                            "sec-ch-ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                                         "Chrome/119.0.0.0 Safari/537.36",
                            "sec-ch-ua-full-version-list": "Mozilla/5.0 (Windows NT 10.0; Win64;"
                                                           " x64) AppleWebKit/537.36 "
                                                           "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-model": "\"\"",
                            "sec-ch-ua-platform": "\"Windows\"",
                            "sec-ch-ua-platform-version": "\"15.0.0\"",
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-origin",
                            'Accept': '*/*',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'X-Mid': response_json.get("two_factor_info", {}).get("device_id"),
                            'X-CSRFToken': csrf_token,
                            "x-instagram-ajax": "1009977574",
                            "x-ig-app-id": "936619743392459",
                            'X-ASBD-ID': '129477',
                            'X-IG-WWW-Claim': '0',
                            "x-web-device-id": "25532C62-8BBC-4927-B6C5-02631D6E05BF",
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Origin': 'https://www.instagram.com',
                            'DNT': '1',
                            'Sec-GPC': '1',
                            'Connection': 'keep-alive',
                            'Referer': 'https://www.instagram.com/accounts/login/two_factor?next=%2F',
                            'Sec-Fetch-Dest': 'empty',
                            'Sec-Fetch-Mode': 'cors',
                            'Sec-Fetch-Site': 'same-origin',
                        },
                        cookies={
                            "ig_did": response_json.get("ig_did", ""),
                            "mid": response_json.get("two_factor_info", {}).get("device_id"),
                            "csrftoken": csrf_token
                        }
                    )
                     
                    if "Oops, an error occurred." in tf_response.text:

                        raise AuthenticationError(
                            "IP temporarily banned most probably due to too many login requests."
                            " Please try again later or use proxies."
                        )
                    
                    try:
                        tf_response_json: dict = tf_response.json()
                    
                        if tf_response_json.get("status", "") != "ok" \
                                or tf_response_json.get("authenticated", False) is False:

                            raise AuthenticationError(
                                "Couldn't log in through 2FA. Most probably your totp_token is incorrect."
                            )
                        
                        session_id: str = tf_response.cookies.get("sessionid", "")
                        rur: str = tf_response.cookies.get("rur", "")
                        mid: str = response_json.get("two_factor_info", {}).get("device_id")
                        user_id: str = tf_response_json.get("userId", "")
                        ig_did: str = tf_response.cookies.get("ig_did", "")
    
                        if session_id == "" or user_id == "":

                            raise AuthenticationError(
                                "2FA authentication response didn't return a valid session_id or user_id."
                            )

                        return json.dumps({
                            "session_id": session_id,
                            "rur": rur,
                            "mid": mid,
                            "user_id": user_id,
                            "ig_did": ig_did,
                            "identifier": user_identifier,
                            "username": WebSession(
                                json.dumps({
                                    "session_id": session_id,
                                    "rur": rur,
                                    "mid": mid,
                                    "user_id": user_id,
                                    "ig_did": ig_did,
                                })
                            ).private_info().username
                        })

                    except JSONDecodeError:
                        raise NetworkError(
                            "Response got while logging in was not a valid "
                            "json. Are you able to visit Instagram on the web?"
                        )
            
            raise AuthenticationError(
                "Either user doesn't exist or your password is too weak (change it to a stronger one)."
            )

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
            "identifier": user_identifier,
            "username": WebSession(
                json.dumps({
                    "session_id": session_id,
                    "rur": rur,
                    "mid": mid,
                    "user_id": user_id,
                    "ig_did": ig_did,
                })
            ).private_info().username
        })

    except JSONDecodeError:
        raise NetworkError("Response got while logging in was not a valid "
                           "json. Are you able to visit Instagram on the web?")
