from .PostUser import PostUser
from .Liker import Liker
from .Likers import Likers
from dataclasses import dataclass, field
from ensta.lib.Commons import refresh_csrf_token
from json import JSONDecodeError


@dataclass(frozen=False)
class Post:
    instance: any = None
    share_url: str = ""
    taken_at: int = 0
    unique_key: str = ""
    media_type: int = 0
    code: str = ""
    caption_is_edited: bool = False
    original_media_has_visual_reply_media: bool = False
    like_and_view_counts_disabled: bool = False
    can_viewer_save: bool = False
    profile_grid_control_enabled: bool = False
    is_comments_gif_composer_enabled: bool = False
    comment_threading_enabled: bool = False
    comment_count: int = 0
    has_liked: bool = False
    user: PostUser = field(default_factory=PostUser)
    can_viewer_reshare: bool = False
    like_count: int = 0
    top_likers: list[str] = field(default_factory=list)
    caption_text: str = ""
    is_caption_covered: bool = False
    caption_created_at: int = 0
    caption_share_enabled: bool = False
    caption_did_report_as_spam: bool = False
    is_paid_partnership: bool = False
    show_shop_entrypoint: bool = False
    deleted_reason: int = 0
    integrity_review_decision: str = ""
    ig_media_sharing_disabled: bool = False
    has_shared_to_fb: int = 0
    is_unified_video: bool = False
    should_request_ads: bool = False
    is_visual_reply_commenter_notice_enabled: bool = False
    commerciality_status: str = ""
    explore_hide_comments: bool = False
    has_delayed_metadata: bool = False
    location_latitude: float = 0
    location_longitude: float = 0

    def _like_action(self, action: str = "like") -> bool:
        if self.unique_key == "": return False

        refresh_csrf_token(self.instance)
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-prefers-color-scheme": self.instance.preferred_color_scheme,
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
            "x-csrftoken": self.instance.csrf_token,
            "x-ig-app-id": self.instance.insta_app_id,
            "x-ig-www-claim": self.instance.x_ig_www_claim,
            "x-instagram-ajax": "1007670408",
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/p/{self.code}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.instance.request_session.post(f"https://www.instagram.com/api/v1/web/likes/{self.unique_key}/{action}/", headers=request_headers)
            response_json = http_response.json()

            if "status" in response_json:
                return response_json["status"] == "ok"
            else:
                return False
        except JSONDecodeError:
            return False

    def like(self) -> bool:
        return self._like_action("like")

    def unlike(self) -> bool:
        return self._like_action("unlike")
    
    def likers(self) -> Likers | None:
        refresh_csrf_token(self.instance)
        request_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-prefers-color-scheme": self.instance.preferred_color_scheme,
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-full-version-list": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.134\", \"Google Chrome\";v=\"114.0.5735.134\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.instance.csrf_token,
            "x-ig-app-id": self.instance.insta_app_id,
            "x-ig-www-claim": self.instance.x_ig_www_claim,
            "x-requested-with": "XMLHttpRequest",
            "Referer": f"https://www.instagram.com/p/{self.code}/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        try:
            http_response = self.instance.request_session.get(f"https://www.instagram.com/api/v1/media/{self.unique_key}/likers/", headers=request_headers)
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
