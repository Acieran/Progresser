from core.application.ports.repositories_interface.user_repository_interface import UserRepositoryInterface
from core.domain.entities import User
from infrastructure.database_access_managers.sqlalchemy.models import User as BDUser
from infrastructure.database.repositories.base_repository import BaseRepository
from core.application.utilities import dict_to_user


class SqlAlchemyUserRepository(UserRepositoryInterface):
    """Concrete implementation using SQLAlchemy and BaseRepository."""
    
    def __init__(self, base_repository: BaseRepository):
        self.base_repo = base_repository
        # Internal mapping - domain entities to infrastructure models
        self._model_mapping = {
            User: BDUser,
        }
    
    def create_user(self, user: User) -> str:
        """Create a new user and return the username."""
        db_model = self._model_mapping[User]
        
        user_data = {
            'username': user.username,
            'active': user.active,
            'telegram_username': user.telegram_username,
        }
        
        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        
        self.base_repo.create(db_model, **user_data)
        return user.username
    
    def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        db_model = self._model_mapping[User]
        result = self.base_repo.get_by_id(db_model, username)
        
        if result:
            return dict_to_user(**result)
        return None
    
    def get_user_by_telegram_id(self, telegram_id: str) -> User | None:
        """Get a user by telegram ID."""
        db_model = self._model_mapping[User]
        results = self.base_repo.get_by_custom_fields(db_model, telegram_username=telegram_id)
        
        if results:
            return dict_to_user(**results[0])
        return None
    
    def update_user(self, username: str, user: User) -> bool:
        """Update an existing user."""
        db_model = self._model_mapping[User]
        
        user_data = {
            'active': user.active,
            'telegram_username': user.telegram_username,
        }
        
        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        
        return self.base_repo.update(db_model, username, **user_data)
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        return self.get_user_by_username(username) is not None
    
    def get_or_create_user(self, username: str, telegram_username: str = None) -> User:
        """Get existing user or create new one."""
        # Try to get existing user
        user = self.get_user_by_username(username)
        if user:
            return user
        
        # Create new user
        new_user = User(
            username=username,
            active=True,
            telegram_username=telegram_username or username
        )
        
        self.create_user(new_user)
        return new_user
