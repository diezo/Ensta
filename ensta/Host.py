import requests
from json import JSONDecodeError
import random
import string
from .Guest import Guest
from .lib.Commons import (
    refresh_csrf_token,
    update_app_id,
    update_homepage_source,
    update_session
)
from .lib import (
    AuthenticationError,
    NetworkError,
    IdentifierError
)
from .containers import FollowListPerson
from .responses.FollowPersonListResponse import FollowPersonListResponse
from .responses.FollowPersonResponse import FollowPersonResponse
from .responses.UnfollowPersonResponse import UnfollowPersonResponse


class Host:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = None
    preferred_color_scheme: str = "dark"
    x_ig_www_claim: str = None
    csrf_token: str = None
    guest: Guest = None

    def __init__(self, session_id: str):
        self.x_ig_www_claim = "hmac." + "".join(random.choices(string.ascii_letters + string.digits + "_-", k=48))
        update_session(self)
        update_homepage_source(self)
        update_app_id(self)
        self.guest = Guest()

        self.request_session.cookies.set("sessionid", session_id)

        if not self.is_authenticated():
            raise AuthenticationError("Either User ID or Session ID is not valid.")

    def update_homepage_source(self):
        temp_homepage_source = requests.get("https://www.instagram.com/").text.strip()

        if temp_homepage_source != "":
            self.homepage_source = temp_homepage_source
        else:
            raise NetworkError("Couldn't load instagram homepage.")

    def is_authenticated(self):
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

    def follow(self, identifier: str | int):
        conversion_success, identifier = self.identifier_conversion(identifier, 1)
        failure_response = FollowPersonResponse()
        if not conversion_success: return failure_response

        # Actual Request
        refresh_csrf_token(self)
        random_referer_username = "".join(random.choices(string.ascii_lowercase, k=6))
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
            "Referer": f"https://www.instagram.com/{random_referer_username}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        http_response = self.request_session.post(f"https://www.instagram.com/api/v1/friendships/create/{identifier}/", headers=request_headers, data=body_json)

        try:
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"] \
                            and "followed_by" in response_json["friendship_status"] \
                            and "previous_following" in response_json:
                        return FollowPersonResponse(
                            success=True,
                            following=response_json["friendship_status"]["following"],
                            follow_requested=response_json["friendship_status"]["outgoing_request"],
                            is_my_follower=response_json["friendship_status"]["followed_by"],
                            previous_following=response_json["previous_following"]
                        )
                    else: return failure_response
                else: return failure_response
            else: return failure_response
        except JSONDecodeError: return failure_response

    def unfollow(self, identifier: str | int):
        conversion_success, identifier = self.identifier_conversion(identifier, 1)
        failure_response = UnfollowPersonResponse()
        if not conversion_success: return failure_response

        # Actual Request
        refresh_csrf_token(self)
        random_referer_username = "".join(random.choices(string.ascii_lowercase, k=6))
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
            "Referer": f"https://www.instagram.com/{random_referer_username}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        http_response = self.request_session.post(f"https://www.instagram.com/api/v1/friendships/destroy/{identifier}/", headers=request_headers, data=body_json)

        try:
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"]:
                        return UnfollowPersonResponse(
                            success=True,
                            unfollowed=not response_json["friendship_status"]["following"] and not response_json["friendship_status"]["outgoing_request"]
                        )
                    else: return failure_response
                else: return failure_response
            else: return failure_response
        except JSONDecodeError: return failure_response

    def follower_list(self, identifier: str | int, count: int):
        conversion_success, identifier = self.identifier_conversion(identifier, 1)
        failure_response = FollowPersonListResponse()
        if not conversion_success: return failure_response

        # Actual Request
        refresh_csrf_token(self)
        random_referer_username = "".join(random.choices(string.ascii_lowercase, k=6))
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
            "Referer": f"https://www.instagram.com/{random_referer_username}/followers/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        max_id = ""
        required_list = []

        while True:
            if max_id != "":
                max_id_text = f"&max_id={max_id}"
            else:
                max_id_text = ""

            http_response = self.request_session.get(f"https://www.instagram.com/api/v1/friendships/{identifier}/followers/?count={30}{max_id_text}&search_surface=follow_list_page", headers=request_headers)

            try:
                response_json = http_response.json()

                if "status" not in response_json or "users" not in response_json:
                    return failure_response

                if response_json["status"] != "ok":
                    return failure_response

                for each_item in response_json["users"]:
                    if len(required_list) < count or count == 0:

                        prop_has_anonymous_profile_picture = False
                        prop_user_id = ""
                        prop_username = ""
                        prop_full_name = ""
                        prop_is_private = False
                        prop_is_verified = False
                        prop_profile_picture_url = ""
                        prop_is_possible_scammer = False

                        if "has_anonymous_profile_picture" in each_item:
                            prop_has_anonymous_profile_picture = each_item["has_anonymous_profile_picture"]

                        if "pk" in each_item:
                            prop_user_id = each_item["pk"]

                        if "username" in each_item:
                            prop_username = each_item["username"]

                        if "full_name" in each_item:
                            prop_full_name = each_item["full_name"]

                        if "is_private" in each_item:
                            prop_is_private = each_item["is_private"]

                        if "is_verified" in each_item:
                            prop_is_verified = each_item["is_verified"]

                        if "profile_pic_url" in each_item:
                            prop_profile_picture_url = each_item["profile_pic_url"]

                        if "is_possible_scammer" in each_item:
                            prop_is_possible_scammer = each_item["is_possible_scammer"]

                        follow_person = FollowListPerson(
                            has_anonymous_profile_picture=prop_has_anonymous_profile_picture,
                            user_id=prop_user_id,
                            username=prop_username,
                            full_name=prop_full_name,
                            is_private=prop_is_private,
                            is_verified=prop_is_verified,
                            profile_picture_url=prop_profile_picture_url,
                            is_possible_scammer=prop_is_possible_scammer
                        )
                        required_list.append(follow_person)

                if (len(required_list) < count or count == 0) and "next_max_id" in response_json:
                    max_id = response_json["next_max_id"]
                else:
                    return FollowPersonListResponse(success=True, users=required_list)
            except JSONDecodeError: return failure_response

    def following_list(self, identifier: str | int, count: int):
        conversion_success, identifier = self.identifier_conversion(identifier, 1)
        failure_response = FollowPersonListResponse()
        if not conversion_success: return failure_response

        # Actual Request
        refresh_csrf_token(self)
        random_referer_username = "".join(random.choices(string.ascii_lowercase, k=6))
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
            "Referer": f"https://www.instagram.com/{random_referer_username}/following/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        max_id = ""
        required_list = []

        while True:
            if max_id != "":
                max_id_text = f"&max_id={max_id}"
            else:
                max_id_text = ""

            http_response = self.request_session.get(f"https://www.instagram.com/api/v1/friendships/{identifier}/following/?count={30}{max_id_text}", headers=request_headers)

            try:
                response_json = http_response.json()

                if "status" not in response_json or "users" not in response_json:
                    return failure_response

                if response_json["status"] != "ok":
                    return failure_response

                for each_item in response_json["users"]:
                    if len(required_list) < count or count == 0:

                        prop_has_anonymous_profile_picture = False
                        prop_user_id = ""
                        prop_username = ""
                        prop_full_name = ""
                        prop_is_private = False
                        prop_is_verified = False
                        prop_profile_picture_url = ""
                        prop_is_possible_scammer = False

                        if "has_anonymous_profile_picture" in each_item:
                            prop_has_anonymous_profile_picture = each_item["has_anonymous_profile_picture"]

                        if "pk" in each_item:
                            prop_user_id = each_item["pk"]

                        if "username" in each_item:
                            prop_username = each_item["username"]

                        if "full_name" in each_item:
                            prop_full_name = each_item["full_name"]

                        if "is_private" in each_item:
                            prop_is_private = each_item["is_private"]

                        if "is_verified" in each_item:
                            prop_is_verified = each_item["is_verified"]

                        if "profile_pic_url" in each_item:
                            prop_profile_picture_url = each_item["profile_pic_url"]

                        if "is_possible_scammer" in each_item:
                            prop_is_possible_scammer = each_item["is_possible_scammer"]

                        follow_person = FollowListPerson(
                            has_anonymous_profile_picture=prop_has_anonymous_profile_picture,
                            user_id=prop_user_id,
                            username=prop_username,
                            full_name=prop_full_name,
                            is_private=prop_is_private,
                            is_verified=prop_is_verified,
                            profile_picture_url=prop_profile_picture_url,
                            is_possible_scammer=prop_is_possible_scammer
                        )
                        required_list.append(follow_person)

                if (len(required_list) < count or count == 0) and "next_max_id" in response_json:
                    max_id = response_json["next_max_id"]
                else:
                    return FollowPersonListResponse(success=True, users=required_list)
            except JSONDecodeError: return failure_response

    def identifier_conversion(self, identifier: str | int, required: str | int):
        identifier = str(identifier).lower().replace(" ", "")
        if len(identifier) < 1: raise IdentifierError(
            "No identifier was given. Please pass either UserId or Username as an argument.")

        # Detect if identifier is Username or UserId
        is_username = False
        for letter in identifier:
            if letter not in string.digits:
                is_username = True
                break

        # Generate UserId if identifier is Username
        if is_username:
            if required == 0:
                return identifier
            else:
                user_id_response = self.guest.get_userid(identifier)

                if user_id_response["success"]:
                    return True, user_id_response["user_id"]
                else:
                    return False, None
        else:
            if required == 0:
                username_response = self.guest.get_username(identifier)

                if username_response["success"]:
                    return True, username_response["username"]
                else:
                    return False, None
            else:
                return identifier
