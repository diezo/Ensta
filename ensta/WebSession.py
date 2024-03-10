import mimetypes
import tempfile
from functools import partial, partialmethod
import json
import random
import string
import requests
import moviepy.editor
from uuid import uuid4
from .Guest import Guest
from pathlib import Path
from json import JSONDecodeError
from .containers.Liker import Liker
from .containers.Likers import Likers
from .containers.Post import Post
from collections.abc import Generator
from .containers.ProfileHost import ProfileHost
from .containers.PrivateInfo import PrivateInfo
from .containers.PostDetail import PostDetail
from .containers import (FollowedStatus, UnfollowedStatus, FollowPerson, PhotoUpload, ReelUpload)
from .lib import (
    SessionError,
    NetworkError,
    IdentifierError,
    DevelopmentError,
    APIError,
    ConversionError
)
from PIL import Image
from ensta.lib.Searcher import create_search_obj, search_comments
from urllib.parse import urlparse, parse_qs
from .Utils import time_id, fb_uploader
from pyquery import PyQuery

USERNAME, UID = 0, 1


IMAGE_RUPLOAD_PARAMS = {
    "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
    "media_type": "1",
    "image_compression": json.dumps({"lib_name": "moz", "lib_version": "3.1.m", "quality": 80})
}

REEL_RUPLOAD_PARAMS = {
    "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
    "is_clips_video": "1",
    "media_type": "2",
}

CAROUSEL_VIDEO_RUPLOAD_PARAMS = {
    "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
    "is_unified_video": "0",
    "is_clips_video": "0",
    "is_sidecar": "1",
    "media_type": "2",
}


