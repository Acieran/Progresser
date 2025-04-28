from sqlalchemy import exc
from sqlalchemy.orm import DeclarativeBase

from database.database_manager import SQLDatabaseManager
from database.repositories.base_repository import BaseRepository
from core.models_sql_alchemy.models import User, UserState, Workspace, Task


class UserRepository(BaseRepository):
    @BaseRepository.transaction_decorator
    def create(self, username: str):
        """Creates a new record in the database."""
        try:
            super().create(User, username=username, telegram_username=username)
            super().create(UserState, telegram_username=username)
        except exc.SQLAlchemyError as e:
            raise e