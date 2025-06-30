from http import HTTPStatus
from shared.logging_decorator import logger

class BaseCustomError(Exception):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None, error_code: int = None):
        super().__init__(error_message)
        self.error_message = error_message
        self.error_code = error_code
        self.state = state
        self.command = command
        self.username = username

class CustomError(BaseCustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None, error_code: int = None):
        super().__init__(error_message, username, state, command, error_code)
        logger.error(error_message, username, state, command, error_code)

class InternalRedisError(CustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message, username, state, command, HTTPStatus.INTERNAL_SERVER_ERROR)

class InternalCreationError(CustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message, username, state, command, HTTPStatus.INTERNAL_SERVER_ERROR)


class BusinessError(BaseCustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None, error_code: int = None):
        super().__init__(error_message, username, state, command, error_code)
        logger.warning(error_message, username, state, command, error_code)

class BusinessCreationError(BusinessError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message, username, state, command)

class WrongTransitionError(BusinessError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message, username, state, command, HTTPStatus.BAD_GATEWAY)

class EntityNotFoundError(BusinessError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message, username, state, command, HTTPStatus.NOT_FOUND)