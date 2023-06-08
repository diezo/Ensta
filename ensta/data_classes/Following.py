class FollowingInternal:

    has_anonymous_profile_picture: bool = False
    user_id: str = ""
    username: str = ""
    full_name: str = ""
    is_private: bool = False
    is_verified: bool = False
    profile_picture_url: str = ""
    is_possible_scammer: bool = False


class Following:

    has_anonymous_profile_picture: bool = False
    user_id: str = ""
    username: str = ""
    full_name: str = ""
    is_private: bool = False
    is_verified: bool = False
    profile_picture_url: str = ""
    is_possible_scammer: bool = False

    def __init__(self, obj: FollowingInternal):
        self.has_anonymous_profile_picture = obj.has_anonymous_profile_picture
        self.user_id = obj.user_id
        self.username = obj.username
        self.full_name = obj.full_name
        self.is_private = obj.is_private
        self.is_verified = obj.is_verified
        self.profile_picture_url = obj.profile_picture_url
        self.is_possible_scammer = obj.is_possible_scammer
