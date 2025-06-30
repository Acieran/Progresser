from core.application.shared.shared_manager import SharedManager
from core.application.shared.use_cases.shared_use_cases import task_check_existence_access_and_return
from core.domain.entities import Task
from shared.logging_decorator import log


@log
def delete_task_use_case(
        self: SharedManager,
        task_id: int,
        user_id: str = None,
        **kwargs
):
    # Валидация обязательных полей
    validation_errors = {}

    # Проверка существования задачи
    check_task = task_check_existence_access_and_return(self, task_id, user_id)
    if not isinstance(check_task, Task):
        validation_errors['task_id'] = check_task
    else:
        task = check_task

    if validation_errors:
        return {
            'status': 'error',
            'errors': validation_errors,
            'task': None
        }
    else:
        try:
            self.db_repository.delete(self.db_model_dict[Task], task.id)
            if task.parent_task_id is not None:
                self.cache_repo.drop_task_progress_cache(task.parent_task_id)

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