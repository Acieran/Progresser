from core.application.shared.shared_manager import SharedManager
from core.application.tasks.use_cases.get_child_tasks_use_case import get_child_tasks_use_case
from core.application.tasks.use_cases.get_task_use_case import get_task_use_case
from shared.logging_decorator import log


@log
def calculate_progress(
    task_use_case: SharedManager,
    task_id: int
) -> float:
    task = get_task_use_case(task_use_case=task_use_case, task_id=task_id)
    if task_progress := task_use_case.cache_repo.get_task_progress_cache(task_id=task_id):
        return task_progress
    else:
        children = get_child_tasks_use_case(task_use_case=task_use_case, parent_task_id=task_id, offset=0, limit=1000)
        if children:
            child_progress_sum = 0
            child_all_sum = 0
            for child in children:
                child_progress_sum += calculate_progress(task_id=child.id) * child.weight
                child_all_sum += child.weight
            progress = child_progress_sum / child_all_sum
        else:
            progress = 1 if task.is_complete else 0
        task_use_case.cache_repo.set_task_progress_cache(task_id = task_id, progress = progress)
        return progress