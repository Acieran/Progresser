from datetime import datetime

from core.application.shared.shared_manager import SharedManager
from core.application.tasks.use_cases.get_task_use_case import get_task_use_case
from core.application.shared.use_cases.shared_use_cases import task_check_existence_access_and_return, user_check_existence_and_return
from core.domain.entities import Task
from shared.logging_decorator import log

@log
def update_task_use_case(
        self: SharedManager,
        task_id: int,
        user_id: str = None,
        **kwargs,
) -> dict[str, ...]:
    """
    Создает новую задачу с валидацией и сохранением в БД.
    Возвращает словарь с результатом операции

    :param self: модуль работы с базой use_case Task
    :param task_id: id Задачи, которую требуется изменить
    :param user_id: Объект пользователя
    :return: Словарь с результатом
    """
    # Валидация обязательных полей
    validation_errors = {}

    # Проверка существования пользователя
    user = user_check_existence_and_return(task_use_case=self, user_id=user_id)
    if user is None:
        validation_errors['user'] = "User does not exist"

    for key, value in kwargs.items():
        if key == "title" and value is not None and len(value.strip()) < 3:
            validation_errors['title'] = "Title must be at least 3 characters"

        if key == "priority" and value is not None and (1 > value or value > 5):
            validation_errors['priority'] = "Priority must be between 1 and 5 inclusive"

        if key == "due_date" and value is not None and value < datetime.now():
            validation_errors['due_date'] = "Due date cannot be in the past"

        # Проверка существования родительской задачи
        if key == "parent_task_id" and value is not None:
            check_task = task_check_existence_access_and_return(task_use_case=self, task_id=value,
                                                                username=user_id)
            if not isinstance(check_task, Task):
                validation_errors['parent_task_id'] = check_task

    try:
        with self.db_repository.transaction():
            task = get_task_use_case(task_use_case=self, task_id=task_id)
            if not task:
                validation_errors['task'] = "Task does not exist"

            for key, value in kwargs.items():
                setattr(task, key, value)

            if validation_errors:
                return {
                    'status': 'validation_error',
                    'errors': validation_errors,
                }

            result = self.db_repository.update(self.db_model_dict[Task], task_id, **task.__dict__)
            if task.parent_task_id is not None:
                self.cache_repo.drop_task_progress_cache(task.parent_task_id)

            return {
                'status': 'success' if result else 'failure',
                'message': f"Task '{task.title}' {'updated successfully' if result else 'update failed'}",
            }

    except Exception as e:
        # Логирование ошибки
        return {
            'status': 'error',
            'errors': {'database': f"Database error: {str(e)}"},
        }


