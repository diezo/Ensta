from json import JSONDecodeError
import random
import string
import requests
from .lib.Commons import (
    update_session,
    update_homepage_source,
    update_app_id,
    refresh_csrf_token
)
from .lib import IdentifierError
from .responses.ProfileResponse import ProfileResponse
from .containers.Profile import Profile


class Guest:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = None
    csrf_token: str = None

    def __init__(self):
        update_session(self)
        update_homepage_source(self)
        update_app_id(self)

    def username_availability(self, username: str):
        username = username.strip().lower().replace(" ", "")
        refresh_csrf_token(self)
        preferred_color_scheme = random.choice(["light", "dark"])
        body_json = {
            "email": f"{username}@{self.csrf_token}.com",
            "username": username,
            "first_name": username.capitalize(),
            "opt_into_one_tap": False
        }
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": preferred_color_scheme,
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
            "x-ig-www-claim": "0",
            "x-instagram-ajax": "1007614758",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/emailsignup/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.post("https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/", headers=request_headers, data=body_json)
            response_json = http_response.json()

            if "errors" in response_json:

                username_suggestions = []
                if "username_suggestions" in response_json:
                    username_suggestions = response_json["username_suggestions"]

                if "username" in response_json["errors"]:
                    return {"success": True, "available": False, "suggestions": username_suggestions}
                else:
                    return {"success": True, "available": True, "suggestions": username_suggestions}
            else:
                return {"success": False, "available": None, "suggestions": []}
        except JSONDecodeError:
            return {"success": False, "available": None, "suggestions": []}

    def profile(self, identifier: str | int):
        conversion_success, identifier = self.identifier_conversion(identifier, 1)
        failure_response = ProfileResponse()
        if not conversion_success: return failure_response

        refresh_csrf_token(self)
        preferred_color_scheme = random.choice(["light", "dark"])
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": preferred_color_scheme,
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
            "x-ig-www-claim": "0",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{identifier}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={identifier}", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "data" in response_json:
                    if "user" in response_json["data"]:
                        profile_object = Profile()

                        if "biography" in response_json["data"]["user"]:
                            profile_object.biography = response_json["data"]["user"]["biography"]

                        if "country_block" in response_json["data"]["user"]:
                            profile_object.country_block = response_json["data"]["user"]["country_block"]

                        if "full_name" in response_json["data"]["user"]:
                            profile_object.full_name = response_json["data"]["user"]["full_name"]

                        if "edge_follow" in response_json["data"]["user"]:
                            if "count" in response_json["data"]["user"]:
                                profile_object.following_count = response_json["data"]["user"]["edge_follow"]["count"]

                        if "edge_followed_by" in response_json["data"]["user"]:
                            if "count" in response_json["data"]["user"]:
                                profile_object.follower_count = response_json["data"]["user"]["edge_followed_by"]["count"]

                        if "id" in response_json["data"]["user"]:
                            profile_object.user_id = response_json["data"]["user"]["id"]

                        if "is_business_account" in response_json["data"]["user"]:
                            profile_object.is_business_account = response_json["data"]["user"]["is_business_account"]

                        if "is_professional_account" in response_json["data"]["user"]:
                            profile_object.is_professional_account = response_json["data"]["user"]["is_professional_account"]

                        if "is_supervision_enabled" in response_json["data"]["user"]:
                            profile_object.is_supervision_enabled = response_json["data"]["user"]["is_supervision_enabled"]

                        if "is_joined_recently" in response_json["data"]["user"]:
                            profile_object.is_joined_recently = response_json["data"]["user"]["is_joined_recently"]

                        if "is_private" in response_json["data"]["user"]:
                            profile_object.is_private = response_json["data"]["user"]["is_private"]

                        if "is_verified" in response_json["data"]["user"]:
                            profile_object.is_verified = response_json["data"]["user"]["is_verified"]

                        if "profile_pic_url" in response_json["data"]["user"]:
                            profile_object.profile_picture_url = response_json["data"]["user"]["profile_pic_url"]

                        if "profile_pic_url_hd" in response_json["data"]["user"]:
                            profile_object.profile_picture_url_hd = response_json["data"]["user"]["profile_pic_url_hd"]

                        if "pronouns" in response_json["data"]["user"]:
                            user_pronouns = []
                            for pronoun in response_json["data"]["user"]["pronouns"]:
                                user_pronouns.append(pronoun)

                            profile_object.pronouns = user_pronouns

                        return ProfileResponse(success=True, user=profile_object)
                    else: return failure_response
                else: return failure_response
            else: return failure_response
        except JSONDecodeError: return failure_response

    def get_userid(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile(username)

        if response.success:
            if response.user.user_id is not None:
                return {"success": True, "user_id": str(response.user.user_id).strip()}
            else:
                return {"success": False, "user_id": ""}
        else:
            return {"success": False, "user_id": ""}

    def get_username(self, user_id: str | int):
        user_id = str(user_id).strip()
        request_headers = {
            "User-Agent": "Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)"
        }

        try:
            http_response = self.request_session.get(f"https://i.instagram.com/api/v1/users/{user_id}/info/", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "user" in response_json:
                    if "username" in response_json["user"]:
                        return {"success": True, "username": response_json["user"]["username"]}
                    else:
                        return {"success": False, "username": ""}
                else:
                    return {"success": False, "username": ""}
            else:
                return {"success": False, "username": ""}

        except JSONDecodeError:
            return {"success": False, "username": ""}

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
                user_id_response = self.get_userid(identifier)

                if user_id_response["success"]:
                    return True, user_id_response["user_id"]
                else:
                    return False, None
        else:
            if required == 0:
                username_response = self.get_username(identifier)

                if username_response["success"]:
                    return True, username_response["username"]
                else:
                    return False, None
            else:
                return identifier
