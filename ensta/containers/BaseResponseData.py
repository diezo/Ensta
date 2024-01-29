from dataclasses import fields, is_dataclass


class BaseResponseData:

    @classmethod
    def from_data(cls, data):
        parsed_data = {}
        
        for field in fields(cls):
            raw_value = data.get(field.name, None)
            
            if raw_value is None:
                parsed_data[field.name] = None
                
            elif not isinstance(field.type, type):
                parsed_data[field.name] = raw_value
                
            elif issubclass(field.type, BaseResponseData):
                value = field.type.from_data(raw_value)
                parsed_data[field.name] = value
                
            elif is_dataclass(field.type):
                value = field.type(**raw_value)
                parsed_data[field.name] = value
                
            else:
                parsed_data[field.name] = raw_value

        return cls(**parsed_data)

    @classmethod
    def from_response_data(cls, response_data: dict):
        if response_data.get("status", "") != "ok":
            raise Exception(
                "Key 'status' not 'ok' in response JSON. "
                "Please check the images or videos you supplied."
            )
            
        data = response_data.get("media")
        
        if data is None: raise Exception(
            "Either Instagram's Internal Server Error or this library needs to be updated."
        )

        return cls.from_data(data)
