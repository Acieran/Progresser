from sqlalchemy.exc import SQLAlchemyError

from core.application.shared.shared_manager import SharedManager
from core.application.utilities import dict_to_user, dict_to_task
from core.domain.entities import User, Task
from shared.logging_decorator import log


@log
def user_check_existence_or_create(
        shared_manager: SharedManager,
        user_id: str,
) -> User:
    try:
        # Проверка существования пользователя
        user = None
        if user_id:
            user_dict = shared_manager.db_repository.get_by_id(shared_manager.db_model_dict[User], user_id)
            if user_dict is None:
                shared_manager.db_repository.create(shared_manager.db_model_dict[User], username=user_id, active=True, telegram_username=user_id)
                user_dict = shared_manager.db_repository.get_by_id(shared_manager.db_model_dict[User], user_id)
            user = dict_to_user(**user_dict)
        return user
    except SQLAlchemyError as e:
        raise e

@log
def user_check_existence_and_return(
        task_use_case: SharedManager,
        user_id: str,
) -> User | None:
    user = task_use_case.db_repository.get_by_id(task_use_case.db_model_dict[User], user_id)
    if user:
        user = dict_to_user(**user)
    return user


@log
def task_check_existence_access_and_return(
        task_use_case: SharedManager,
        task_id: int,
        username: str | None = None,
) -> Task | str:
    task_dict = task_use_case.db_repository.get_by_id(task_use_case.db_model_dict[Task], task_id)
    if not task_dict:
        return f"Parent task {task_id} not found"
    task = dict_to_task(**task_dict)
    if username and task.owner_name != username:
        return "You don't have access to this parent task"
    return task
