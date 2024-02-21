import string
import random
import requests
import dataclasses
from json import JSONDecodeError
from .containers.Profile import Profile
from .containers.ProfileHost import ProfileHost
from .lib.Exceptions import APIError, NetworkError, RateLimitedError
from collections.abc import Generator
from .containers.Post import Post
from .containers.PostUser import PostUser


class Guest:
    request_session: requests.Session = None
    homepage_source: str = None
    insta_app_id: str = "936619743392459"
    preferred_color_scheme: str = "dark"
    x_ig_www_claim: str
    csrf_token: str = None
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                      "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    def __init__(self, proxy: dict[str, str] | None = None) -> None:
        self.request_session = requests.Session()
        self.x_ig_www_claim = "hmac." + "".join(random.choices(string.ascii_letters + string.digits + "_-", k=48))
        self.csrf_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
        self.request_session.cookies.set("csrftoken", self.csrf_token)

        if proxy is not None: self.request_session.proxies.update(proxy)

    def username_availability(self, username: str) -> bool | None:
        username = username.replace(" ", "").lower()

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
            "x-ig-www-claim": "0",
            "x-instagram-ajax": "1007614758",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/emailsignup/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.request_session.post(
                "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/",
                headers=request_headers,
                data=body_json
            )
            response_json = http_response.json()

            if "errors" in response_json:
                return "username" not in response_json["errors"]
        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def profile(self, username: str, __session__: requests.Session | None = None) -> Profile | ProfileHost | None:
        username: str = username.replace(" ", "").lower()

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
            "x-ig-www-claim": "0",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/{username}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        session: requests.Session = __session__
        if __session__ is None: session: requests.Session = self.request_session

        http_response: requests.Response = session.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers=request_headers,
            allow_redirects=False
        )

        if http_response.status_code == 302:
            raise RateLimitedError(
                "Your IP Address has been temporarily flagged, maybe because you made too many requests. "
                "Please wait for some time, or switch to a different WiFi network, or use proxies. "
                "And be careful next time."
            ) if __session__ is None else RateLimitedError(
                "Your actions are being temporarily limited, maybe because "
                "Instagram suspected automated behaviour on your account. "
                "Please wait for some time, or use a different account. "
                "And be careful next time to avoid a permanent ban."
            )

        try:
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
            return response.user_id.replace(" ", "")

    def get_username(self, uid: str | int, __session__: requests.Session | None = None) -> str | None:
        uid = uid.replace(" ", "")

        request_headers = {
            "User-Agent": "Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; "
                          "samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)"
        }

        try:
            session: requests.Session = __session__
            if __session__ is None: session: requests.Session = self.request_session

            http_response = session.get(f"https://i.instagram.com/api/v1/users/{uid}/info/", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json \
                    and response_json["status"] == "ok" \
                    and "user" in response_json \
                    and "username" in response_json["user"]:

                return response_json["user"]["username"].replace(" ", "").lower()

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    def posts(self, username: str, count: int = 0, __session__: requests.Session | None = None) -> Generator[Post, None, None]:
        """
        Generates a list of target's posts of specified size.
        :param username: Target's Username
        :param count: Amount of posts to fetch
        :param __session__: (Optional) Custom request session object
        :return: Generator which yields each post's data
        """

        username = username.replace(" ", "").lower()

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

                session: requests.Session = __session__
                if __session__ is None: session: requests.Session = self.request_session

                http_response = session.get(
                    f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count_text}"
                    f"{current_max_id_text}",
                    headers=request_headers
                )
                
                response_json = http_response.json()

                if "status" not in response_json or "items" not in response_json:
                    yield None
                    raise NetworkError("HTTP response doesn't include 'status' or 'items' node.")

                if response_json["status"] != "ok":
                    yield None
                    
                    if response_json.get("message", "") == "checkpoint_required":
                        raise RateLimitedError(
                            "IP Temporarily Flagged: Wait for some time, or switch "
                            "to a different WiFi Network, or use proxies."
                        )

                    raise NetworkError("Request failed.")

                for each_item in response_json["items"]:
                    if generated_count < count or count == 0:

                        yield self.__process_post_data(each_item)
                        generated_count += 1

                if (generated_count < count or count == 0) and "next_max_id" in response_json:
                    current_max_id = response_json["next_max_id"]
                else:
                    return None
            except JSONDecodeError:
                yield None
                raise NetworkError("HTTP Response is not a valid JSON.")

    def reels(
        self,
        uid: str | int,
        count: int = 0,
        __session__: requests.Session | None = None,
    ) -> Generator[Post, None, None]:
        """
        Generates a list of target's reels of specified size.
        :param uid: Target's user ID
        :param count: Amount of reels to fetch
        :param __session__: (Optional) Custom request session object
        :return: Generator which yields each reel's data
        """

        uid = str(uid).replace(" ", "")

        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.preferred_color_scheme,
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"15.0.0"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

        generated_count = 0
        max_id = None

        while True:
            try:
                session: requests.Session = __session__
                if __session__ is None:
                    session: requests.Session = self.request_session

                http_response = session.post(
                    "https://www.instagram.com/api/v1/clips/user/",
                    data={
                        "target_user_id": user_id,
                        "page_size": "50",
                        "include_feed_video": "true",
                        "max_id": max_id,
                    },
                    headers=request_headers,
                )

                response_json = http_response.json()

                if "status" not in response_json or "items" not in response_json:
                    yield None
                    raise NetworkError(
                        "HTTP response doesn't include 'status' or 'items' node."
                    )

                if response_json["status"] != "ok":
                    yield None

                    if response_json.get("message", "") == "checkpoint_required":
                        raise RateLimitedError(
                            "IP Temporarily Flagged: Wait for some time, or switch "
                            "to a different WiFi Network, or use proxies."
                        )

                    raise NetworkError("Request failed.")

                for each_item in response_json["items"]:
                    if generated_count < count or count == 0:
                        yield self.__process_post_data(each_item["media"], reel=True)
                        generated_count += 1

                if (generated_count < count or count == 0) and response_json.get(
                    "paging_info", {}
                ).get("more_available", False):
                    max_id = response_json["paging_info"]["max_id"]
                else:
                    return None
            except JSONDecodeError:
                yield None
                raise NetworkError("HTTP Response is not a valid JSON.")

    @staticmethod
    def __process_post_data(data: dict, reel: bool = False) -> Post:
        caption: dict | None = data.get("caption", None)

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
        user_data: dict | None = data.get("user", None)

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
            share_url=f"https://www.instagram.com/reel/{data.get('code', '')}"
            if reel
            else f"https://www.instagram.com/p/{data.get('code', '')}/",
            taken_at=data.get("taken_at", 0),
            post_id=data.get("pk", ""),
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
