from datetime import datetime

from core.application.ports.repositories import BaseRepositoryInterface
from core.application.utilities import dict_to_task, dict_to_user
from core.domain.entities import Entities, Task, User


def create_new_task_use_case(
        db_repository: BaseRepositoryInterface,
        bd_model_dict: dict[type[Entities], ...],
        user_id: str,
        title: str,
        description: str = None,
        due_date: datetime = None,
        priority: int = None,
        parent_task_id: int = None,
        **kwargs
) -> dict[str, ...]:
    """
    Создает новую задачу с валидацией и сохранением в БД
    Возвращает словарь с результатом операции

    :param db_repository: модуль работы с базой данных
    :param bd_model_dict: Словарь конвертации объектов из enitities в BD models
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

    if priority is not None and (priority < 1 or priority > 3):
        validation_errors['priority'] = "Priority must be between 1 and 3"

    if due_date and due_date < datetime.now():
        validation_errors['due_date'] = "Due date cannot be in the past"

    # Проверка существования пользователя
    user = User(username=user_id, active=True)
    if user_id:
        user_dict = db_repository.get_by_id(bd_model_dict[Task], user_id)
        if not user_dict:
            db_repository.create(bd_model_dict[User], username=user_id, active=True)
        else:
            user = dict_to_user(**user_dict)

    # Проверка существования родительской задачи
    if parent_task_id:
        parent_task_dict = db_repository.get_by_id(bd_model_dict[Task], parent_task_id)
        if not parent_task_dict:
            validation_errors['parent_task_id'] = f"Parent task {parent_task_id} not found"
        parent_task = dict_to_task(**parent_task_dict)
        if parent_task.user.username != user.username:
            validation_errors['parent_task_id'] = "You don't have access to this parent task"

    if validation_errors:
        return {
            'status': 'error',
            'errors': validation_errors,
            'task': None
        }

    # Создание объекта задачи
    new_task = Task(
        user=user,
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
        db_repository.create(bd_model_dict[Task], **new_task.__dict__)

        # # Обновление родительской задачи если нужно
        # if parent_task_id:
        #     db_repository.update(bd_model_dict[Task], parent_task_id, saved_task.id)

        return {
            'status': 'success',
            'task': new_task,
            'message': f"Task '{new_task.title}' created successfully"
        }

    except Exception as e:
        # Логирование ошибки
        return {
            'status': 'error',
            'errors': {'database': f"Database error: {str(e)}"},
            'task': None
        }