class WebSession:

    session_data: str
    request_session: requests.Session
    insta_app_id: str = "936619743392459"
    preferred_color_scheme: str = "dark"
    x_ig_www_claim: str
    csrf_token: str
    guest: Guest
    user_id: str
    username: str
    identifier: str
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                      "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    private_user_agent: str = "Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x1920; " \
                              "OnePlus; 6T Dev; devitron; qcom; en_US; 314665256)"

    def __init__(
        self,
        session_data: str,
        proxy: dict[str, str] = None,
        skip_auth_verification: bool = False
    ) -> None:

        self.session_data = session_data
        self.x_ig_www_claim = "hmac." + "".join(random.choices(string.ascii_letters + string.digits + "_-", k=48))
        self.csrf_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        self.request_session = requests.Session()
        self.request_session.headers["user-agent"] = self.user_agent

        if proxy is not None: self.request_session.proxies.update(proxy)

        session_data_json: dict = json.loads(session_data)

        self.guest = Guest(proxy=proxy)

        self.user_id = session_data_json.get("user_id")
        self.username = session_data_json.get("username")
        self.identifier = session_data_json.get("identifier")

        self.request_session.cookies.set("sessionid", session_data_json.get("session_id"))
        self.request_session.cookies.set("rur", session_data_json.get("rur"))
        self.request_session.cookies.set("mid", session_data_json.get("mid"))
        self.request_session.cookies.set("ds_user_id", session_data_json.get("user_id"))
        self.request_session.cookies.set("ig_did", session_data_json.get("ig_did"))
        self.request_session.cookies.set("csrftoken", self.csrf_token)

        if not skip_auth_verification and not self.authenticated():
            raise SessionError(
                "SessionID expired. If you used a saved session, delete ensta-session.txt file and try again"
            )

    def authenticated(self) -> bool:
        """
        Returns whether user is logged in or not.
        That is, if the provided username-password combination or session-id is correct.
        :return: Boolean (True / False)
        """

        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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
        http_response = self.request_session.get(
            "https://www.instagram.com/api/v1/accounts/edit/web_form_data/",
            headers=request_headers
        )

        try:
            http_response.json()
            return True
        except JSONDecodeError:
            return False

    def follow(self, identifier: str | int) -> FollowedStatus | None:
        """
        Follows the target user.
        :param identifier: Target user's Username or UserID
        :return: Object with the followed info
        """

        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success: raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

        # Actual Request
        body_json = {
            "container_module": "profile",
            "nav_chain": f"PolarisProfileNestedContentRoot:profilePage:1:via_cold_start",
            "user_id": identifier
        }
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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
            http_response = self.request_session.post(
                f"https://www.instagram.com/api/v1/friendships/create/{identifier}/",
                headers=request_headers,
                data=body_json
            )
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
                else:
                    if response_json["status"] != "ok":
                        if response_json.get("spam", False):
                            raise NetworkError(
                                "Spam Detected: Your actions are being limited by Instagram. Please slow down."
                            )
                        
                        raise NetworkError("Response \"Status\" not ok.")
                    
                    raise NetworkError("'friendship_status' attribute not in response json.")
            else:
                raise NetworkError("'status' attribute not in response json.")
        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def unfollow(self, identifier: str | int) -> UnfollowedStatus | None:
        """
        Unfollows the target user.
        :param identifier: Target user's Username or UserID
        :return: Object with the unfollowed info
        """

        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success: raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

        # Actual Request
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
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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
            http_response = self.request_session.post(
                f"https://www.instagram.com/api/v1/friendships/destroy/{identifier}/",
                headers=request_headers,
                data=body_json
            )
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"] \
                            and "followed_by" in response_json["friendship_status"]:

                        return UnfollowedStatus(
                            unfollowed=not (
                                    response_json["friendship_status"]["following"] or
                                    response_json["friendship_status"]["outgoing_request"]
                            ),

                            is_my_follower=response_json["friendship_status"]["followed_by"]
                        )
                else:
                    if response_json["status"] != "ok": raise NetworkError("Response \"Status\" not ok.")
                    else: raise NetworkError("'friendship_status' attribute not in response json.")
            else:
                raise NetworkError("'status' attribute not in response json.")
        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def followers(self, identifier: str | int, count: int = 0) -> Generator[FollowPerson, None, None]:
        """
        Generates a list of target's followers of specified size.

        :param identifier: Target's Username or UserID
        :param count: Amount of followers to fetch
        :return: Generator which yields each user's details
        """

        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success:
            yield None
            raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

        # Actual Request
        request_headers: dict = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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

                http_response = self.request_session.get(
                    f"https://www.instagram.com/api/v1/friendships/{identifier}/followers/?count={str(count_text)}"
                    f"{current_max_id_text}&search_surface=follow_list_page",
                    headers=request_headers
                )
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
                                third_party_downloads_enabled=each_item["third_party_downloads_enabled"]
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
        """
        Generates a list of users which the target follows, of specified size.
        :param identifier: Target's Username or UserID
        :param count: Amount of followings to fetch
        :return: Generator which yields each user's details
        """

        conversion_success, identifier = self._identifier(identifier, UID)
        if not conversion_success:
            yield None
            raise ConversionError(f"Can't convert identifier \"{identifier}\" into 'UID'.")

        # Actual Request
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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
                    f"https://www.instagram.com/api/v1/friendships/{identifier}/following/?count={str(count_text)}"
                    f"{current_max_id_text}",
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
                                profile_picture_url=each_item["profile_pic_url"]
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
        identifier = str(identifier).lower().replace(" ", "")

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
            user_id = self.get_uid(identifier)

            if user_id is not None and user_id != "":
                return True, user_id
            else:
                return False, None

        elif not is_username and required == USERNAME:
            username = self.get_username(identifier)

            if username is not None and username != "":
                return True, username
            else:
                return False, None

        elif not is_username and required == UID:
            return True, identifier

        else:
            raise DevelopmentError()

    def _set_account_privacy(self, privacy: str) -> bool:
        is_private = (privacy == "private")

        if privacy != "private" and privacy != "public":
            raise DevelopmentError()

        body_json = {
            "is_private": is_private
        }
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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
            http_response = self.request_session.post(
                "https://www.instagram.com/api/v1/web/accounts/set_private/",
                headers=request_headers,
                data=body_json
            )
            response_json = http_response.json()

            if "status" not in response_json:
                return False

            if response_json["status"] != "ok":
                return False

            return True
        except JSONDecodeError:
            return False

    def switch_to_private_account(self) -> bool:
        """
        Switches your account type to 'Private'. This means, only your followers can see your posts, stories & highlights.
        :return: Boolean (Whether your account type was successfully switched to private)
        """

        return self._set_account_privacy("private")

    def switch_to_public_account(self) -> bool:
        """
        Switches your account type to 'Public'. This means, anyone can see your posts, stories & highlights.
        :return: Boolean (Whether your account type was successfully switched to public)
        """

        return self._set_account_privacy("public")

    def profile(self, username: str) -> ProfileHost | None:
        """
        Returns profile data of the target user. Including name, profile picture, follower_count, following_count, etc.
        :param username: Username of the target
        :return: Profile object which contains all the data
        """

        return self.guest.profile(username, __session__=self.request_session)

    def get_username(self, uid: str | int) -> str | None:
        """
        Returns the username of the target user, when given their userid.
        :param uid: Target's UserID
        :return: Target's Username
        """

        return self.guest.get_username(uid, __session__=self.request_session)

    def get_uid(self, username: str) -> str | None:
        """
        Returns the userid of the target user, when given their username.
        :param username: Target's Username
        :return: Target's UserID
        """

        return self.guest.get_uid(username, __session__=self.request_session)

    def posts(self, username: str, count: int = 0) -> Generator[Post, None, None]:
        """
        Generates a list of target's posts of specified size.
        :param username: Target's Username
        :param count: Amount of posts to fetch
        :return: Generator which yields each post's data
        """

        return self.guest.posts(username, count, __session__=self.request_session)

    def get_raw_post(self, share_url: str) -> str:
        share_url: str = share_url.strip()

        request_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif"
                      ",image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
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
        return http_response.text

    def post(self, share_url: str) -> PostDetail:
        """
        Get single post data from URL.
        :param share_url: URL of target post
        :return: PostDetail Object
        """

        parsed_url = urlparse(share_url)
        code = parsed_url.path.removeprefix('/p/').removesuffix('/')
        response_text = self.get_raw_post(share_url)
        doc = PyQuery(response_text)
        url = urlparse(doc('meta[property="al:ios:url"]').attr('content'))
        pk = parse_qs(url.query)['id'][0]
        search_post = create_search_obj(code=code, pk=pk)
        post = {}
        comments = []
        for json_script in doc('script[type="application/json"]'):
            try:
                json_data = json.loads(json_script.text)
            except Exception as ex:
                continue
            comments.extend(search_comments(json_data))
            for p in search_post(json_data):
                post.update(p)
        post['comments'] = comments
        return PostDetail.from_data(post)

    def get_post_id(self, share_url: str) -> str:
        """
        Returns post_id of specific post, given its share_url, which can further be used to like or add comment to that post.
        :param share_url: Share URL of post. e.g. - https://www.instagram.com/p/Czr2yLmroCQ/
        :return: PostID in text format
        """

        response_text = self.get_raw_post(share_url)

        required_text = "instagram://images?id="

        initial_index = response_text.find(required_text)
        if initial_index == -1: raise APIError()

        rest_text = response_text[initial_index + len(required_text): initial_index + len(required_text) + 25]

        end_index = rest_text.find('"')
        if end_index == -1: raise APIError()

        return rest_text[:end_index]

    def private_info(self) -> PrivateInfo:
        """
        Returns your own (logged-in user's) private info which only you can access. Such as gender, birthday, email, phone number, etc.
        :return: Object which contains your private info
        """

        request_headers = {
            "accept": "*/*",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/edit/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        http_response = self.request_session.get(
            f"https://www.instagram.com/api/v1/accounts/edit/web_form_data/",
            headers=request_headers
        )

        try:
            response_json: dict = http_response.json()

            if "status" not in response_json: raise NetworkError("Key 'status' not in response json.")
            if response_json.get("status") != "ok": raise NetworkError("Key 'status' not 'ok' in response json.")

            data: json = response_json.get("form_data", {})
            if len(data.keys()) == 0: raise NetworkError("Form data doesn't contain any keys.")

            return PrivateInfo(
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                email=data.get("email", ""),
                is_email_confirmed=data.get("is_email_confirmed", False),
                is_phone_confirmed=data.get("is_phone_confirmed", False),
                username=data.get("username", ""),
                phone_number=data.get("phone_number", ""),
                gender=("f" if data.get("gender", 0) == 0 else "m"),
                birthday=data.get("birthday", ""),
                fb_birthday=data.get("fb_birthday", ""),
                biography=data.get("biography", ""),
                external_url=data.get("external_url", ""),
                chaining_enabled=data.get("chaining_enabled", False),
                presence_disabled=data.get("presence_disabled", False),
                business_account=data.get("business_account", False),
                user_tag_review_enabled=data.get("usertag_review_enabled", False),
                custom_gender=data.get("custom_gender", ""),
                trusted_username=data.get("trusted_username", ""),
                trust_days=data.get("trust_days", 0)
            )

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def change_bio(self, biography: str) -> bool:
        """
        Updates your (logged-in user's) biography to the newly given text.
        :param biography: New Biography
        :return: Boolean (Whether your biography was successfully updated or not)
        """

        private_info = self.private_info()

        request_headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-instagram-ajax": "1009841815",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/edit/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json = {
            "biography": biography,
            "chaining_enabled": "on" if private_info.chaining_enabled else "off",
            "email": private_info.email,
            "external_url": private_info.external_url,
            "first_name": private_info.first_name,
            "phone_number": private_info.phone_number,
            "username": private_info.username
        }

        http_response = self.request_session.post(
            f"https://www.instagram.com/api/v1/web/accounts/edit/",
            headers=request_headers,
            data=body_json
        )

        try:
            response_json: dict = http_response.json()

            if "status" not in response_json: raise NetworkError(
                "Key 'status' not in response json. Possibly it's a fault from your side."
            )
            return response_json.get("status") == "ok"

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def change_display_name(self, display_name: str) -> bool:
        """
        Updates your (logged-in user's) display name on Instagram.
        :param display_name: New name
        :return: Boolean (Whether your name was successfully updated or not)
        """

        private_info = self.private_info()

        request_headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-instagram-ajax": "1009841815",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/edit/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json = {
            "biography": private_info.biography,
            "chaining_enabled": "on" if private_info.chaining_enabled else "off",
            "email": private_info.email,
            "external_url": private_info.external_url,
            "first_name": display_name,
            "phone_number": private_info.phone_number,
            "username": private_info.username
        }

        http_response = self.request_session.post(
            f"https://www.instagram.com/api/v1/web/accounts/edit/",
            headers=request_headers,
            data=body_json
        )

        try:
            response_json: dict = http_response.json()

            if "status" not in response_json: raise NetworkError(
                "Key 'status' not in response json. Possibly it's a fault from your side."
            )

            return response_json.get("status") == "ok"

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def _upload_image(self, media: str, upload_id: str | None = None, **kwargs) -> str:
        """
        https://i.instagram.com/rupload_igphoto/
        """
        rupload_params = dict(kwargs)
        media_path: Path = Path(media)
        mimetype, _ = mimetypes.guess_type(media_path)
        upload_id = upload_id or time_id()
        waterfall_id = str(uuid4())
        upload_name = fb_uploader(upload_id)
        rupload_params.update(**{
            "upload_id": upload_id,
            "xsharing_user_ids": json.dumps([self.user_id]),
        })

        with open(media_path, "rb") as file:
            image_data = file.read()
            image_length = str(len(image_data))

        request_headers = {
            "accept-encoding": "gzip",
            "x-instagram-rupload-params": json.dumps(rupload_params),
            "x_fb_photo_waterfall_id": waterfall_id,
            "x-entity-type": mimetype,
            "offset": "0",
            "x-entity-name": upload_name,
            "x-entity-length": image_length,
            "content-type": mimetype,
            "content-length": image_length
        }

        http_response = self.request_session.post(
            f"https://i.instagram.com/rupload_igphoto/{upload_name}",
            data=image_data,
            headers=request_headers
        )

        try:
            response_json: dict = http_response.json()

            if response_json.get("status", "") != "ok":
                raise NetworkError("Response json key 'status' not ok.")
            if response_json.get("upload_id", "") == "":
                raise NetworkError(
                    "Key 'upload_id' in response json doesn't exist or is invalid."
                )

            return str(response_json.get("upload_id"))

        except JSONDecodeError:
            raise NetworkError("Response not a valid json.")

    def _upload_video(self, media: str, upload_id: str | None = None, thumbnail=0, **kwargs) -> str:
        """
        https://i.instagram.com/rupload_igvideo/
        video requires and image as thumbnail
        """
        assert thumbnail != None
        rupload_params = dict(kwargs)
        media_path: Path = Path(media)
        mimetype, _ = mimetypes.guess_type(media_path)
        video_editor = moviepy.editor.VideoFileClip(media)
        waterfall_id = str(uuid4())
        upload_id = upload_id or time_id()
        upload_name = fb_uploader(upload_id)

        rupload_params.update(**{
            "xsharing_user_ids": json.dumps([self.user_id]),
            "upload_id": upload_id,
            "upload_media_duration_ms": str(int(video_editor.duration * 1000)),
            "upload_media_width": str(video_editor.size[0]),
            "upload_media_height": str(video_editor.size[1]),
        })

        request_headers__get = {
            "accept-encoding": "gzip",
            "x-instagram-rupload-params": json.dumps(rupload_params),
            "x_fb_video_waterfall_id": waterfall_id,
            "x-entity-type": mimetype,
        }

        with open(media_path, "rb") as file:
            video_data = file.read()
            video_length = str(len(video_data))

        request_headers = {
            "offset": "0",
            "x-entity-name": upload_name,
            "x-entity-length": video_length,
            "content-type": mimetype,
            "content-length": video_length,
            **request_headers__get
        }

        http_response = self.request_session.post(
            f"https://i.instagram.com/rupload_igvideo/{upload_name}",
            data=video_data,
            headers=request_headers
        )
        response_json: dict = http_response.json()
        if response_json.get("status", "") != "ok":
            raise Exception()

        if isinstance(thumbnail, (int, float)):
            thumbnail_frame = video_editor.get_frame(thumbnail)
            with tempfile.NamedTemporaryFile(suffix='.jpg') as thumbnail_file:
                Image.fromarray(thumbnail_frame).save(thumbnail_file.name)
                return self.upload_image(media=thumbnail_file.name, upload_id=upload_id)
        return self.upload_image(media=thumbnail, upload_id=upload_id)

    def upload_media(self, media: str, upload_id: str | None = None, **kwargs) -> str:

        def unknown_type(*_, **__):
            raise Exception(f'Unknown type {media}')

        mimetype, _ = mimetypes.guess_type(media)
        type, _ = mimetype.split('/')
        methods = {
            'image': self._upload_image,
            'video': self._upload_video,
        }
        method = methods.get(type, unknown_type)
        return method(media, upload_id, **kwargs)

    upload_video_for_carousel = partialmethod(_upload_video, **CAROUSEL_VIDEO_RUPLOAD_PARAMS)
    upload_video_for_reel = partialmethod(_upload_video, **REEL_RUPLOAD_PARAMS)
    upload_image = partialmethod(_upload_image, **IMAGE_RUPLOAD_PARAMS)

    def pub_photo(
        self,
        upload_id: str,
        caption: str = "",
        alt_text: str = "",
        archive_only: bool = False,
        disable_comments: bool = False,
        like_and_view_counts_disabled: bool = False
    ) -> PhotoUpload:
        """
        Creates a single photo post on your account.
        :param upload_id: Upload ID of file already uploaded using get_upload_id() method
        :param caption: Optional caption text for current post
        :param alt_text: Optional custom accessibility caption for this photo
        :param archive_only: Boolean (Should this post be directly archived)
        :param disable_comments: Boolean (Should comments on this post be disabled)
        :param like_and_view_counts_disabled: Boolean (Shouldn't people be able to see how many users liked & viewed this post)
        :return: PostUpload
        """

        request_headers: dict = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
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
            "x-instagram-ajax": "1009848613",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json = {
            "archive_only": archive_only,
            "caption": caption,
            "clips_share_preview_to_feed": "1",
            "disable_comments": "1" if disable_comments else "0",
            "disable_oa_reuse": False,
            "igtv_share_preview_to_feed": "1",
            "is_meta_only_post": "0",
            "is_unified_video": "1",
            "like_and_view_counts_disabled": "1" if like_and_view_counts_disabled else "0",
            "source_type": "library",
            "upload_id": upload_id,
            "video_subtitles_enabled": "0"
        }

        if alt_text != "": body_json["custom_accessibility_caption"] = alt_text

        http_response = self.request_session.post(
            "https://www.instagram.com/api/v1/media/configure/",
            headers=request_headers,
            data=body_json
        )

        try:
            response_json: dict = http_response.json()
            return PhotoUpload.from_response_data(response_json)

        except JSONDecodeError:
            raise NetworkError("Response not a valid json.")

    def pub_carousel(
        self,
        upload_ids: list[str],
        caption: str = "",
        archive_only: bool = False,
        disable_comments: bool = False,
        like_and_view_counts_disabled: bool = False,
    ) -> bool:  # TODO: Implement Return Value
        """
        Creates a single post with multiple photos on your account.
        :param upload_ids: List (Upload IDs of files already uploaded using get_upload_id() method)
        :param caption: Optional caption text for current post
        :param archive_only: Boolean (Should this post be directly archived)
        :param disable_comments: Boolean (Should comments on this post be disabled)
        :param like_and_view_counts_disabled: Boolean (Shouldn't people be able to see how many users liked & viewed this post)
        :return: Boolean (Whether post was successfully created or not)
        """

        request_headers: dict = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
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
            "x-instagram-ajax": "1009848613",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json = {
            "archive_only": archive_only,
            "caption": caption,
            "children_metadata": [{"upload_id": upload_id} for upload_id in upload_ids],
            "client_sidecar_id": time_id(),
            "disable_comments": "1" if disable_comments else "0",
            "like_and_view_counts_disabled": "1" if like_and_view_counts_disabled else "0",
            "source_type": "library"
        }

        http_response = self.request_session.post(
            "https://www.instagram.com/api/v1/media/configure_sidecar/",
            headers=request_headers,
            data=json.dumps(body_json)
        )

        try:
            response_json: dict = http_response.json()

            return response_json.get("status", "") == "ok"

        except JSONDecodeError:
            raise NetworkError("Response not a valid json.")

    def pub_reel(
        self,
        upload_id: str,
        caption: str = "",
        alt_text: str = "",
        archive_only: bool = False,
        disable_comments: bool = False,
        like_and_view_counts_disabled: bool = False,
        video_subtitles_enabled: bool = False
    ) -> ReelUpload:
        """
        Uploads a reel on your account.
        :param video_path: Path of the video file
        :param thumbnail_path: Path of the image to be used as the thumbnail of current reel
        :param caption: Optional caption text for current reel
        :param alt_text: Optional custom accessibility caption for this reel
        :param archive_only: Boolean (Should this reel be directly archived)
        :param disable_comments: Boolean (Should comments on this reel be disabled)
        :param like_and_view_counts_disabled: Boolean (Shouldn't people be able to see how many users liked & viewed this reel)
        :param video_subtitles_enabled: Boolean (Should subtitles be enabled on this reel)
        :return: ReelUpload
        """
        request_headers: dict = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
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
            "x-instagram-ajax": "1009848613",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json = {
            "archive_only": archive_only,
            "caption": caption,
            "clips_share_preview_to_feed": "1",
            "disable_comments": "1" if disable_comments else "0",
            "disable_oa_reuse": "0",
            "igtv_share_preview_to_feed": "1",
            "is_meta_only_post": "0",
            "is_unified_video": "1",
            "like_and_view_counts_disabled": "1" if like_and_view_counts_disabled else "0",
            "source_type": "library",
            "upload_id": upload_id,
            "video_subtitles_enabled": "1" if video_subtitles_enabled else "0"
        }

        if alt_text != "": body_json["custom_accessibility_caption"] = alt_text

        http_response = self.request_session.post(
            "https://www.instagram.com/api/v1/media/configure_to_clips/",
            headers=request_headers,
            data=body_json
        )

        try:
            response_json: dict = http_response.json()
            return ReelUpload.from_response_data(response_json)

        except JSONDecodeError:
            raise NetworkError("Response not a valid json.")

    def comment(self, text: str, post_id: str) -> bool:
        """
        Adds a comment on target post.
        :param text: Comment text
        :param post_id: ID of target post, fetch using get_post_id() method
        :return: Boolean (Whether comment was successfully added or not)
        """

        request_headers: json = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.134\", "
                                           "\"Google Chrome\";v=\"114.0.5735.134\"",
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
            "Referer": f"https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json: json = {"comment_text": text}

        http_response = self.request_session.post(
            f"https://www.instagram.com/api/v1/web/comments/{post_id}/add/",
            headers=request_headers,
            data=body_json
        )

        try:
            response_json: dict = http_response.json()

            return response_json.get("status", "") == "ok"

        except JSONDecodeError:
            return False

    def __like_action(self, post_id: str, action: str = "like") -> bool:

        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.110\", "
                                           "\"Google Chrome\";v=\"114.0.5735.110\"",
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
            "x-instagram-ajax": "1007670408",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.post(
                f"https://www.instagram.com/api/v1/web/likes/{post_id}/{action}/",
                headers=request_headers
            )

            response_json = http_response.json()

            if "status" in response_json:
                return response_json["status"] == "ok"
            else:
                return False
        except JSONDecodeError:
            return False

    def like(self, post_id: str) -> bool:
        """
        Likes the target post.
        :param post_id: ID of target post, fetch using get_post_id() method
        :return: Boolean (Whether target post was liked successfully or not)
        """

        return self.__like_action(post_id, "like")

    def unlike(self, post_id: str) -> bool:
        """
        Unlikes the target post.
        :param post_id: ID of target post, fetch using get_post_id() method
        :return: Boolean (Whether target post was unliked successfully or not)
        """

        return self.__like_action(post_id, "unlike")

    def likers(self, post_id: str) -> Likers | None:
        """
        Generates a list of users who liked the target post of specified size.
        :param post_id: ID of target post, fetch using get_post_id() method
        :return: Generator which yields each user's data
        """

        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.134\", "
                                           "\"Google Chrome\";v=\"114.0.5735.134\"",
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
            "Referer": f"https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.get(
                f"https://www.instagram.com/api/v1/media/{post_id}/likers/",
                headers=request_headers
            )

            response_json: dict = http_response.json()

            if "status" not in response_json or "users" not in response_json:
                return None

            if response_json["status"] != "ok":
                return None

            likers_list = []
            for user in response_json["users"]:
                user: dict
                liker = Liker(
                    user_id=user.get("pk", ""),
                    username=user.get("username", ""),
                    full_name=user.get("full_name", ""),
                    is_private=user.get("is_private", False),
                    badges=user.get("account_badges", []),
                    is_verified=user.get("is_verified", False),
                    profile_picture_id=user.get("profile_pic_id", ""),
                    profile_picture_url=user.get("pprofile_pic_url", ""),
                    latest_reel_media=user.get("latest_reel_media", 0)
                )
                likers_list.append(liker)

            return Likers(
                user_count=response_json.get("user_count", 0),
                users=likers_list
            )
        except JSONDecodeError:
            return None
