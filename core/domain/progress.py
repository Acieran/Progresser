from core.domain.entities import Task


def calculate_progress(task: Task) -> float:
    if not task.children_tasks:
        return 100.0 if task.is_complete else 0.0
    completed = sum(calculate_progress(child) for child in task.children_tasks)
    return completed / len(task.children_tasks)