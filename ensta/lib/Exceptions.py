class SessionError(Exception):

    def __init__(self, message):
        super().__init__(message)


class NetworkError(Exception):

    def __init__(self, message):
        super().__init__(message)


class IdentifierError(Exception):

    def __init__(self, message):
        super().__init__(message)


class DevelopmentError(Exception):

    def __init__(self):
        super().__init__(
            f"There was an error while executing this function, maybe caused due to a bug in the "
            "code. Please raise an issue on GitHub"
        )


class AuthenticationError(Exception):

    def __init__(self, message):
        super().__init__(message)


class APIError(Exception):

    def __init__(self, message: str | None = None):
        if message is not None:
            super().__init__(
                "Looks like Instagram has made changes to the API Response."
                "Please raise this as an issue on GitHub."
            )
        else:
            super().__init__(message)


class ConversionError(Exception):

    def __init__(self, message):
        super().__init__(message)


class FileTypeError(Exception):

    def __init__(self, message):
        super().__init__(message)


class RateLimitedError(Exception):

    def __init__(self, message):
        super().__init__(message)
