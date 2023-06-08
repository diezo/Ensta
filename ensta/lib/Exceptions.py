class AuthenticationError(Exception):

    def __init__(self, message):
        super().__init__(message)


class NetworkError(Exception):

    def __init__(self, message):
        super().__init__(message)


class IdentifierTypeError(Exception):

    def __init__(self, message):
        super().__init__(message)
