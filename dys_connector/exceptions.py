
class DysHttpException(Exception):
    """
    Dys Base Http Exception
    Attributes:
        status_code -- Http status code
        message -- explanation of the error
    """
    def __init__(self, status_code, message="Dys Http Exception"):
        self.status_code = status_code
        self.message = f"{message}, status code {status_code}!"
        super().__init__(self.message)


class DysBadRequestError(DysHttpException):
    """Raised when Dys Http Bad request occurs with error code 400"""
    def __init__(self, message="Dys Bad Request Error!"):
        self.status_code = 400
        self.message = message
        super().__init__(status_code=self.status_code, message=message)


class DysUnauthorizedError(DysHttpException):
    """Raised when Dys Http unauthorized error occurs with error code 401"""
    def __init__(self, message="Dys Unauthorized Error!"):
        self.status_code = 401
        self.message = message
        super().__init__(status_code=self.status_code, message=message)


class DysInternalServerError(DysHttpException):
    """Raised when Dys Internal Server Error occurs with error code 500"""
    def __init__(self, message="Dys Internal Server Error!"):
        self.status_code = 500
        self.message = message
        super().__init__(status_code=self.status_code, message=message)


class DysBadGatewayError(DysHttpException):
    """Raised when Dys Bad Gateway Error occurs with error code 502"""
    def __init__(self, message="Dys Bad Gateway Error!"):
        self.status_code = 502
        self.message = message
        super().__init__(status_code=self.status_code, message=message)


class DysServiceTemporarilyUnavailable(DysHttpException):
    """Raised when Dys Service Temporarily Unavailable occurs with error code 503"""
    def __init__(self, message="Dys Service Temporarily Unavailable!"):
        self.status_code = 503
        self.message = message
        super().__init__(status_code=self.status_code, message=message)


class DysClearDirectoryItemDeleteException(DysHttpException):
    """Raised when Dys Internal Server Error occurs with error code 500"""
    def __init__(self, message="Clear Directory Item Delete Exception"):
        self.status_code = 500
        self.message = message
        super().__init__(status_code=self.status_code, message=message)

