from core.domain.entities import Task, User
from shared.logging_decorator import log


@log
def dict_to_task(**kwargs) -> Task:
    approved = {}
    for key, value in kwargs.items():
        if key in Task.__annotations__.keys():
            approved[key] = value
    return Task(**approved)

@log
def dict_to_user(**kwargs) -> User:
    approved = {}
    for key, value in kwargs.items():
        if key in User.__annotations__.keys():
            approved[key] = value
    return User(**approved)