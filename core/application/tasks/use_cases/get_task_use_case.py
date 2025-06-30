from core.application.shared.shared_manager import SharedManager
from core.application.shared.use_cases.shared_use_cases import user_check_existence_and_return, task_check_existence_access_and_return
from core.domain.entities import Task
from shared.logging_decorator import log


@log
def get_task_use_case(
        task_use_case: SharedManager,
        task_id: int,
        user_id: str | None = None,
) -> Task | None:
    validation_errors = {}

    # Проверка существования пользователя
    user = None
    if user_id:
        user = user_check_existence_and_return(task_use_case=task_use_case, user_id=user_id)
        user = user.username if user else None

    task = None
    if task_id:
        check_task = task_check_existence_access_and_return(
            task_use_case=task_use_case,
            task_id=task_id,
            username=user
        )
        if not isinstance(check_task, Task):
            validation_errors['task_id'] = check_task
        else:
            task = check_task
    return task