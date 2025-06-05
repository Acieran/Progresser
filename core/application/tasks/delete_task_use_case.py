from core.application.ports.repositories import BaseRepositoryInterface
from core.application.tasks.shared import user_check_existence_and_return, task_check_existence_access_and_return
from core.domain.entities import Entities, Task
from shared.logging_decorator import log


@log
def delete_task_use_case(
        db_repository: BaseRepositoryInterface,
        bd_model_dict: dict[type[Entities], ...],
        user_id: str,
        task_id: int
):
    # Валидация обязательных полей
    validation_errors = {}

    # Проверка существования пользователя
    user = user_check_existence_and_return(db_repository, bd_model_dict, user_id)

    # Проверка существования задачи
    task = None
    if task_id:
        check_task = task_check_existence_access_and_return(db_repository, bd_model_dict, task_id, user)
        if not isinstance(check_task, Task):
            validation_errors['task_id'] = check_task
        else:
            task = check_task
    else:
        validation_errors['task_id'] = f"Task id is required to perform this operation"

    if validation_errors:
        return {
            'status': 'error',
            'errors': validation_errors,
            'task': None
        }
    else:
        try:
            db_repository.delete(bd_model_dict[Task], task.id)

            return {
                'status': 'success',
                'message': f"Task '{task.title}' deleted successfully"
            }
        except Exception as e:
            # Логирование ошибки
            return {
                'status': 'error',
                'errors': {'database': f"Database error: {str(e)}"},
                'task': None
            }