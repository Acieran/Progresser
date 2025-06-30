from core.application.shared.shared_manager import SharedManager
from core.application.shared.use_cases.shared_use_cases import user_check_existence_and_return
from core.domain.entities import Task
from shared.logging_decorator import log


@log
def get_child_tasks_use_case(
        task_use_case: SharedManager,
        parent_task_id: int | None,
        user_id: str | None = None,
        offset: int = 0,
        limit: int = 10,
) -> list[Task]:
    # validation_errors = {}

    # Проверка существования пользователя
    if user_id:
        user_check_existence_and_return(task_use_case=task_use_case, user_id=user_id)

    # result = None
    # check_task = task_check_existence_access_and_return(shared_manager.db_repository, shared_manager.db_model_dict, parent_task_id, user_id)
    # if not isinstance(check_task, Task):
    #     validation_errors['task_id'] = check_task
    # else:
    result = task_use_case.db_repository.get_by_custom_fields(
        model=task_use_case.db_model_dict[Task],
        parent_task_id=parent_task_id,
        offset=offset,
        limit=limit,
    )
    task_list: list[Task] = []
    for item in result:
        task_list.append(Task(**item))
    result = task_list
    return result

