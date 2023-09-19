import requests
import random
import string
import json
from json import JSONDecodeError
from collections.abc import Generator
from .lib.Commons import (
    refresh_csrf_token,
    update_app_id,
    update_homepage_source,
    update_session,
    format_identifier,
    format_url,
    format_username
)
from .lib import (
    SessionError,
    NetworkError,
    IdentifierError,
    DevelopmentError,
    APIError,
    ConversionError
)
from .containers import (FollowedStatus, UnfollowedStatus, FollowPerson)
from .containers.ProfileHost import ProfileHost
from .containers.PostUser import PostUser
from .containers.Post import Post
from .Guest import Guest

USERNAME = 0
UID = 1


class BaseHost:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = None
    preferred_color_scheme: str = "dark"
    x_ig_www_claim: str = None
    csrf_token: str = None
    guest: Guest = None

    def __init__(self, session_id: str, proxy: dict[str, str] | None = None) -> None:
        self.x_ig_www_claim = "hmac." + "".join(random.choices(string.ascii_letters + string.digits + "_-", k=48))
        update_session(self)
        update_homepage_source(self)
        update_app_id(self)

        if proxy is not None: self.request_session.proxies.update(proxy)

        self.guest = Guest(
            homepage_source=self.homepage_source,
            app_id=self.insta_app_id
        )

        self.request_session.cookies.set("sessionid", session_id)

        if not self.authenticated():
            raise SessionError("SessionID is incorrect or expired.")

    def update_homepage_source(self) -> None:
        temp_homepage_source = self.request_session.get("https://www.instagram.com/").text.strip()

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
        if not conversion_success: raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

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
            raise NetworkError("HTTP Response is not a valid JSON.")

    def unfollow(self, identifier: str | int) -> UnfollowedStatus | None:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success: raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

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
            raise NetworkError("HTTP Response is not a valid JSON.")

    def followers(self, identifier: str | int, count: int = 0) -> Generator[FollowPerson, None, None]:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success:
            yield None
            raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

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
                    raise NetworkError("HTTP response doesn't include 'status' or 'users' node.")

                if response_json["status"] != "ok":
                    yield None
                    raise NetworkError("HTTP response status not 'ok'.")

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
                raise NetworkError("HTTP Response is not a valid JSON.")

    def followings(self, identifier: str | int, count: int = 0) -> Generator[FollowPerson, None, None]:
        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success:
            yield None
            raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

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
                    raise NetworkError("HTTP response doesn't include 'status' or 'users' node.")

                if response_json["status"] != "ok":
                    yield None
                    raise NetworkError("HTTP response status not 'ok'.")

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
                raise NetworkError("HTTP Response is not a valid JSON.")

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

    def posts(self, username: str, count: int = 0) -> Generator[Post, None, None]:
        username = format_username(username)

        refresh_csrf_token(self)
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.110\", \"Google Chrome\";v=\"114.0.5735.110\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{username}/",
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

                http_response = self.request_session.get(f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count_text}{current_max_id_text}", headers=request_headers)
                response_json = http_response.json()

                if "status" not in response_json or "items" not in response_json:
                    yield None
                    raise NetworkError("HTTP response doesn't include 'status' or 'items' node.")

                if response_json["status"] != "ok":
                    yield None
                    raise NetworkError("HTTP response status not 'ok'.")

                for each_item in response_json["items"]:
                    if generated_count < count or count == 0:

                        yield self._process_post_data(each_item)
                        generated_count += 1

                if (generated_count < count or count == 0) and "next_max_id" in response_json:
                    current_max_id = response_json["next_max_id"]
                else:
                    return None
            except JSONDecodeError:
                yield None
                raise NetworkError("HTTP Response is not a valid JSON.")

    def post(self, share_url: str) -> Post | None:
        share_url: str = format_url(share_url)
        request_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.110\", \"Google Chrome\";v=\"114.0.5735.110\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "viewport-width": "1475",
            "referrerPolicy": "strict-origin-when-cross-origin"
        }

        http_response = self.request_session.get(share_url, headers=request_headers)
        response_text = http_response.text

        required_text = "{\"response\":\"{\\\"items\\\":"

        initial_index = response_text.rfind(required_text)
        if initial_index == -1: raise APIError()

        rest_text = response_text[initial_index - len(required_text) + len(required_text): len(response_text)]
        end_text = "\\\"auto_load_more_enabled\\\":false}\",\"status_code\":200}"
        end_index = rest_text.find(end_text)

        try:
            data: dict = json.loads(rest_text[:end_index + len(end_text)])

            if "response" in data:
                response_data: dict = json.loads(data["response"])

                if "items" in response_data:
                    items_data: list = response_data["items"]

                    if len(items_data) > 0:
                        selected_post: dict = items_data[len(items_data) - 1]

                        if selected_post is not None:
                            return self._process_post_data(selected_post)

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def _process_post_data(self, data: dict) -> Post:

        caption: dict = data.get("caption", None)

        caption_text = ""
        is_caption_covered = False
        caption_created_at = 0
        caption_share_enabled = False
        caption_did_report_as_spam = False

        if caption is not None:
            caption_text = caption.get("text", "")
            is_caption_covered = caption.get("is_covered", False)
            caption_created_at = caption.get("created_at", 0)
            caption_share_enabled = caption.get("share_enabled", False)
            caption_did_report_as_spam = caption.get("did_report_as_spam", False)

        user: PostUser = PostUser()
        user_data: dict = data.get("user", None)

        if user_data is not None:
            user: PostUser = PostUser(
                has_anonymous_profile_picture=user_data.get("has_anonymous_profile_picture", False),
                fbid_v2=user_data.get("fbid_v2", ""),
                transparency_product_enabled=user_data.get("transparency_product_enabled", False),
                is_favorite=user_data.get("is_favorite", False),
                is_unpublished=user_data.get("is_unpublished", False),
                uid=user_data.get("pk", ""),
                username=user_data.get("username", ""),
                full_name=user_data.get("full_name", ""),
                is_private=user_data.get("is_private", False),
                is_verified=user_data.get("is_verified", False),
                profile_picture_id=user_data.get("profile_pic_id", ""),
                profile_picture_url=user_data.get("profile_pic_url", ""),
                account_badges=user_data.get("account_badges", []),
                feed_post_reshare_disabled=user_data.get("feed_post_reshare_disabled", False),
                show_account_transparency_details=user_data.get("show_account_transparency_details", False),
                third_party_downloads_enabled=user_data.get("third_party_downloads_enabled", 0),
                latest_reel_media=user_data.get("latest_reel_media", 0)
            )

        return Post(
            instance=self,
            share_url=f"https://www.instagram.com/p/{data.get('code', '')}",
            taken_at=data.get("taken_at", 0),
            unique_key=data.get("pk", ""),
            media_type=data.get("media_type", 0),
            code=data.get("code", ""),
            caption_is_edited=data.get("caption_is_edited", False),
            original_media_has_visual_reply_media=data.get("original_media_has_visual_reply_media", False),
            like_and_view_counts_disabled=data.get("like_and_view_counts_disabled", False),
            can_viewer_save=data.get("can_viewer_save", False),
            profile_grid_control_enabled=data.get("profile_grid_control_enabled", False),
            is_comments_gif_composer_enabled=data.get("is_comments_gif_composer_enabled", False),
            comment_threading_enabled=data.get("comment_threading_enabled", False),
            comment_count=data.get("comment_count", 0),
            has_liked=data.get("has_liked", False),
            user=user,
            can_viewer_reshare=data.get("can_viewer_reshare", False),
            like_count=data.get("like_count", 0),
            top_likers=data.get("top_likers", []),
            caption_text=caption_text,
            is_caption_covered=is_caption_covered,
            caption_created_at=caption_created_at,
            caption_share_enabled=caption_share_enabled,
            caption_did_report_as_spam=caption_did_report_as_spam,
            is_paid_partnership=data.get("is_paid_partnership", False),
            show_shop_entrypoint=data.get("show_shop_entrypoint", False),
            deleted_reason=data.get("deleted_reason", 0),
            integrity_review_decision=data.get("integrity_review_decision", ""),
            ig_media_sharing_disabled=data.get("ig_media_sharing_disabled", False),
            has_shared_to_fb=data.get("has_shared_to_fb", False),
            is_unified_video=data.get("is_unified_video", False),
            should_request_ads=data.get("should_request_ads", False),
            is_visual_reply_commenter_notice_enabled=data.get("is_visual_reply_commenter_notice_enabled", False),
            commerciality_status=data.get("commerciality_status", ""),
            explore_hide_comments=data.get("explore_hide_comments", False),
            has_delayed_metadata=data.get("has_delayed_metadata", False),
            location_latitude=data.get("lat", 0),
            location_longitude=data.get("lng", 0)
        )
