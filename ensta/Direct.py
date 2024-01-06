import time
import json
import random
import hashlib
import requests
from uuid import uuid4
from requests import Session
from .lib.Exceptions import NetworkError
from .containers.Inbox import Inbox
from .containers.DirectThread import DirectThread
from .containers.DirectThreadInviter import DirectThreadInviter
from json import JSONDecodeError


class Direct:

    session_data: str
    request_session: Session
    insta_app_id: str = "936619743392459"
    user_id: str
    private_user_agent: str = "Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x1920; " \
                              "OnePlus; 6T Dev; devitron; qcom; en_US; 314665256)"

    def __init__(
        self,
        session_data: str,
        proxy: dict[str, str] = None
    ) -> None:

        self.session_data = session_data
        self.request_session = requests.Session()

        if proxy is not None: self.request_session.proxies.update(proxy)

        session_data_json: dict = json.loads(session_data)
        self.user_id = session_data_json.get("user_id")

        self.request_session.cookies.set("sessionid", session_data_json.get("session_id"))
        self.request_session.cookies.set("rur", session_data_json.get("rur"))
        self.request_session.cookies.set("mid", session_data_json.get("mid"))
        self.request_session.cookies.set("ds_user_id", session_data_json.get("user_id"))
        self.request_session.cookies.set("ig_did", session_data_json.get("ig_did"))

    @property
    def __private_headers(self) -> dict:

        try: mid: str = json.loads(self.session_data).get("mid", "")
        except JSONDecodeError: mid: str = ""

        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-Locale": "en_US",
            "X-IG-Device-Locale": "en_US",
            "X-IG-Mapped-Locale": "en_US",
            "X-Pigeon-Session-Id": f"UFS-{uuid4()}-1",
            "X-Pigeon-Rawclienttime": str(round(time.time(), 3)),
            "X-IG-Bandwidth-Speed-KBPS": str(random.randint(2500000, 3000000) / 1000),
            "X-IG-Bandwidth-TotalBytes-B": str(random.randint(5000000, 90000000)),
            "X-IG-Bandwidth-TotalTime-MS": str(random.randint(2000, 9000)),
            "X-IG-App-Startup-Country": "IN",
            "X-Bloks-Version-Id": "ce555e5500576acd8e84a66018f54a05720f2dce29f0bb5a1f97f0c10d6fac48",
            "X-IG-WWW-Claim": "0",
            "X-Bloks-Is-Layout-RTL": "false",
            "X-Bloks-Is-Panorama-Enabled": "true",
            "X-IG-Device-ID": str(uuid4()),
            "X-IG-Family-Device-ID": str(uuid4()),
            "X-IG-Android-ID": f"android-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}",
            "X-IG-Timezone-Offset": "-14400",
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvx0=",
            "X-IG-App-ID": self.insta_app_id,
            "Priority": "u=3",
            "User-Agent": self.private_user_agent,
            "Accept-Language": "en-US",
            "X-MID": mid,
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "X-FB-HTTP-Engine": "Liger",
            "Connection": "keep-alive",
            "X-FB-Client-IP": "True",
            "X-FB-Server-Cluster": "True",
            "IG-INTENDED-USER-ID": self.user_id,
            "X-IG-Nav-Chain": "9MV:self_profile:2,ProfileMediaTabFragment:self_profile:3,9Xf:self_following:4",
            "X-IG-SALT-IDS": str(random.randint(1061162222, 1061262222))
        }

    def inbox(self) -> Inbox:
        """
        Fetches all the chats from inbox.

        :return: Inbox object with chat items and some other data
        """

        # params: json = {
        #     "visual_message_return_type": "unseen",
        #     "thread_message_limit": "10",
        #     "persistentBadging": "true",
        #     "limit": "20",
        #     "is_prefetching": "false",
        #     "fetch_reason": "manual_refresh"
        # }

        http_response = self.request_session.get(
            "https://i.instagram.com/api/v1/direct_v2/inbox/",
            headers=self.__private_headers
        )

        try:
            response_json: dict = http_response.json()

            if response_json.get("status", "") != "ok": raise NetworkError("Key 'status' not 'ok' in response json.")
            if "inbox" not in response_json: raise NetworkError("Key 'inbox' not in response json.")

            inbox_json: dict = response_json.get("inbox", {})

            return Inbox(
                unseen_count=inbox_json.get("unseen_count"),
                unseen_count_timestamp=inbox_json.get("unseen_count_ts"),
                threads=self.__parse_threads(inbox_json.get("threads", list()))
            )

        except JSONDecodeError:
            raise NetworkError("HTTP Response is not a valid JSON.")

    @staticmethod
    def __parse_inviter(data: dict) -> DirectThreadInviter | None:
        if data is None: return None

        return DirectThreadInviter(
            user_id=data.get("pk"),
            username=data.get("username"),
            full_name=data.get("full_name"),
            profile_picture_url=data.get("profile_pic_url"),
            profile_picture_id=data.get("profile_pic_id"),
            is_private=data.get("is_private"),
            is_verified=data.get("is_verified"),
            allowed_commenter_type=data.get("allowed_commenter_type"),
            reel_auto_archive=data.get("reel_auto_archive"),
            has_onboarded_to_text_post_app=data.get("has_onboarded_to_text_post_app"),
            third_party_downloads_enabled=data.get("third_party_downloads_enabled"),
            has_anonymous_profile_picture=data.get("has_anonymous_profile_picture"),
            all_media_count=data.get("all_media_count"),
            liked_clips_count=data.get("liked_clips_count"),
            reachability_status=data.get("reachability_status"),
            has_encrypted_backup=data.get("has_encrypted_backup")
        )

    # @staticmethod
    # def __parse_last_permanent_item(data: dict) -> DirectThreadLastPermanentItem | None:
    #     if data is None: return None
    #
    #     return DirectThreadLastPermanentItem()

    def __parse_threads(self, data: list[dict]) -> list[DirectThread]:

        if len(data) < 1: return list()

        threads: list[DirectThread] = list()

        for item in data:
            theme_data: dict = item.get("theme_data")

            node = DirectThread(
                raw=item,
                thread_title=item.get("thread_title"),
                inviter=self.__parse_inviter(item.get("inviter")),
                # last_permanent_item=self.__parse_last_permanent_item(item.get("last_permanent_item")),
                has_older=item.get("has_older"),
                has_newer=item.get("has_newer"),
                pending=item.get("pending"),
                canonical=item.get("canonical"),
                thread_id=item.get("thread_id"),
                thread_v2_id=item.get("thread_v2_id"),
                viewer_id=item.get("viewer_id"),
                last_activity_at=item.get("last_activity_at"),
                muted=item.get("muted"),
                vc_muted=item.get("vc_muted"),
                approval_required_for_new_members=item.get("approval_required_for_new_members"),
                archived=item.get("archived"),
                thread_has_audio_only_call=item.get("thread_has_audio_only_call"),
                is_group=item.get("is_group"),
                is_translation_enabled=item.get("is_translation_enabled"),
                folder=item.get("folder"),
                e2ee_cutover_status=item.get("e2ee_cutover_status"),
                last_non_sender_item_at=item.get("last_non_sender_item_at"),
                marked_as_unread=item.get("marked_as_unread"),
                input_mode=item.get("input_mode"),
                assigned_admin_id=item.get("assigned_admin_id"),
                mentions_muted=item.get("mentions_muted"),
                is_appointment_booking_enabled=item.get("is_appointment_booking_enabled"),
                is_creator_subscriber_thread=item.get("is_creator_subscriber_thread"),
                business_thread_folder=item.get("business_thread_folder"),
                read_state=item.get("read_state"),
                translation_banner_impression_count=item.get("translation_banner_impression_count"),
                thread_subtype=item.get("thread_subtype"),
                thread_type=item.get("thread_type"),
                is_xac_thread=item.get("is_xac_thread"),
                named=item.get("named"),
                bc_partnership=item.get("bc_partnership"),
                relevancy_score=item.get("relevancy_score"),
                relevancy_score_expr=item.get("relevancy_score_expr"),
                oldest_cursor=item.get("oldest_cursor"),
                newest_cursor=item.get("newest_cursor"),
                next_cursor=item.get("next_cursor"),
                previous_cursor=item.get("prev_cursor"),
                thread_has_drop_in=item.get("thread_has_drop_in"),
                shh_transport_mode=item.get("shh_transport_mode"),
                shh_mode_enabled=item.get("shh_mode_enabled"),
                shh_toggler_userid=item.get("shh_toggler_userid"),
                is_close_friend_thread=item.get("is_close_friend_thread"),
                has_groups_xac_ineligible_user=item.get("has_groups_xac_ineligible_user"),
                system_folder=item.get("system_folder"),
                is_fanclub_subscriber_thread=item.get("is_fanclub_subscriber_thread"),
                joinable_group_link=item.get("joinable_group_link"),
                group_link_joinable_mode=item.get("group_link_joinable_mode"),
                has_reached_message_request_limit=item.get("has_reached_message_request_limit"),
                should_upsell_nudge=item.get("should_upsell_nudge"),
                is_creator_thread=item.get("is_creator_thread"),
                is_business_thread=item.get("is_business_thread"),
                is_sender_possible_business_impersonator=item.get("is_sender_possible_business_impersonator"),
                is_xac_readonly=item.get("is_xac_readonly"),
                will_xac_be_readonly=item.get("will_xac_be_readonly"),
                creator_agent_enabled=item.get("creator_agent_enabled"),
                is_pin=item.get("is_pin"),
                is_spam=item.get("is_spam"),
                spam=item.get("spam"),
                is_3p_api_user=item.get("is_3p_api_user")
            )

            if theme_data is not None:
                node.theme_id = theme_data.get("theme_id")
                node.theme_name = theme_data.get("name")
                node.theme_type = theme_data.get("theme_type")

            threads.append(node)

        return threads
