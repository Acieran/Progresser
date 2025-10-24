from abc import ABC, abstractmethod
from core.domain.entities import User


class UserRepositoryInterface(ABC):
    """Domain-focused repository for User operations."""
    
    @abstractmethod
    def create_user(self, user: User) -> str:
        """Create a new user and return the username."""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        pass
    
    @abstractmethod
    def get_user_by_telegram_id(self, telegram_id: str) -> User | None:
        """Get a user by telegram ID."""
        pass
    
    @abstractmethod
    def update_user(self, username: str, user: User) -> bool:
        """Update an existing user."""
        pass
    
    @abstractmethod
    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        pass
    
    @abstractmethod
    def get_or_create_user(self, username: str, telegram_username: str = None) -> User:
        """Get existing user or create new one."""
        pass
