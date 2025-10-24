from core.application.ports.repositories_interface.task_repository_interface import TaskRepositoryInterface
from core.domain.entities import Task
from infrastructure.database_access_managers.sqlalchemy.models import Task as BDTask
from infrastructure.database.repositories.base_repository import BaseRepository
from core.application.utilities import dict_to_task


class SqlAlchemyTaskRepository(TaskRepositoryInterface):
    """Concrete implementation using SQLAlchemy and BaseRepository."""
    
    def __init__(self, base_repository: BaseRepository):
        self.base_repo = base_repository
        # Internal mapping - domain entities to infrastructure models
        self._model_mapping = {
            Task: BDTask,
        }
    
    def create_task(self, task: Task) -> int:
        """Create a new task and return its ID."""
        db_model = self._model_mapping[Task]
        
        # Convert domain entity to database fields
        task_data = {
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date,
            'priority': task.priority,
            'is_complete': task.is_complete,
            'weight': task.weight,
            'owner_name': task.owner_name,
            'parent_task_id': task.parent_task_id,
        }
        
        # Remove None values
        task_data = {k: v for k, v in task_data.items() if v is not None}
        
        return self.base_repo.create(db_model, **task_data)
    
    def get_task_by_id(self, task_id: int) -> Task | None:
        """Get a task by its ID."""
        db_model = self._model_mapping[Task]
        result = self.base_repo.get_by_id(db_model, task_id)
        
        if result:
            return dict_to_task(**result)
        return None
    
    def get_tasks_by_owner(self, owner_name: str) -> list[Task]:
        """Get all tasks owned by a specific user."""
        db_model = self._model_mapping[Task]
        results = self.base_repo.get_by_custom_fields(db_model, owner_name=owner_name)
        
        return [dict_to_task(**result) for result in results]
    
    def get_child_tasks(self, parent_task_id: int) -> list[Task]:
        """Get all child tasks of a parent task."""
        db_model = self._model_mapping[Task]
        results = self.base_repo.get_by_custom_fields(db_model, parent_task_id=parent_task_id)
        
        return [dict_to_task(**result) for result in results]
    
    def update_task(self, task_id: int, task: Task) -> bool:
        """Update an existing task."""
        db_model = self._model_mapping[Task]
        
        # Convert domain entity to database fields
        task_data = {
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date,
            'priority': task.priority,
            'is_complete': task.is_complete,
            'weight': task.weight,
            'owner_name': task.owner_name,
            'parent_task_id': task.parent_task_id,
        }
        
        # Remove None values
        task_data = {k: v for k, v in task_data.items() if v is not None}
        
        return self.base_repo.update(db_model, task_id, **task_data)
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID."""
        db_model = self._model_mapping[Task]
        return self.base_repo.delete(db_model, task_id)
    
    def task_exists(self, task_id: int) -> bool:
        """Check if a task exists."""
        return self.get_task_by_id(task_id) is not None
    
    def user_has_access_to_task(self, task_id: int, username: str) -> bool:
        """Check if user has access to a task."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        return task.owner_name == username
