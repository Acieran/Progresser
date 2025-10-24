from abc import ABC, abstractmethod
from core.domain.entities import Task


class TaskRepositoryInterface(ABC):
    """Domain-focused repository for Task operations."""
    
    @abstractmethod
    def create_task(self, task: Task) -> int:
        """Create a new task and return its ID."""
        pass
    
    @abstractmethod
    def get_task_by_id(self, task_id: int) -> Task | None:
        """Get a task by its ID."""
        pass
    
    @abstractmethod
    def get_tasks_by_owner(self, owner_name: str) -> list[Task]:
        """Get all tasks owned by a specific user."""
        pass
    
    @abstractmethod
    def get_child_tasks(self, parent_task_id: int) -> list[Task]:
        """Get all child tasks of a parent task."""
        pass
    
    @abstractmethod
    def update_task(self, task_id: int, task: Task) -> bool:
        """Update an existing task."""
        pass
    
    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID."""
        pass
    
    @abstractmethod
    def task_exists(self, task_id: int) -> bool:
        """Check if a task exists."""
        pass
    
    @abstractmethod
    def user_has_access_to_task(self, task_id: int, username: str) -> bool:
        """Check if user has access to a task."""
        pass
