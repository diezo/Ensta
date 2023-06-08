import requests
import requests.cookies
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
    IdentifierTypeError
)
from .data_classes import FollowerInternal
from ensta.identifier import IDENTIFIER_USERNAME, IDENTIFIER_USERID


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

    def follow_user_id(self, user_id: str | int):
        user_id = str(user_id).strip()
        refresh_csrf_token(self)
        random_referer_username = "".join(random.choices(string.ascii_lowercase, k=6))
        body_json = {
            "container_module": "profile",
            "nav_chain": f"PolarisProfileRoot:profilePage:1:via_cold_start",
            "user_id": user_id
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

        failure_response = {"success": False, "following": None, "follow_requested": None, "previous_following": None, "is_my_follower": None}
        http_response = self.request_session.post(f"https://www.instagram.com/api/v1/friendships/create/{user_id}/", headers=request_headers, data=body_json)

        try:
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"] \
                            and "followed_by" in response_json["friendship_status"] \
                            and "previous_following" in response_json:
                        return {
                            "success": True,
                            "following": response_json["friendship_status"]["following"],
                            "follow_requested": response_json["friendship_status"]["outgoing_request"],
                            "is_my_follower": response_json["friendship_status"]["followed_by"],
                            "previous_following": response_json["previous_following"]
                        }
                    else: return failure_response
                else: return failure_response
            else: return failure_response
        except JSONDecodeError: return failure_response

    def follow_username(self, username: str):
        username = username.lower().strip().replace(" ", "")
        user_id_response = self.guest.get_userid(username)
        failure_response = {"success": False, "following": None, "follow_requested": None, "previous_following": None, "is_my_follower": None}

        if user_id_response["success"]:
            return self.follow_user_id(user_id_response["user_id"])
        else:
            return failure_response

    def unfollow_user_id(self, user_id: str | int):
        user_id = str(user_id).strip()
        refresh_csrf_token(self)
        random_referer_username = "".join(random.choices(string.ascii_lowercase, k=6))
        body_json = {
            "container_module": "profile",
            "nav_chain": f"PolarisProfileRoot:profilePage:1:via_cold_start",
            "user_id": user_id
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

        failure_response = {"success": False, "unfollowed": None}
        http_response = self.request_session.post(f"https://www.instagram.com/api/v1/friendships/destroy/{user_id}/", headers=request_headers, data=body_json)

        try:
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "friendship_status" in response_json:
                    if "following" in response_json["friendship_status"] \
                            and "outgoing_request" in response_json["friendship_status"]:
                        return {
                            "success": True,
                            "unfollowed": not response_json["friendship_status"]["following"] and not response_json["friendship_status"]["outgoing_request"]
                        }
                    else: return failure_response
                else: return failure_response
            else: return failure_response
        except JSONDecodeError: return failure_response

    def unfollow_username(self, username: str):
        username = username.lower().strip().replace(" ", "")
        user_id_response = self.guest.get_userid(username)
        failure_response = {"success": False, "unfollowed": None}

        if user_id_response["success"]:
            return self.unfollow_user_id(user_id_response["user_id"])
        else:
            return failure_response

    def follower_list(self, identifier_type: int, identifier: str | int, count: int):

        # Identifier Conversion
        if identifier_type == IDENTIFIER_USERNAME:
            username = identifier.lower().strip().replace(" ", "")
            user_id_response = self.guest.get_userid(username)
            failure_response = {"success": False, "follower_list": None}

            if user_id_response["success"]:
                user_id = user_id_response["user_id"]
            else:
                return failure_response
        elif identifier_type == IDENTIFIER_USERID:
            user_id = str(identifier).strip()
        else:
            raise IdentifierTypeError(f"{str(identifier_type)} is not a valid identifier type. Please choose a valid identifier type from ensta.identifier package.")

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

        failure_response = {"success": False, "follower_list": None}
        max_id = ""
        required_list = []

        while True:
            if max_id != "":
                max_id_text = f"&max_id={max_id}"
            else:
                max_id_text = ""

            http_response = self.request_session.get(f"https://www.instagram.com/api/v1/friendships/{user_id}/followers/?count={30}{max_id_text}&search_surface=follow_list_page", headers=request_headers)

            try:
                response_json = http_response.json()

                if "status" not in response_json or "users" not in response_json:
                    return failure_response

                if response_json["status"] != "ok":
                    return failure_response

                for each_item in response_json["users"]:
                    if len(required_list) < count or count == 0:
                        follower_obj = FollowerInternal()

                        if "has_anonymous_profile_picture" in each_item:
                            follower_obj.has_anonymous_profile_picture = each_item["has_anonymous_profile_picture"]

                        if "pk" in each_item:
                            follower_obj.user_id = each_item["pk"]

                        if "username" in each_item:
                            follower_obj.username = each_item["username"]

                        if "full_name" in each_item:
                            follower_obj.full_name = each_item["full_name"]

                        if "is_private" in each_item:
                            follower_obj.is_private = each_item["is_private"]

                        if "is_verified" in each_item:
                            follower_obj.is_verified = each_item["is_verified"]

                        if "profile_pic_url" in each_item:
                            follower_obj.profile_picture_url = each_item["profile_pic_url"]

                        if "is_possible_scammer" in each_item:
                            follower_obj.is_possible_scammer = each_item["is_possible_scammer"]

                        required_list.append(follower_obj)

                if (len(required_list) < count or count == 0) and "next_max_id" in response_json:
                    max_id = response_json["next_max_id"]
                else:
                    return {"success": True, "follower_list": required_list, "list_size": len(required_list)}
            except JSONDecodeError: return failure_response
