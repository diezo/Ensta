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
        super().__init__(f"There was some problem when executing this method. This was caused due to a bug in the code. Please contact the developer of submit this as an issue.\nFound in: {location}")
