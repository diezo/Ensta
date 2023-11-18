import random
import string
import requests
import requests.cookies
from requests.cookies import RequestsCookieJar


def refresh_csrf_token(self) -> None:
    self.csrf_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))

    cookie_jar: RequestsCookieJar = self.request_session.cookies
    cookies = list(cookie_jar.items())
    cookie_jar.clear()
    final_cookies = {}

    for key, value in cookies:
        final_cookies[key] = value

    final_cookies["csrftoken"] = self.csrf_token

    for key in final_cookies:
        cookie_jar.set(key, final_cookies[key])


def format_username(username: str) -> str:
    return username.replace(" ", "").lower()


def format_uid(uid: str) -> str:
    return uid.replace(" ", "")


def format_identifier(identifier: str | int) -> str:
    return str(identifier).lower().replace(" ", "")


def format_url(url: str) -> str:
    return url.strip()
