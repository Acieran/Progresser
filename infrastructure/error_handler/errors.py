from http import HTTPStatus
from shared.logging_decorator import logger


class CustomError(Exception):
    def __init__(self, error_message: str):
        super().__init__(error_message)
        self.error_message = error_message

class WrongTransitionError(CustomError):
    def __init__(self, error_message: str, username: str, state: str, command: str, ):
        super().__init__(error_message)
        self.error_code = HTTPStatus.BAD_GATEWAY
        self.state = state
        self.command = command
        self.username = username
        logger.warning(self.error_message, username, state, command)

class InternalRedisError(CustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message)
        self.error_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.state = state
        self.command = command
        self.username = username
        logger.error(self.error_message, username, state, command)

class InternalCreationError(CustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message)
        self.error_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.state = state
        self.command = command
        self.username = username
        logger.error(self.error_message, username, state, command)

class EntityNotFoundError(CustomError):
    def __init__(self, error_message: str, username: str = None, state: str = None, command: str = None):
        super().__init__(error_message)
        self.error_code = HTTPStatus.NOT_FOUND
        self.state = state
        self.command = command
        self.username = username
        logger.warning(self.error_message, username, state, command)