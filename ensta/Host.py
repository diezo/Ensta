import requests
from json import JSONDecodeError
import random
import string
from .Guest import Guest
from .lib.Commons import (
    refresh_csrf_token,
    update_app_id,
    update_homepage_source,
    update_session,
    format_identifier
)
from .lib import (
    AuthenticationError,
    NetworkError,
    IdentifierError,
    CodeError
)
from .containers import (FollowedStatus, UnfollowedStatus)
from .containers.Profile import Profile

USERNAME = 0
UID = 1


class Host:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = None
    preferred_color_scheme: str = "dark"
    x_ig_www_claim: str = None
    csrf_token: str = None
    guest: Guest = None

    def __init__(self, session_id: str) -> None:
        self.x_ig_www_claim = "hmac." + "".join(random.choices(string.ascii_letters + string.digits + "_-", k=48))
        update_session(self)
        update_homepage_source(self)
        update_app_id(self)
        self.guest = Guest(
            homepage_source=self.homepage_source,
            insta_app_id=self.insta_app_id
        )

        self.request_session.cookies.set("sessionid", session_id)

        if not self.authenticated():
            raise AuthenticationError("Either User ID or Session ID is not valid.")

    def update_homepage_source(self) -> None:
        temp_homepage_source = requests.get("https://www.instagram.com/").text.strip()

        if temp_homepage_source == "":
            raise NetworkError("Couldn't load instagram homepage.")

        self.homepage_source = temp_homepage_source

    def authenticated(self) -> bool:
        refresh_csrf_token(self)
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.91\", \"Google Chrome\";v=\"114.0.5735.91\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "198387",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/edit/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        http_response = self.request_session.get("https://www.instagram.com/api/v1/accounts/edit/web_form_data/", headers=request_headers)

        try:
            http_response.json()
            return True
        except JSONDecodeError:
            return False

    def follow(self, identifier: str | int) -> FollowedStatus | None:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success: return None

        # Actual Request
        refresh_csrf_token(self)
        body_json = {
            "container_module": "profile",
            "nav_chain": f"PolarisProfileRoot:profilePage:1:via_cold_start",
            "user_id": identifier
        }
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.91\", \"Google Chrome\";v=\"114.0.5735.91\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "198387",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-instagram-ajax": "1007616494",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{''.join(random.choices(string.ascii_lowercase, k=5))}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.post(f"https://www.instagram.com/api/v1/friendships/create/{identifier}/", headers=request_headers, data=body_json)
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"] \
                            and "followed_by" in response_json["friendship_status"] \
                            and "previous_following" in response_json:
                        return FollowedStatus(
                            following=response_json["friendship_status"]["following"],
                            follow_requested=response_json["friendship_status"]["outgoing_request"],
                            is_my_follower=response_json["friendship_status"]["followed_by"],
                            previous_following=response_json["previous_following"]
                        )
        except JSONDecodeError:
            return None

    def unfollow(self, identifier: str | int) -> UnfollowedStatus | None:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success: return None

        # Actual Request
        refresh_csrf_token(self)
        body_json = {
            "container_module": "profile",
            "nav_chain": f"PolarisProfileRoot:profilePage:1:via_cold_start",
            "user_id": identifier
        }
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.91\", \"Google Chrome\";v=\"114.0.5735.91\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "198387",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-instagram-ajax": "1007616494",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{''.join(random.choices(string.ascii_lowercase, k=6))}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.post(f"https://www.instagram.com/api/v1/friendships/destroy/{identifier}/", headers=request_headers, data=body_json)
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"] \
                            and "followed_by" in response_json["friendship_status"]:
                        return UnfollowedStatus(
                            unfollowed=not response_json["friendship_status"]["following"] and not response_json["friendship_status"]["outgoing_request"],
                            is_my_follower=response_json["friendship_status"]["followed_by"]
                        )
        except JSONDecodeError:
            return None

    def _identifier(self, identifier: str | int, required: str | int):
        identifier = format_identifier(identifier)

        if len(identifier) <= 0:
            raise IdentifierError("No identifier was given. Please pass either UserId or Username as an argument.")

        # Identifier: Username or UID?
        is_username = False
        for letter in identifier:
            if letter not in string.digits:
                is_username = True
                break

        if is_username and required == USERNAME:
            return True, identifier

        elif is_username and required == UID:
            user_id = self.guest.get_uid(identifier)

            if user_id is not None and user_id != "":
                return True, user_id
            else:
                return False, None

        elif not is_username and required == USERNAME:
            username = self.guest.get_username(identifier)

            if username is not None and username != "":
                return True, username
            else:
                return False, None

        elif not is_username and required == UID:
            return True, identifier

        else:
            raise CodeError("Identifier Conversion (Else Block)")

    def _set_account_privacy(self, privacy: str) -> bool:
        is_private = (privacy == "private")

        if privacy != "private" and privacy != "public":
            raise CodeError("_set_account_privacy")

        refresh_csrf_token(self)
        body_json = {
            "is_private": is_private
        }
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.91\", \"Google Chrome\";v=\"114.0.5735.91\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "198387",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-instagram-ajax": "1007616494",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/who_can_see_your_content/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.post("https://www.instagram.com/api/v1/web/accounts/set_private/", headers=request_headers, data=body_json)
            response_json = http_response.json()

            if "status" not in response_json:
                return False

            if response_json["status"] != "ok":
                return False

            return True
        except JSONDecodeError:
            return False

    def switch_to_private_account(self) -> bool:
        return self._set_account_privacy("private")

    def switch_to_public_account(self) -> bool:
        return self._set_account_privacy("public")

    def profile(self, username: str) -> Profile | None:
        return self.guest.profile(username, self.request_session)
