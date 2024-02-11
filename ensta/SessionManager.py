import json
from .Credentials import Credentials


class SessionManager:

    @staticmethod
    def save_to_file(
            file_name: str,
            identifier: str,
            phone_id: str,
            instance: Credentials
    ) -> None:

        session: str = json.dumps(
            {
                "bearer": instance.bearer,
                "user_id": instance.user_id,
                "username": instance.username,
                "identifier": identifier,
                "phone_id": phone_id,
                "device_id": instance.device_id
            }, indent=4)

        with open(file_name, "w") as file: file.write(session)

    @staticmethod
    def load_from_file(file_name: str) -> str:
        with open(file_name, "r") as file: return file.read().strip()
