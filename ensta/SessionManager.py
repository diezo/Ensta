import hashlib
import json
import os
from json import JSONDecodeError


class SessionManager:
    """
    SessionManager is smart. It takes username-password and decides where to store the session.
    It also checks for password changes. If so, ignores the old session.
    """

    @staticmethod
    def save_to_file(
            folder_name: str,
            identifier: str,
            password: str,
            phone_id: str,
            instance: any
    ) -> None:

        # Calculate Hashes
        identifier_hash: str = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
        password_hash: str = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Create 'Sessions' Folder If It Doesn't Exist
        SessionManager.create_folder(folder_name)

        # Write Session To File
        with open(f"{folder_name}/{identifier_hash}.json", "w", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    {
                        "bearer": instance.bearer,
                        "user_id": instance.user_id,
                        "username": instance.username,
                        "password_hash": password_hash,
                        "identifier": identifier,
                        "phone_id": phone_id,
                        "device_id": instance.device_id
                    }, indent=4
                )
            )

    @staticmethod
    def load_from_file(
            identifier: str,
            password: str,
            folder_name: str
    ) -> dict:

        # Calculate Hashes
        identifier_hash: str = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
        password_hash: str = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Path To Session File
        session_path: str = f"{folder_name}/{identifier_hash}.json"

        # 'Session' File Doesn't Exist?
        if not os.path.exists(session_path): return dict()

        # Read Session Data: JSON
        with open(session_path, "r") as file:
            try: content: dict = json.loads(file.read().strip())
            except JSONDecodeError: return dict()

        # Password Hash Matches?
        """
        If password hashes don't match, it means that the user has changed the password
        for some reason, and the library must log in again with the new password instead
        of just using the old session.

        Hope the explanation was good enough :)
        """
        if content.get("password_hash", "") != password_hash: return dict()

        # Return Session Data: It's in Good Condition!
        return content

    @staticmethod
    def create_folder(name: str):
        if not os.path.exists(name) or not os.path.isdir(name): os.mkdir(name)
