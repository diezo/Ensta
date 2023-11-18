from json import JSONDecodeError
import requests
from .lib.Commons import (
    refresh_csrf_token,
    format_username,
    format_uid
)
from .lib.Exceptions import APIError, NetworkError
from .containers.Profile import Profile
from .containers.ProfileHost import ProfileHost
import dataclasses
from fake_useragent import UserAgent


class Guest:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = "936619743392459"
    preferred_color_scheme: str = "dark"
    csrf_token: str = None

    def __init__(self, proxy: dict[str, str] | None = None) -> None:
        self.request_session = requests.Session()
        if proxy is not None: self.request_session.proxies.update(proxy)

    def username_availability(self, username: str) -> bool | None:
        username = format_username(username)
        refresh_csrf_token(self)
        body_json = {
            "email": f"{username}@{self.csrf_token}.com",
            "username": username,
            "first_name": username.capitalize(),
            "opt_into_one_tap": False
        }
        ua = UserAgent().random
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": ua,
            "sec-ch-ua-full-version-list": ua,
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
            raise NetworkError("HTTP Response is not a valid JSON.")

    def profile(self, username: str, __session__: requests.Session | None = None) -> Profile | ProfileHost | None:
        username: str = format_username(username)
        refresh_csrf_token(self)
        ua = UserAgent().random
        request_headers: dict = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": ua,
            "sec-ch-ua-full-version-list": ua,
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
            session: requests.Session = __session__
            if __session__ is None: session: requests.Session = self.request_session

            http_response: requests.Response = session.get(
                f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
                headers=request_headers,
            )
            response_json: dict = http_response.json()

            if "status" in response_json:
                if response_json["status"] == "ok" and "data" in response_json:
                    if "user" in response_json["data"]:
                        try:
                            data: dict = response_json["data"]["user"]

                            if data is None:
                                raise APIError("User object not found inside HTTP response.")

                            profile = Profile(
                                raw=data,
                                biography=data["biography"],
                                biography_links=data["bio_links"],
                                country_block=data["country_block"],
                                full_name=data["full_name"],
                                follower_count=data["edge_followed_by"]["count"],
                                following_count=data["edge_follow"]["count"],
                                user_id=data["id"],
                                category_name=data["category_name"],
                                is_business_account=data["is_business_account"],
                                is_professional_account=data["is_professional_account"],
                                is_supervision_enabled=data["is_supervision_enabled"],
                                is_joined_recently=data["is_joined_recently"],
                                is_private=data["is_private"],
                                is_verified=data["is_verified"],
                                profile_picture_url=data["profile_pic_url"],
                                profile_picture_url_hd=data["profile_pic_url_hd"],
                                pronouns=data["pronouns"],
                                has_ar_effects=data["has_ar_effects"],
                                has_clips=data["has_clips"],
                                has_guides=data["has_guides"],
                                has_channel=data["has_channel"],
                                highlight_count=data["highlight_reel_count"],
                                hide_like_and_view_counts=data["hide_like_and_view_counts"],
                                is_embeds_disabled=data["is_embeds_disabled"],
                                is_verified_by_mv4b=data["is_verified_by_mv4b"],
                                should_show_category=data["should_show_category"],
                                should_show_public_contacts=data["should_show_public_contacts"],
                                show_account_transparency_details=data["show_account_transparency_details"],
                                total_post_count=data["edge_owner_to_timeline_media"]["count"]
                            )

                            if __session__ is not None:
                                profile_host = ProfileHost()

                                for key, value in dataclasses.asdict(profile).items():
                                    setattr(profile_host, key, value)

                                profile_host.blocked_by_viewer = data["blocked_by_viewer"]
                                profile_host.followed_by_viewer = data["followed_by_viewer"]
                                profile_host.follows_viewer = data["follows_viewer"]
                                profile_host.has_blocked_viewer = data["has_blocked_viewer"]
                                profile_host.has_requested_viewer = data["has_requested_viewer"]
                                profile_host.is_guardian_of_viewer = data["is_guardian_of_viewer"]
                                profile_host.is_supervised_by_viewer = data["is_supervised_by_viewer"]
                                profile_host.requested_by_viewer = data["requested_by_viewer"]
                                profile_host.mutual_follower_count = data["edge_mutual_followed_by"]["count"]

                                return profile_host

                            return profile
                        except KeyError:
                            raise APIError()
        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def get_uid(self, username: str, __session__: requests.Session | None = None) -> str | None:
        username: str = username.strip().lower().replace(" ", "")
        response: Profile | None = self.profile(username, __session__)

        if response.user_id is not None:
            return format_uid(response.user_id)

    def get_username(self, uid: str | int, __session__: requests.Session | None = None) -> str | None:
        uid = format_uid(uid)
        refresh_csrf_token(self)
        request_headers = {
            "User-Agent": "Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)"
        }

        try:
            session: requests.Session = __session__
            if __session__ is None: session: requests.Session = self.request_session

            http_response = session.get(f"https://i.instagram.com/api/v1/users/{uid}/info/", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json and response_json["status"] == "ok" and "user" in response_json and "username" in response_json["user"]:
                return format_username(response_json["user"]["username"])

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")
