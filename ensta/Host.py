from .BaseHost import BaseHost
from .lib.Exceptions import SessionError
from .Authentication import NewSessionID
import os


# noinspection PyMissingConstructor
class Host(BaseHost):

    DEFAULT_FILE: str = "ensta-session.txt"

    username: str = None
    password: str = None

    save: any = None
    load: any = None
    file: str | None = None

    proxy: dict[str, str] = None

    def __init__(self, username: str, password: str, file: str = None, save: any = None,
                 load: any = None, proxy: dict[str, str] = None) -> None:

        self.username: str = username
        self.password: str = password
        self.file: str = file
        self.save: any = save
        self.load: any = load
        self.proxy: dict[str, str] = proxy

        if self.file is None and self.load is None: self.file: str = self.DEFAULT_FILE
        self.load_session()

    def load_session(self, sid: str = None) -> any:
        if self.file is None and self.load is None and sid is None:
            raise Exception("Neither Load Function nor File Name was passed to load SessionId.")

        if sid:
            try: super().__init__(sid, self.proxy)
            except SessionError: return self.new_session()

        elif self.load:
            session_id: str = self.load().strip()

            if session_id == "": return self.new_session()
            else:
                try: super().__init__(session_id, self.proxy)
                except SessionError: return self.new_session()

        elif self.file:
            if not os.path.exists(self.file): return self.new_session()

            with open(self.file, "r") as reading:
                if (session_id := reading.read().strip()) == "": return self.new_session()
                else:
                    try: super().__init__(session_id, self.proxy)
                    except SessionError: return self.new_session()

    def new_session(self) -> None:
        session_id: str = NewSessionID(self.username, self.password, self.proxy)
        if self.save: self.save(session_id)

        if self.file:
            with open(self.file, "w") as writing: writing.write(session_id)

        self.load_session(session_id)
