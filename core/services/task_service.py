from datetime import datetime
from typing import Optional

from core.application.ports.repositories_interface.task_repository_interface import TaskRepositoryInterface
from core.application.ports.repositories_interface.user_repository_interface import UserRepositoryInterface
from core.application.ports.caching import CacheInterface
from core.domain.entities import Task


class TaskService:
    """Service for task operations - handles validation and orchestration."""
    
    def __init__(
        self,
        task_repository: TaskRepositoryInterface,
        user_repository: UserRepositoryInterface,
        cache_repo: CacheInterface
    ):
        self.task_repository = task_repository
        self.user_repository = user_repository
        self.cache_repo = cache_repo
    
    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[int] = None,
        parent_task_id: Optional[int] = None,
        **kwargs
    ) -> Task:
        """
        Create a new task with validation.
        
        Args:
            user_id: Username of the task owner
            title: Task title (required, min 3 characters)
            description: Optional task description
            due_date: Optional due date (cannot be in the past)
            priority: Optional priority (1-5)
            parent_task_id: Optional parent task ID
            **kwargs: Additional task attributes
            
        Returns:
            Task: The created task entity
            
        Raises:
            ValueError: If validation fails
            PermissionError: If user doesn't have access to parent task
        """
        # Input validation
        self._validate_create_task_input(title, priority, due_date)
        
        # Ensure user exists (create if needed)
        user = self.user_repository.get_or_create_user(user_id, telegram_username=user_id)
        
        # Validate parent task if specified
        if parent_task_id:
            self._validate_parent_task(parent_task_id, user_id)
        
        # Create task entity
        task = Task(
            owner_name=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            due_date=due_date,
            priority=priority,
            parent_task_id=parent_task_id,
            is_complete=False,
            weight=1,
            **kwargs
        )
        
        # Save to database
        task_id = self.task_repository.create_task(task)
        task.id = task_id
        
        # Invalidate parent task progress cache if needed
        if parent_task_id:
            self.cache_repo.drop_task_progress_cache(parent_task_id)
        
        return task
    
    def _validate_create_task_input(
        self,
        title: str,
        priority: Optional[int],
        due_date: Optional[datetime]
    ) -> None:
        """Validate input parameters for task creation."""
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters")
        
        if priority is not None and not (1 <= priority <= 5):
            raise ValueError("Priority must be between 1 and 5 inclusive")
        
        if due_date and due_date < datetime.now():
            raise ValueError("Due date cannot be in the past")
    
    def _validate_parent_task(self, parent_task_id: int, user_id: str) -> None:
        """Validate that parent task exists and user has access."""
        if not self.task_repository.task_exists(parent_task_id):
            raise ValueError(f"Parent task {parent_task_id} not found")
        
        if not self.task_repository.user_has_access_to_task(parent_task_id, user_id):
            raise PermissionError("You don't have access to this parent task")
    
    def get_task(self, task_id: int, user_id: str) -> Task:
        """Get a task with permission check."""
        task = self.task_repository.get_task_by_id(task_id)
        if not task:
            raise ValueError("Task not found")
        
        if not self.task_repository.user_has_access_to_task(task_id, user_id):
            raise PermissionError("You don't have access to this task")
        
        return task
    
    def delete_task(self, task_id: int, user_id: str) -> bool:
        """Delete a task with permission check."""
        task = self.get_task(task_id, user_id)  # This includes permission check
        
        success = self.task_repository.delete_task(task_id)
        
        # Invalidate parent task progress cache if needed
        if success and task.parent_task_id:
            self.cache_repo.drop_task_progress_cache(task.parent_task_id)
        
        return success
    
    def update_task(self, task_id: int, user_id: str, **updates) -> Task:
        """Update a task with validation and permission check."""
        task = self.get_task(task_id, user_id)  # This includes permission check
        
        # Validate updates
        self._validate_update_task_input(updates)
        
        # Validate parent task if being changed
        if 'parent_task_id' in updates and updates['parent_task_id'] is not None:
            self._validate_parent_task(updates['parent_task_id'], user_id)
        
        # Apply updates
        for key, value in updates.items():
            setattr(task, key, value)
        
        # Save changes
        success = self.task_repository.update_task(task_id, task)
        if not success:
            raise RuntimeError("Failed to update task")
        
        # Invalidate parent task progress cache if needed
        if task.parent_task_id:
            self.cache_repo.drop_task_progress_cache(task.parent_task_id)
        
        return task
    
    def _validate_update_task_input(self, updates: dict) -> None:
        """Validate input parameters for task updates."""
        if 'title' in updates and updates['title'] is not None:
            if len(updates['title'].strip()) < 3:
                raise ValueError("Title must be at least 3 characters")
        
        if 'priority' in updates and updates['priority'] is not None:
            if not (1 <= updates['priority'] <= 5):
                raise ValueError("Priority must be between 1 and 5 inclusive")
        
        if 'due_date' in updates and updates['due_date'] is not None:
            if updates['due_date'] < datetime.now():
                raise ValueError("Due date cannot be in the past")
    
    def get_child_tasks(self, parent_task_id: int, user_id: str, offset: int = 0, limit: int = 10) -> list[Task]:
        """Get child tasks with permission check."""
        # Verify user has access to parent task
        if not self.task_repository.user_has_access_to_task(parent_task_id, user_id):
            raise PermissionError("You don't have access to this parent task")
        
        return self.task_repository.get_child_tasks(parent_task_id)[offset:offset + limit]
