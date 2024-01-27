from typing import Any, List
from .BaseRespondeData import BaseRespondeData
from dataclasses import dataclass


@dataclass(frozen=True)
class CommentInformTreatment(BaseRespondeData):
    should_have_inform_treatment: bool
    text: str
    url: Any  # @TODO
    action_type: Any  # @TODO

@dataclass(frozen=True)
class SharingFrictionInfo(BaseRespondeData):
    should_have_sharing_friction: bool
    bloks_app_url: Any  # @TODO
    sharing_friction_payload: Any  # @TODO
