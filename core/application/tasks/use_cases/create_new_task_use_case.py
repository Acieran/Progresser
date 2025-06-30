from datetime import datetime

from core.application.shared.shared_manager import SharedManager
from core.application.shared.use_cases.shared_use_cases import task_check_existence_access_and_return, user_check_existence_or_create
from core.domain.entities import Task
from shared.logging_decorator import log

@log
def create_new_task_use_case(
        self: SharedManager,
        user_id: str,
        title: str,
        description: str = None,
        due_date: datetime = None,
        priority: int = None,
        parent_task_id: int = None,
        **kwargs,
) -> dict[str, ...]:
    """
    Создает новую задачу с валидацией и сохранением в БД
    Возвращает словарь с результатом операции

    :param self: модуль работы с базой use_case Task
    :param user_id: Объект пользователя
    :param title: Название задачи (обязательное)
    :param description: Описание задачи
    :param due_date: Срок выполнения
    :param priority: Приоритет (1-3)
    :param parent_task_id: ID родительской задачи
    :return: Словарь с результатом
    """
    # Валидация обязательных полей
    validation_errors = {}

    if not title or len(title.strip()) < 3:
        validation_errors['title'] = "Title must be at least 3 characters"

    if priority and (1 > priority or priority > 5):
        validation_errors['priority'] = "Priority must be between 1 and 5 inclusive"

    if due_date and due_date < datetime.now():
        validation_errors['due_date'] = "Due date cannot be in the past"

    # Проверка существования пользователя
    user = user_check_existence_or_create(shared_manager=self, user_id=user_id)
    if user is None:
        validation_errors['user'] = "User does not exist"

    # Проверка существования родительской задачи
    if parent_task_id:
        check_task = task_check_existence_access_and_return(task_use_case=self, task_id=parent_task_id, username=user_id)
        if not isinstance(check_task, Task):
            validation_errors['parent_task_id'] = check_task

    if validation_errors:
        return {
            'status': 'validation_error',
            'errors': validation_errors,
            'id': None
        }

    # Создание объекта задачи
    new_task = Task(
        owner_name=user_id,
        title=title.strip(),
        description=description.strip() if description else None,
        due_date=due_date,
        priority=priority,
        parent_task_id=parent_task_id,
        is_complete=False,
        weight=1,
    )

    # Сохранение в БД
    try:
        for key in new_task.__annotations__.keys():
            if new_task.__getattribute__(key) is None:
                new_task.__delattr__(key)
        new_id = self.db_repository.create(self.db_model_dict[Task], **new_task.__dict__)
        if new_task.parent_task_id is not None:
            self.cache_repo.drop_task_progress_cache(new_task.parent_task_id)

        return {
            'status': 'success',
            'id': new_id,
            'message': f"Task '{new_task.title}' created successfully"
        }

    except Exception as e:
        # Логирование ошибки
        return {
            'status': 'error',
            'errors': {'database': f"Database error: {str(e)}"},
            'id': None
        }