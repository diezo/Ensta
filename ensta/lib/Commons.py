import random
import string


def refresh_csrf_token(self) -> None:
    self.csrf_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))


def format_username(username: str) -> str:
    return username.replace(" ", "").lower()


def format_uid(uid: str) -> str:
    return uid.replace(" ", "")


def format_identifier(identifier: str | int) -> str:
    return str(identifier).lower().replace(" ", "")


def format_url(url: str) -> str:
    return url.strip()
