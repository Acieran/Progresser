from core.application.ports.repositories import BaseRepositoryInterface
from core.application.utilities import dict_to_user, dict_to_task
from core.domain.entities import User, Entities, Task
from shared.logging_decorator import log


@log
def user_check_existence_and_return(
        db_repository: BaseRepositoryInterface,
        bd_model_dict: dict[type[Entities], ...],
        user_id: str,
) -> User | None:
    # Проверка существования пользователя
    user = None
    if user_id:
        user_dict = db_repository.get_by_id(bd_model_dict[User], user_id)
        if user_dict is None:
            db_repository.create(bd_model_dict[User], username=user_id, active=True)
        else:
            user = dict_to_user(**user_dict)
    return user

@log
def task_check_existence_access_and_return(
        db_repository: BaseRepositoryInterface,
        bd_model_dict: dict[type[Entities], ...],
        task_id: int,
        user: User
) -> Task | str:
    task_dict = db_repository.get_by_id(bd_model_dict[Task], task_id)
    if not task_dict:
        return f"Parent task {task_id} not found"
    task = dict_to_task(**task_dict)
    if task.user.username != user.username:
        return "You don't have access to this parent task"
    return task
