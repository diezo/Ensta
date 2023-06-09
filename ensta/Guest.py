from json import JSONDecodeError
import random
import requests
from .lib.Commons import (
    update_session,
    update_homepage_source,
    update_app_id,
    refresh_csrf_token,
    format_username,
    format_uid
)
from .containers.Profile import Profile


class Guest:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = None
    csrf_token: str = None

    def __init__(self, homepage_source: str = None, insta_app_id: str = None) -> None:
        update_session(self)

        if homepage_source is not None:
            self.homepage_source = homepage_source
        else:
            update_homepage_source(self)

        if insta_app_id is not None:
            self.insta_app_id = insta_app_id
        else:
            update_app_id(self)

    def username_availability(self, username: str) -> bool | None:
        username = format_username(username)
        refresh_csrf_token(self)
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
            "sec-ch-prefers-color-scheme": random.choice(["light", "dark"]),
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
                return "username" not in response_json["errors"]
        except JSONDecodeError:
            return None

    def profile(self, username: str) -> Profile:
        username = format_username(username)
        failure_response = Profile()

        refresh_csrf_token(self)
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": random.choice(["light", "dark"]),
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
            "Referer": f"https://www.instagram.com/{username}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.get(
                f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                headers=request_headers
            )
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "data" in response_json:
                    if "user" in response_json["data"]:

                        profile_object_biography = None
                        profile_object_country_block = None
                        profile_object_full_name = None
                        profile_object_following_count = None
                        profile_object_follower_count = None
                        profile_object_user_id = None
                        profile_object_is_business_account = None
                        profile_object_is_professional_account = None
                        profile_object_is_supervision_enabled = None
                        profile_object_is_joined_recently = None
                        profile_object_is_private = None
                        profile_object_is_verified = None
                        profile_object_profile_picture_url = None
                        profile_object_profile_picture_url_hd = None
                        profile_object_pronouns = None

                        if "biography" in response_json["data"]["user"]:
                            profile_object_biography = response_json["data"]["user"]["biography"]

                        if "country_block" in response_json["data"]["user"]:
                            profile_object_country_block = response_json["data"]["user"]["country_block"]

                        if "full_name" in response_json["data"]["user"]:
                            profile_object_full_name = response_json["data"]["user"]["full_name"]

                        if "edge_follow" in response_json["data"]["user"]:
                            if "count" in response_json["data"]["user"]["edge_follow"]:
                                profile_object_following_count = response_json["data"]["user"]["edge_follow"]["count"]

                        if "edge_followed_by" in response_json["data"]["user"]:
                            if "count" in response_json["data"]["user"]["edge_followed_by"]:
                                profile_object_follower_count = response_json["data"]["user"]["edge_followed_by"]["count"]

                        if "id" in response_json["data"]["user"]:
                            profile_object_user_id = response_json["data"]["user"]["id"]

                        if "is_business_account" in response_json["data"]["user"]:
                            profile_object_is_business_account = response_json["data"]["user"]["is_business_account"]

                        if "is_professional_account" in response_json["data"]["user"]:
                            profile_object_is_professional_account = response_json["data"]["user"]["is_professional_account"]

                        if "is_supervision_enabled" in response_json["data"]["user"]:
                            profile_object_is_supervision_enabled = response_json["data"]["user"][
                                "is_supervision_enabled"]

                        if "is_joined_recently" in response_json["data"]["user"]:
                            profile_object_is_joined_recently = response_json["data"]["user"]["is_joined_recently"]

                        if "is_private" in response_json["data"]["user"]:
                            profile_object_is_private = response_json["data"]["user"]["is_private"]

                        if "is_verified" in response_json["data"]["user"]:
                            profile_object_is_verified = response_json["data"]["user"]["is_verified"]

                        if "profile_pic_url" in response_json["data"]["user"]:
                            profile_object_profile_picture_url = response_json["data"]["user"]["profile_pic_url"]

                        if "profile_pic_url_hd" in response_json["data"]["user"]:
                            profile_object_profile_picture_url_hd = response_json["data"]["user"]["profile_pic_url_hd"]

                        if "pronouns" in response_json["data"]["user"]:
                            user_pronouns = []
                            for pronoun in response_json["data"]["user"]["pronouns"]:
                                user_pronouns.append(pronoun)
                            profile_object_pronouns = user_pronouns

                        return Profile(biography=profile_object_biography,
                                       country_block=profile_object_country_block,
                                       full_name=profile_object_full_name,
                                       follower_count=profile_object_follower_count,
                                       following_count=profile_object_following_count,
                                       user_id=profile_object_user_id,
                                       is_business_account=profile_object_is_business_account,
                                       is_professional_account=profile_object_is_professional_account,
                                       is_supervision_enabled=profile_object_is_supervision_enabled,
                                       is_joined_recently=profile_object_is_joined_recently,
                                       is_private=profile_object_is_private,
                                       is_verified=profile_object_is_verified,
                                       profile_picture_url=profile_object_profile_picture_url,
                                       profile_picture_url_hd=profile_object_profile_picture_url_hd,
                                       pronouns=profile_object_pronouns)

                    else:
                        return failure_response
                else:
                    return failure_response
            else:
                return failure_response
        except JSONDecodeError:
            return failure_response

    def get_uid(self, username: str) -> str | None:
        username = username.strip().lower().replace(" ", "")
        response = self.profile(username)

        if response.user_id is not None:
            return format_uid(response.user_id)

    def get_username(self, uid: str | int) -> str | None:
        uid = format_uid(uid)
        refresh_csrf_token(self)
        request_headers = {
            "User-Agent": "Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)"
        }

        try:
            http_response = self.request_session.get(f"https://i.instagram.com/api/v1/users/{uid}/info/", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json and response_json["status"] == "ok" and "user" in response_json and "username" in response_json["user"]:
                return format_username(response_json["user"]["username"])

        except JSONDecodeError:
            return None
