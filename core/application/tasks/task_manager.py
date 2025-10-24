from core.application.ports.caching import CacheInterface
from core.application.ports.repositories_interface import BaseRepositoryInterface
from core.application.shared.shared_manager import SharedManager
from core.application.tasks.use_cases.delete_task_use_case import delete_task_use_case
from core.application.tasks.use_cases.calculate_progress import calculate_progress
from core.application.tasks.use_cases.create_new_task_use_case import create_new_task_use_case
from core.application.tasks.use_cases.get_task_use_case import get_task_use_case
from core.application.tasks.use_cases.get_child_tasks_use_case import get_child_tasks_use_case
from core.application.tasks.use_cases.update_task_use_case import update_task_use_case
from core.domain.entities import Entities


class TaskManager(SharedManager):
    delete_task_use_case = delete_task_use_case
    calculate_progress = calculate_progress
    create_new_task_use_case = create_new_task_use_case
    get_task_use_case = get_task_use_case
    get_child_tasks_use_case = get_child_tasks_use_case
    update_task_use_case = update_task_use_case

    def __init__(self, db_repository: BaseRepositoryInterface, db_model_dict: dict[type[Entities], ...],
                 cache_repo: CacheInterface):
        super().__init__(db_repository, db_model_dict, cache_repo)