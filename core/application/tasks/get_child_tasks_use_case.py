from core.application.ports.repositories import BaseRepositoryInterface
from core.application.tasks.shared import user_check_existence_and_return, task_check_existence_access_and_return
from core.domain.entities import Entities, Task
from shared.logging_decorator import log


@log
def get_child_tasks_use_case(
        db_repository: BaseRepositoryInterface,
        bd_model_dict: dict[type[Entities], ...],
        user_id: str,
        parent_task_id: int,
) -> list[dict]:
    validation_errors = {}

    # Проверка существования пользователя
    user = user_check_existence_and_return(db_repository, bd_model_dict, user_id)

    result = None
    if parent_task_id:
        check_task = task_check_existence_access_and_return(db_repository, bd_model_dict, parent_task_id, user)
        if not isinstance(check_task, Task):
            validation_errors['task_id'] = check_task
        else:
            result = db_repository.get_by_custom_fields(bd_model_dict[Task],parent_id=parent_task_id)
    return result