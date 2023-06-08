from dataclasses import dataclass, field
from ..containers import Profile


@dataclass(frozen=True)
class ProfileResponse:

    success: bool = False,
    user: Profile = field(default=Profile)
