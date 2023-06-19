from .Host import Host
from .lib.Exceptions import SessionError
from .Authentication import NewSessionID
import os


class AutoHost(Host):

    username: str | None = None
    password: str | None = None
    save: any = None
    load: any = None
    file: str | None = None

    def __init__(self, username: str, password: str, file: str = None, save: any = None, load: any = None) -> None:

        self.username: str = username
        self.password: str = password
        self.file: str = file
        self.save: any = save
        self.load: any = load

        # Incorrect Arguments
        if self.file is None and (self.save is None or self.load is None):
            raise Exception("Pass either 'file' or 'push_method' and 'pull_method' as an argument.")

        # Load From Method
        if self.save is not None and self.load is not None:
            sessionid: str = load().strip()

            if sessionid != "":
                try: Host(sessionid)
                except SessionError:
                    sessionid: str = self._new_session()

            else: sessionid: str = self._new_session()

            # Initialize Parent Class
            super(AutoHost, self).__init__(sessionid)

        # Load From File
        else:
            if os.path.exists(file):
                with open(file, "r") as file:

                    # Is SessionID Blank?
                    if (sessionid := file.read().strip()) != "":
                        try:
                            Host(sessionid)
                        except SessionError:
                            sessionid: str = self._new_session()

                    # SessionID Is Blank
                    else:
                        sessionid: str = self._new_session()

            # Path Doesn't Exist
            else: sessionid: str = self._new_session()

            # Initialize Parent Class
            super(AutoHost, self).__init__(sessionid)

    def _new_session(self) -> str:
        # Generate New SessionID
        sessionid = NewSessionID(self.username, self.password)

        # Save To Method
        if self.save is not None and self.load is not None:
            self.save(sessionid)

        # Save To File
        else:
            with open(self.file, "w") as file: file.write(sessionid)

        # Return SessionID
        return sessionid
