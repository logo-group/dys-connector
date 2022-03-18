
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
