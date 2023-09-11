import random
import string
import requests
import requests.cookies
from .Exceptions import NetworkError


def update_app_id(self) -> None:
    app_id_occurrence_string = "\"APP_ID\":\""
    app_id_first_occurrence = self.homepage_source.index(app_id_occurrence_string)
    app_id_raw_text = self.homepage_source[
                      app_id_first_occurrence + len(app_id_occurrence_string): app_id_first_occurrence + 30]
    self.insta_app_id = app_id_raw_text[: app_id_raw_text.index("\"")]


def refresh_csrf_token(self) -> None:
    self.csrf_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    self.request_session.cookies.set("csrftoken", self.csrf_token)


def update_session(self) -> None:
    self.request_session = requests.Session()


def update_homepage_source(self) -> None:
    request_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-prefers-color-scheme": random.choice(["light", "dark"]),
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
        "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.110\", \"Google Chrome\";v=\"114.0.5735.110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua-platform-version": "\"15.0.0\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "viewport-width": "1475",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    temp_homepage_source = requests.get("https://www.instagram.com/", headers=request_headers).text.strip()

    if temp_homepage_source != "":
        self.homepage_source = temp_homepage_source
    else:
        raise NetworkError("Couldn't load instagram homepage.")


def format_username(username: str) -> str:
    return username.replace(" ", "").lower()


def format_uid(uid: str) -> str:
    return uid.replace(" ", "")


def format_identifier(identifier: str | int) -> str:
    return str(identifier).lower().replace(" ", "")


def format_url(url: str) -> str:
    return url.strip()
