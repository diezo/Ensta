class AuthenticationError(Exception):

    def __init__(self, message):
        super().__init__(message)


class NetworkError(Exception):

    def __init__(self, message):
        super().__init__(message)


class IdentifierError(Exception):

    def __init__(self, message):
        super().__init__(message)


class CodeError(Exception):

    def __init__(self, location: str = "Unknown"):
        super().__init__(f"There was an error while executing this function, maybe caused due to a bug in the code. Please submit this as an issue on GitHub.\nFound in: {location}")
