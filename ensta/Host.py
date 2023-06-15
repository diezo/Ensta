import requests
from json import JSONDecodeError
import random
import string
from collections.abc import Generator
from .Guest import Guest
from .lib.Commons import (
    refresh_csrf_token,
    update_app_id,
    update_homepage_source,
    update_session,
    format_identifier
)
from .lib import (
    SessionError,
    NetworkError,
    IdentifierError,
    DevelopmentError,
    APIError
)
from .containers import (FollowedStatus, UnfollowedStatus, FollowPerson)
from .containers.ProfileHost import ProfileHost

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
            app_id=self.insta_app_id
        )

        self.request_session.cookies.set("sessionid", session_id)

        if not self.authenticated():
            raise SessionError("SessionID is incorrect or expired.")

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

    def followers(self, identifier: str | int, count: int = 0) -> Generator[FollowPerson, None, None]:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success:
            yield None
            return None

        # Actual Request
        refresh_csrf_token(self)
        request_headers: dict = {
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
            "Referer": f"https://www.instagram.com/{''.join(random.choices(string.ascii_lowercase, k=6))}/followers/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        current_max_id: str = ""
        generated_count: int = 0

        while True:
            current_max_id_text: str = ""

            if current_max_id != "":
                current_max_id_text: str = f"&max_id={current_max_id}"

            try:
                count_text = 35

                if count < 35:
                    count_text = count

                http_response = self.request_session.get(f"https://www.instagram.com/api/v1/friendships/{identifier}/followers/?count={str(count_text)}{current_max_id_text}&search_surface=follow_list_page", headers=request_headers)
                response_json = http_response.json()

                if "status" not in response_json or "users" not in response_json:
                    yield None
                    return None

                if response_json["status"] != "ok":
                    yield None
                    return None

                for each_item in response_json["users"]:
                    if generated_count < count or count == 0:

                        try:
                            yield FollowPerson(
                                has_anonymous_profile_picture=each_item["has_anonymous_profile_picture"],
                                user_id=each_item["pk"],
                                username=each_item["username"],
                                full_name=each_item["full_name"],
                                is_private=each_item["is_private"],
                                is_verified=each_item["is_verified"],
                                profile_picture_url=each_item["profile_pic_url"],
                                badges=each_item["account_badges"],
                                third_party_downloads_enabled=each_item["third_party_downloads_enabled"],
                                is_possible_scammer=each_item["is_possible_scammer"]
                            )

                        except KeyError:
                            raise APIError()

                        generated_count += 1

                if (generated_count < count or count == 0) and "next_max_id" in response_json:
                    current_max_id = response_json["next_max_id"]
                else:
                    return None
            except JSONDecodeError:
                yield None
                return None

    def followings(self, identifier: str | int, count: int = 0) -> Generator[FollowPerson, None, None]:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success:
            yield None
            return None

        # Actual Request
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
            "Referer": f"https://www.instagram.com/{''.join(random.choices(string.ascii_lowercase, k=6))}/following/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        current_max_id = ""
        generated_count = 0

        while True:
            current_max_id_text = ""

            if current_max_id != "":
                current_max_id_text = f"&max_id={current_max_id}"

            try:
                count_text = 35

                if count < 35:
                    count_text = count

                http_response = self.request_session.get(
                    f"https://www.instagram.com/api/v1/friendships/{identifier}/following/?count={str(count_text)}{current_max_id_text}",
                    headers=request_headers)
                response_json = http_response.json()

                if "status" not in response_json or "users" not in response_json:
                    yield None
                    return None

                if response_json["status"] != "ok":
                    yield None
                    return None

                for each_item in response_json["users"]:
                    if generated_count < count or count == 0:

                        try:
                            yield FollowPerson(
                                has_anonymous_profile_picture=each_item["has_anonymous_profile_picture"],
                                user_id=each_item["pk"],
                                username=each_item["username"],
                                full_name=each_item["full_name"],
                                is_private=each_item["is_private"],
                                is_verified=each_item["is_verified"],
                                profile_picture_url=each_item["profile_pic_url"],
                                is_possible_scammer=each_item["is_possible_scammer"]
                            )

                        except KeyError:
                            raise APIError()

                        generated_count += 1

                if (generated_count < count or count == 0) and "next_max_id" in response_json:
                    current_max_id = response_json["next_max_id"]
                else:
                    return None
            except JSONDecodeError:
                yield None
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
            raise DevelopmentError("Identifier Conversion (Else Block)")

    def _set_account_privacy(self, privacy: str) -> bool:
        is_private = (privacy == "private")

        if privacy != "private" and privacy != "public":
            raise DevelopmentError("_set_account_privacy")

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

    def profile(self, username: str) -> ProfileHost | None:
        return self.guest.profile(username, __session__=self.request_session)

    def get_username(self, uid: str | int) -> str | None:
        return self.guest.get_username(uid, __session__=self.request_session)
