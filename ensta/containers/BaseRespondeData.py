

from typing import Self
from dataclasses import fields, is_dataclass


class BaseRespondeData:

    @classmethod
    def from_data(cls, data):
        parsed_data = {}
        for field in fields(cls):
            raw_value = data.get(field.name, None)
            if raw_value is None:
                parsed_data[field.name] = None
            elif not isinstance(field.type, type):
                parsed_data[field.name] = raw_value
            elif issubclass(field.type, BaseRespondeData):
                value = field.type.from_data(raw_value)
                parsed_data[field.name] = value
            elif is_dataclass(field.type):
                value = field.type(**raw_value)
                parsed_data[field.name] = value
            else:
                parsed_data[field.name] = raw_value

        return cls(**parsed_data)

    @classmethod
    def from_response_data(cls, response_data: dict) -> 'Self':
        success = response_data.get("status", "") == "ok"
        if not success:
            raise Exception("Response status is not ok")
        data = response_data.get("media", False)
        if not data:
            raise Exception("There is no media in response")
        return cls.from_data(data)
