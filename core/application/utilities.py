from core.domain.entities import Task, User


def dict_to_task(**kwargs) -> Task:
    approved = {}
    for key, value in kwargs.items():
        if hasattr(Task, key):
            approved[key] = value
    return Task(**approved)

def dict_to_user(**kwargs) -> User:
    approved = {}
    for key, value in kwargs.items():
        if hasattr(User, key):
            approved[key] = value
    return User(**approved)