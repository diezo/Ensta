import requests
import requests.cookies
from ensta.lib import exceptions
from json import JSONDecodeError
import random
import string
from Guest import Guest
from ensta.lib import commons


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
        commons.update_session(self)
        commons.update_homepage_source(self)
        commons.update_app_id(self)
        self.guest = Guest()

        self.request_session.cookies.set("sessionid", session_id)

        if not self.is_authenticated():
            raise exceptions.AuthenticationError("Either User ID or Session ID is not valid.")

    def update_homepage_source(self):
        temp_homepage_source = requests.get("https://www.instagram.com/").text.strip()

        if temp_homepage_source != "":
            self.homepage_source = temp_homepage_source
        else:
            raise exceptions.NetworkError("Couldn't load instagram homepage.")

    def is_authenticated(self):
        commons.refresh_csrf_token(self)
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
        commons.refresh_csrf_token(self)
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
