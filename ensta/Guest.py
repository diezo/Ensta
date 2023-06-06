from json import JSONDecodeError
import base64
import random
import requests
import requests.cookies
from .lib import commons


class Guest:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = None
    csrf_token: str = None

    def __init__(self):
        commons.update_session(self)
        commons.update_homepage_source(self)
        commons.update_app_id(self)

    def username_availability(self, username: str):
        username = username.strip().lower().replace(" ", "")
        commons.refresh_csrf_token(self)
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

    def profile_info(self, username: str):
        username = username.strip().lower().replace(" ", "")
        commons.refresh_csrf_token(self)
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
            "Referer": f"https://www.instagram.com/{username}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "data" in response_json:
                    if "user" in response_json["data"]:
                        return {"success": True, "data": response_json["data"]["user"]}
                    else:
                        return {"success": False, "data": None}
                else:
                    return {"success": False, "data": None}
            else:
                return {"success": False, "data": None}
        except JSONDecodeError:
            return {"success": False, "data": None}

    def get_userid(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "id" in response["data"]:
                return {"success": True, "user_id": str(response["data"]["id"]).strip()}
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

    def get_follower_count(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "edge_followed_by" in response["data"]:
                if "count" in response["data"]["edge_followed_by"]:
                    return {"success": True, "follower_count": response["data"]["edge_followed_by"]["count"]}
                else:
                    return {"success": False, "follower_count": ""}
            else:
                return {"success": False, "follower_count": ""}
        else:
            return {"success": False, "follower_count": ""}

    def get_following_count(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "edge_follow" in response["data"]:
                if "count" in response["data"]["edge_follow"]:
                    return {"success": True, "following_count": response["data"]["edge_follow"]["count"]}
                else:
                    return {"success": False, "following_count": ""}
            else:
                return {"success": False, "following_count": ""}
        else:
            return {"success": False, "following_count": ""}

    def get_biography(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "biography" in response["data"]:
                return {"success": True, "biography": response["data"]["biography"]}
            else:
                return {"success": False, "biography": ""}
        else:
            return {"success": False, "biography": ""}

    def get_display_name(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "full_name" in response["data"]:
                return {"success": True, "display_name": response["data"]["full_name"]}
            else:
                return {"success": False, "display_name": ""}
        else:
            return {"success": False, "display_name": ""}

    def get_profile_picture_url(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "profile_pic_url" in response["data"]:
                return {"success": True, "profile_picture_url": str(response["data"]["profile_pic_url"]).strip()}
            else:
                return {"success": False, "profile_picture_url": ""}
        else:
            return {"success": False, "profile_picture_url": ""}

    def get_profile_picture_url_hd(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "profile_pic_url_hd" in response["data"]:
                return {"success": True, "profile_picture_url_hd": str(response["data"]["profile_pic_url_hd"]).strip()}
            else:
                return {"success": False, "profile_picture_url_hd": ""}
        else:
            return {"success": False, "profile_picture_url_hd": ""}

    def get_profile_picture_base64(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = self.get_profile_picture_url(username, profile_snapshot)
        else:
            response = self.get_profile_picture_url(username)

        if response["success"]:
            profile_picture_url = response["profile_picture_url"]

            if profile_picture_url == "":
                return {"success": False, "profile_picture_base64": ""}

            base64_image = base64.b64encode(requests.get(profile_picture_url).content).decode("utf-8")
            return {"success": True, "profile_picture_base64": f"data:image/jpg;base64,{base64_image}"}
        else:
            return {"success": False, "profile_picture_base64": ""}

    def get_profile_picture_base64_hd(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = self.get_profile_picture_url_hd(username, profile_snapshot)
        else:
            response = self.get_profile_picture_url_hd(username)

        if response["success"]:
            profile_picture_url_hd = response["profile_picture_url_hd"]

            if profile_picture_url_hd == "":
                return {"success": False, "profile_picture_base64_hd": ""}

            base64_image = base64.b64encode(requests.get(profile_picture_url_hd).content).decode("utf-8")
            return {"success": True, "profile_picture_base64_hd": f"data:image/jpg;base64,{base64_image}"}
        else:
            return {"success": False, "profile_picture_base64_hd": ""}

    def is_account_private(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "is_private" in response["data"]:
                return {"success": True, "private": response["data"]["is_private"]}
            else:
                return {"success": False, "private": None}
        else:
            return {"success": False, "private": None}

    def is_account_verified(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "is_verified" in response["data"]:
                return {"success": True, "verified": response["data"]["is_verified"]}
            else:
                return {"success": False, "verified": None}
        else:
            return {"success": False, "verified": None}

    def is_business_account(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "is_business_account" in response["data"]:
                return {"success": True, "business_account": response["data"]["is_business_account"]}
            else:
                return {"success": False, "business_account": None}
        else:
            return {"success": False, "business_account": None}

    def is_professional_account(self, username: str, profile_snapshot: dict | None = None):
        username = username.strip().lower().replace(" ", "")

        if profile_snapshot is not None:
            response = profile_snapshot
        else:
            response = self.profile_info(username)

        if response["success"]:
            if "is_professional_account" in response["data"]:
                return {"success": True, "professional_account": response["data"]["is_professional_account"]}
            else:
                return {"success": False, "professional_account": None}
        else:
            return {"success": False, "professional_account": None}
